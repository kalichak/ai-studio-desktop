"""Serviço de análise de projetos."""
from core.gemini_client import GeminiClient
from utils.file_helpers import read_project_files

class ProjectAnalyzerService:
    """Analisa estrutura de projetos de código."""
    
    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client
    
    async def analyze(self, directory: str, model_name: str):
        """
        Analisa projeto e retorna insights em streaming.
        
        Yields:
            dict: {"status": str, "text": str, "file_count": int}
        """
        # Lê arquivos
        yield {"status": "reading", "text": "Lendo arquivos...", "file_count": 0}
        
        content, file_count = read_project_files(directory)
        
        if file_count == 0:
            yield {
                "status": "error", 
                "text": "Nenhum arquivo de código encontrado.", 
                "file_count": 0
            }
            return
        
        yield {
            "status": "analyzing", 
            "text": f"Analisando {file_count} arquivos...", 
            "file_count": file_count
        }
        
        # Cria prompt
        prompt = self._build_analysis_prompt(file_count, content)
        
        # Gera análise
        full_response = ""
        async for chunk in self.client.generate_stream(prompt, model_name):
            full_response += chunk
            yield {"status": "streaming", "text": chunk, "file_count": file_count}
        
        yield {"status": "complete", "text": "", "file_count": file_count}
    
    def _build_analysis_prompt(self, file_count: int, content: str) -> str:
        """Constrói prompt de análise."""
        return f"""Você é um Arquiteto de Software experiente. Analise este projeto com {file_count} arquivos.

Forneça:
1. **Objetivo do Projeto** (2-3 linhas)
2. **3 Pontos Fortes** da arquitetura/código
3. **3 Riscos ou Bugs Potenciais** a corrigir
4. **Recomendações** de melhoria

Código do projeto:
{content}
"""