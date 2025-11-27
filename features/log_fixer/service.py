"""Serviço de análise e correção de logs de erro."""
from core.gemini_client import GeminiClient

class LogFixerService:
    """Analisa logs de erro e sugere correções."""
    
    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client
    
    async def analyze_and_fix(self, log_text: str, model_name: str):
        """
        Analisa log de erro e retorna solução em streaming.
        
        Args:
            log_text: Texto do log de erro
            model_name: Modelo Gemini a usar
        
        Yields:
            str: Análise e solução em chunks
        """
        prompt = self._build_prompt(log_text)
        
        async for chunk in self.client.generate_stream(prompt, model_name):
            yield chunk
    
    def _build_prompt(self, log_text: str) -> str:
        """Constrói prompt otimizado para análise de erros."""
        return f"""Você é um desenvolvedor experiente especializado em debug.

Analise este log de erro e forneça:

1. **Causa Raiz** - O que causou este erro?
2. **Linha/Arquivo Problemático** - Onde está o problema?
3. **Código Corrigido** - Forneça o código corrigido (se aplicável)
4. **Solução Passo a Passo** - Como resolver definitivamente
5. **Prevenção** - Como evitar este erro no futuro

Log de erro:
```
{log_text}
```

Seja direto e objetivo. Se houver código, forneça-o completo e corrigido.
"""