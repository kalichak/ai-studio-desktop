"""Cliente centralizado para API Gemini com rate limiting, retries e monitoramento de uso."""
import asyncio
import time
import random
from collections import deque
from google import genai
from config.settings import settings

# --- TABELA DE LIMITES ---
MODEL_LIMITS = {
    "gemini-2.0-flash":      {"rpm": 15, "tpm": 1_000_000, "rpd": 1500},
    "gemini-2.0-flash-lite": {"rpm": 30, "tpm": 1_000_000, "rpd": 1500},
    "gemini-2.5-pro":        {"rpm": 2,  "tpm": 32_000,    "rpd": 50},
    "default":               {"rpm": 15, "tpm": 1_000_000, "rpd": 1500} # Fallback
}

class UsageTracker:
    def __init__(self):
        self.total_requests = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_errors = 0
        self.start_time = time.time()
        
        # Filas para janela deslizante (último minuto)
        self.requests_last_minute = deque()
        self.tokens_last_minute = deque() # (timestamp, count)

    def log_request(self):
        self.total_requests += 1
        now = time.time()
        self.requests_last_minute.append(now)
        self._clean_old_records(now)

    def log_tokens(self, input_tokens, output_tokens):
        total = input_tokens + output_tokens
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        
        # Registra tokens para cálculo de TPM
        now = time.time()
        self.tokens_last_minute.append((now, total))

    def log_error(self):
        self.total_errors += 1

    def _clean_old_records(self, now):
        """Limpa registros com mais de 60s."""
        # Limpa requisições
        while self.requests_last_minute and now - self.requests_last_minute[0] > 60:
            self.requests_last_minute.popleft()
        
        # Limpa tokens
        while self.tokens_last_minute and now - self.tokens_last_minute[0][0] > 60:
            self.tokens_last_minute.popleft()

    def get_detailed_stats(self, current_model_name: str):
        """Retorna estatísticas comparadas com o limite do modelo atual."""
        now = time.time()
        self._clean_old_records(now)
        
        # Identifica limites do modelo
        limits = MODEL_LIMITS.get("default")
        for key in MODEL_LIMITS:
            if key in str(current_model_name).lower():
                limits = MODEL_LIMITS[key]
                break
        
        # Cálculos Atuais
        current_rpm = len(self.requests_last_minute)
        current_tpm = sum(t[1] for t in self.tokens_last_minute)
        
        return {
            "model": current_model_name,
            "rpm_current": current_rpm,
            "rpm_limit": limits["rpm"],
            "tpm_current": current_tpm,
            "tpm_limit": limits["tpm"],
            "rpd_current": self.total_requests, # Nota: Isso reseta ao fechar o app
            "rpd_limit": limits["rpd"],
            "errors": self.total_errors,
            "rpm_percent": min(current_rpm / limits["rpm"], 1.0),
            "tpm_percent": min(current_tpm / limits["tpm"], 1.0)
        }

_USAGE_TRACKER = UsageTracker()

