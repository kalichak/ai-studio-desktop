"""Serviço de automações e orquestração de scripts."""
import subprocess
import os
import asyncio
from typing import Dict, List, Callable
from core.gemini_client import GeminiClient

class AutomationsService:
    """
    Central de automações: IA + Scripts externos.
    """
    
    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client
        
        # Automações com IA
        self.ai_automations = {
            "generate_tests": {
                "name": "Gerar Testes Unitários",
                "icon": "🧪",
                "description": "Cria testes automatizados para seu código",
                "handler": self._generate_tests
            },
            "create_docs": {
                "name": "Criar Documentação",
                "icon": "📚",
                "description": "Gera documentação técnica completa",
                "handler": self._create_documentation
            },
            "refactor_code": {
                "name": "Refatorar Código",
                "icon": "♻️",
                "description": "Aplica boas práticas e clean code",
                "handler": self._refactor_code
            },
            "security_scan": {
                "name": "Análise de Segurança",
                "icon": "🔒",
                "description": "Identifica vulnerabilidades no código",
                "handler": self._security_scan
            },
        }
        
        # Scripts/Apps externos registrados
        self.external_scripts = []
    
    def get_all_automations(self) -> List[Dict]:
        """Retorna lista de todas automações disponíveis."""
        automations = []
        
        # Adiciona automações com IA
        for key, info in self.ai_automations.items():
            automations.append({
                "id": key,
                "type": "ai",
                "name": info["name"],
                "icon": info["icon"],
                "description": info["description"]
            })
        
        # Adiciona scripts externos
        for script in self.external_scripts:
            automations.append({
                "id": script["id"],
                "type": "script",
                "name": script["name"],
                "icon": "⚙️",
                "description": script["description"],
                "path": script["path"]
            })
        
        return automations
    
    def register_external_script(self, name: str, path: str, description: str = ""):
        """
        Registra script/app externo.
        
        Args:
            name: Nome do script
            path: Caminho completo do executável/script
            description: Descrição do que faz
        """
        script_id = f"ext_{len(self.external_scripts)}"
        self.external_scripts.append({
            "id": script_id,
            "name": name,
            "path": path,
            "description": description or f"Executa {name}"
        })
    
    def remove_script(self, script_id: str):
        """Remove script registrado."""
        self.external_scripts = [s for s in self.external_scripts if s["id"] != script_id]
    
    async def run_automation(self, automation_type: str, code: str, model_name: str):
        """
        Executa automação selecionada.
        
        Args:
            automation_type: Tipo de automação (ex: "generate_tests")
            code: Código fonte para processar
            model_name: Modelo Gemini a usar
        
        Yields:
            str: Resultado em streaming
        """
        if automation_type not in self.automations:
            yield f"❌ Automação '{automation_type}' não encontrada."
            return
        
        automation_fn = self.automations[automation_type]
        async for chunk in automation_fn(code, model_name):
            yield chunk
    
    async def _generate_tests(self, code: str, model_name: str):
        """Gera testes unitários para o código."""
        prompt = f"""Gere testes unitários completos para este código.
Use pytest ou unittest conforme apropriado.

Código:
{code}

Forneça:
1. Arquivo de teste completo
2. Casos de teste para cenários normais e edge cases
3. Mocks necessários (se aplicável)
"""
        async for chunk in self.client.generate_stream(prompt, model_name):
            yield chunk
    
    async def _create_documentation(self, code: str, model_name: str):
        """Gera documentação detalhada."""
        prompt = f"""Crie documentação técnica completa para este código.

Código:
{code}

Inclua:
1. Visão geral e objetivo
2. Documentação de funções/classes (docstrings)
3. Exemplos de uso
4. Requisitos e dependências
"""
        async for chunk in self.client.generate_stream(prompt, model_name):
            yield chunk
    
    async def _refactor_code(self, code: str, model_name: str):
        """Refatora código seguindo boas práticas."""
        prompt = f"""Refatore este código seguindo princípios SOLID e clean code.

Código:
{code}

Forneça:
1. Código refatorado completo
2. Explicação das mudanças
3. Melhorias de performance/legibilidade aplicadas
"""
        async for chunk in self.client.generate_stream(prompt, model_name):
            yield chunk
    
    async def _security_scan(self, code: str, model_name: str):
        """Analisa vulnerabilidades de segurança."""
        prompt = f"""Analise este código em busca de vulnerabilidades de segurança.

Código:
{code}

Identifique:
1. Vulnerabilidades (SQL injection, XSS, etc)
2. Exposição de dados sensíveis
3. Problemas de autenticação/autorização
4. Código corrigido para cada vulnerabilidade
"""
        async for chunk in self.client.generate_stream(prompt, model_name):
            yield chunk