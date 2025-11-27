"""Lógica de negócio do Chat."""
from core.gemini_client import GeminiClient

class ChatService:
    """Gerencia lógica de conversação."""
    
    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client
        self.history = []
    
    def add_to_history(self, role: str, text: str):
        """Adiciona mensagem ao histórico."""
        self.history.append({"role": role, "text": text})
    
    def build_prompt(self, user_message: str) -> str:
        """Constrói prompt com contexto do histórico."""
        history_context = "\n".join([
            f"{msg['role']}: {msg['text']}" 
            for msg in self.history[-4:]  # Últimas 4 mensagens
        ])
        return f"{history_context}\nUsuário: {user_message}"
    
    async def send_message(self, message: str, model_name: str):
        """Envia mensagem e retorna resposta em streaming."""
        prompt = self.build_prompt(message)
        
        full_response = ""
        async for chunk in self.client.generate_stream(prompt, model_name):
            full_response += chunk
            yield chunk
        
        # Salva no histórico após completar
        self.add_to_history("user", message)
        self.add_to_history("assistant", full_response)
    
    def clear_history(self):
        """Limpa histórico de conversação."""
        self.history.clear()