# --- RATE LIMITER ---
class RateLimiter:
    def __init__(self, max_requests: int = 15, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        async with self._lock:
            now = time.time()
            while self.requests and now - self.requests[0] > self.time_window:
                self.requests.popleft()
            
            if len(self.requests) >= self.max_requests:
                wait_time = self.time_window - (now - self.requests[0]) + 1
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    now = time.time()
                    while self.requests and now - self.requests[0] > self.time_window:
                        self.requests.popleft()
            self.requests.append(time.time())

_SHARED_RATE_LIMITER = RateLimiter(max_requests=15, time_window=60)

# --- CLIENTE GEMINI ---
class GeminiClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or getattr(settings, "GEMINI_API_KEY", None)
        self._current_task = None
        self.rate_limiter = _SHARED_RATE_LIMITER
        self.tracker = _USAGE_TRACKER
        self.current_model_name = "gemini-2.0-flash" # Padrão
        self.client = None

        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
    
    def get_usage_stats(self):
        """Retorna estatísticas detalhadas baseadas no modelo atual."""
        return self.tracker.get_detailed_stats(self.current_model_name)

    def set_current_model(self, model_name):
        """Atualiza qual modelo está sendo usado para ajustar os limites."""
        self.current_model_name = model_name

    def get_available_models(self):
        if not self.api_key or not self.client:
            return [], "Chave API vazia."
        try:
            # Lista de modelos conhecidos que funcionam com a API
            known_models = [
                "models/gemini-2.0-flash",
                "models/gemini-2.0-flash-lite",
                "models/gemini-1.5-pro",
                "models/gemini-1.5-flash",
            ]
            # Tenta listar modelos da API, mas com fallback para lista conhecida
            try:
                all_models = list(self.client.models.list())
                options = [{"key": m.name, "text": m.name.replace("models/", "")} for m in all_models]
            except:
                options = [{"key": m, "text": m.replace("models/", "")} for m in known_models]

            return (options, f"{len(options)} modelos.") if options else ([], "Nenhum modelo.")
        except Exception as e:
            return [], f"Erro: {str(e)}"
    
    async def generate_stream(self, prompt: str, model_name: str, timeout: int = 120):
        if not model_name:
            yield "❌ Nenhum modelo selecionado."
            return

        if not self.client:
            yield "❌ Cliente não inicializado. Configure uma chave API."
            return

        # Atualiza o modelo atual para o tracker saber os limites
        self.current_model_name = model_name

        if not model_name.startswith("models/"):
            model_name = f"models/{model_name}"

        try:
            self._current_task = asyncio.current_task()
        except RuntimeError: pass

        max_retries = 3
        current_try = 0

        while current_try <= max_retries:
            try:
                await self.rate_limiter.acquire()
                self.tracker.log_request()

                # Tenta usar generate_content com stream
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    stream=True,
                    config=getattr(settings, "SAFETY_SETTINGS", {})
                )

                # Se a resposta não for um iterator assíncrono, converte
                if hasattr(response, '__aiter__'):
                    async for chunk in response:
                        if hasattr(chunk, 'text') and chunk.text:
                            yield chunk.text
                        if hasattr(chunk, 'usage_metadata') and chunk.usage_metadata:
                            try:
                                self.tracker.log_tokens(
                                    chunk.usage_metadata.prompt_token_count,
                                    chunk.usage_metadata.candidates_token_count
                                )
                            except: pass
                elif hasattr(response, '__iter__'):
                    for chunk in response:
                        # Executa em thread para não bloquear
                        await asyncio.sleep(0)
                        if hasattr(chunk, 'text') and chunk.text:
                            yield chunk.text
                        if hasattr(chunk, 'usage_metadata') and chunk.usage_metadata:
                            try:
                                self.tracker.log_tokens(
                                    chunk.usage_metadata.prompt_token_count,
                                    chunk.usage_metadata.candidates_token_count
                                )
                            except: pass
                else:
                    # Resposta normal (não streaming)
                    if hasattr(response, 'text'):
                        yield response.text
                    if hasattr(response, 'usage_metadata') and response.usage_metadata:
                        try:
                            self.tracker.log_tokens(
                                response.usage_metadata.prompt_token_count,
                                response.usage_metadata.candidates_token_count
                            )
                        except: pass

                return

            except asyncio.CancelledError:
                yield "Cancelado."
                return
            except Exception as e:
                self.tracker.log_error()
                error_msg = str(e).lower()
                if "429" in error_msg or "resource" in error_msg:
                    current_try += 1
                    if current_try <= max_retries:
                        await asyncio.sleep(2 ** current_try)
                        yield f"\n⏳ Retry {current_try}...\n"
                        continue
                yield f"Erro: {str(e)}"
                return

    def cancel_current_operation(self):
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            return True
        return False