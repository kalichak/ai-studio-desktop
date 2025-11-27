"""Cliente centralizado para API Gemini com tratamento robusto de erros."""
import asyncio
import google.generativeai as genai
from config.settings import settings

class GeminiClient:
    """Gerencia todas interações com a API Gemini de forma segura."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self._current_task = None  # Para cancelamento
        if self.api_key:
            genai.configure(api_key=self.api_key)
    
    def get_available_models(self):
        """Lista modelos compatíveis com geração de texto."""
        if not self.api_key:
            return [], "Chave API vazia."
        
        try:
            all_models = list(genai.list_models())
            text_models = [
                m for m in all_models 
                if 'generateContent' in m.supported_generation_methods
            ]
            
            options = []
            model_names = [m.name for m in text_models]
            
            # Prioriza modelos recomendados
            for priority in settings.PRIORITY_MODELS:
                if priority in model_names:
                    clean = priority.replace("models/", "")
                    label = f"{clean} (Recomendado)" if "flash" in priority else clean
                    options.append({"key": priority, "text": label})
            
            # Adiciona outros modelos
            for model in text_models:
                if model.name not in settings.PRIORITY_MODELS and "vision" not in model.name:
                    options.append({
                        "key": model.name, 
                        "text": model.name.replace("models/", "")
                    })
            
            return options, "Modelos carregados com sucesso."
        
        except Exception as e:
            return [], f"Erro ao listar modelos: {str(e)}"
    
    async def generate_stream(self, prompt: str, model_name: str, timeout: int = 120):
        """
        Gera resposta em streaming com timeout e tratamento de erros.
        
        Args:
            prompt: Texto do prompt
            model_name: Nome do modelo Gemini
            timeout: Tempo máximo em segundos (padrão: 120s)
        
        Yields:
            str: Chunks de resposta ou mensagens de erro
        """
        if not model_name:
            yield "❌ Nenhum modelo selecionado."
            return
        
        try:
            model = genai.GenerativeModel(
                model_name, 
                safety_settings=settings.SAFETY_SETTINGS
            )
            
            # Cria task com timeout
            self._current_task = asyncio.create_task(
                self._generate_with_timeout(model, prompt, timeout)
            )
            
            async for chunk in self._current_task:
                yield chunk
        
        except asyncio.CancelledError:
            yield "\n\n⚠️ Operação cancelada pelo usuário."
            return
        
        except asyncio.TimeoutError:
            yield f"\n\n⏱️ Timeout: A requisição demorou mais de {timeout}s. Tente novamente ou use um modelo mais rápido."
            return
        
        except Exception as e:
            error_msg = str(e).lower()
            
            if "429" in error_msg or "quota" in error_msg or "rate" in error_msg:
                yield "\n\n⚠️ **Limite de requisições excedido (429)**\n\n"
                yield "**Soluções:**\n"
                yield "1. Aguarde 1 minuto e tente novamente\n"
                yield "2. Troque para o modelo `gemini-1.5-flash` (maior limite gratuito)\n"
                yield "3. Verifique sua cota em: https://aistudio.google.com/app/apikey\n"
            
            elif "401" in error_msg or "api key" in error_msg or "unauthorized" in error_msg:
                yield "\n\n❌ **Erro de Autenticação (401)**\n\n"
                yield "Sua chave API está inválida ou expirada.\n"
                yield "Gere uma nova em: https://aistudio.google.com/app/apikey\n"
            
            elif "403" in error_msg or "permission" in error_msg:
                yield "\n\n❌ **Acesso Negado (403)**\n\n"
                yield "Você não tem permissão para usar este modelo.\n"
                yield "Tente outro modelo da lista.\n"
            
            elif "404" in error_msg or "not found" in error_msg:
                yield f"\n\n❌ **Modelo não encontrado (404)**\n\n"
                yield f"O modelo `{model_name}` não existe ou foi removido.\n"
                yield "Recarregue a lista de modelos (botão ↻).\n"
            
            elif "blocked" in error_msg or "safety" in error_msg:
                yield "\n\n🛡️ **Conteúdo Bloqueado por Segurança**\n\n"
                yield "O Gemini bloqueou sua requisição por questões de segurança.\n"
                yield "Tente reformular sua pergunta de forma mais neutra.\n"
            
            else:
                yield f"\n\n❌ **Erro inesperado:** {str(e)}\n\n"
                yield "Tente novamente ou escolha outro modelo.\n"
    
    async def _generate_with_timeout(self, model, prompt: str, timeout: int):
        """Gera conteúdo com timeout."""
        try:
            # Executa geração com timeout
            response = await asyncio.wait_for(
                self._async_generate(model, prompt),
                timeout=timeout
            )
            
            async for chunk in response:
                yield chunk
        
        except asyncio.TimeoutError:
            raise  # Propaga timeout
        
        except Exception as e:
            raise  # Propaga outros erros
    
    async def _async_generate(self, model, prompt: str):
        """Wrapper assíncrono para generate_content (que é síncrono)."""
        try:
            # Executa em thread separada para não bloquear
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: model.generate_content(prompt, stream=True)
            )
            
            # Processa chunks
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                
                # Permite cancelamento entre chunks
                await asyncio.sleep(0)
        
        except Exception as e:
            raise  # Propaga erro para tratamento acima
    
    def cancel_current_operation(self):
        """Cancela operação em andamento."""
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            return True
        return False