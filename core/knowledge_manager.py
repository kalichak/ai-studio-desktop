"""Sistema de gerenciamento de conhecimentos e configuração de prompts."""
import json
import os
from datetime import datetime
from typing import Dict, List

class KnowledgeManager:
    """Gerencia conhecimentos anexados ao sistema."""

    def __init__(self, data_dir: str = ".claude"):
        self.data_dir = data_dir
        self.knowledge_file = os.path.join(data_dir, "knowledge.json")
        self.prompts_file = os.path.join(data_dir, "prompts.json")

        # Cria diretório se não existir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        self.knowledge = self._load_json(self.knowledge_file, {})
        self.prompts = self._load_json(self.prompts_file, self._default_prompts())

    def _load_json(self, filepath: str, default: dict) -> dict:
        """Carrega arquivo JSON ou retorna padrão."""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Erro ao carregar {filepath}: {e}")
        return default

    def _save_json(self, filepath: str, data: dict):
        """Salva dados em JSON."""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Salvo: {filepath}")
        except Exception as e:
            print(f"❌ Erro ao salvar {filepath}: {e}")

    def _default_prompts(self) -> dict:
        """Retorna prompts padrão para cada função."""
        return {
            "project_analyzer": {
                "name": "Analisador de Projeto",
                "prompt": "Analise este projeto e forneça um resumo detalhado de:\n1. Arquitetura\n2. Principais componentes\n3. Padrões de design\n4. Possíveis melhorias\n\nProjeto:\n{content}"
            },
            "chat": {
                "name": "Chat IA",
                "prompt": "Você é um assistente útil. {knowledge}\n\nResponda apropriadamente à pergunta do usuário."
            },
            "log_fixer": {
                "name": "Corretor de Logs",
                "prompt": "Analise este log de erro e forneça:\n1. O problema\n2. Causa raiz provável\n3. Soluções recomendadas\n\nLog:\n{content}"
            },
            "automations": {
                "name": "Automações",
                "prompt": "Execute a seguinte automação:\n{content}\n\nResultado esperado: {expected}"
            },
            "data_randomizer": {
                "name": "Randomizador de Dados",
                "prompt": "Processe estes dados:\n{content}\n\nOperação: {operation}"
            }
        }

    def add_knowledge(self, title: str, content: str, category: str = "geral") -> bool:
        """Adiciona novo conhecimento."""
        try:
            if category not in self.knowledge:
                self.knowledge[category] = []

            self.knowledge[category].append({
                "title": title,
                "content": content,
                "added_at": datetime.now().isoformat(),
                "enabled": True
            })

            self._save_json(self.knowledge_file, self.knowledge)
            return True
        except Exception as e:
            print(f"❌ Erro ao adicionar conhecimento: {e}")
            return False

    def remove_knowledge(self, category: str, index: int) -> bool:
        """Remove conhecimento."""
        try:
            if category in self.knowledge and 0 <= index < len(self.knowledge[category]):
                del self.knowledge[category][index]
                self._save_json(self.knowledge_file, self.knowledge)
                return True
        except Exception as e:
            print(f"❌ Erro ao remover conhecimento: {e}")
        return False

    def get_active_knowledge(self, category: str = None) -> str:
        """Retorna conhecimentos ativos em formato de contexto."""
        knowledge_text = ""

        if category and category in self.knowledge:
            items = self.knowledge[category]
        else:
            items = []
            for cat_items in self.knowledge.values():
                items.extend(cat_items)

        active = [k for k in items if k.get("enabled", True)]

        if active:
            knowledge_text = "Contexto adicional:\n"
            for k in active:
                knowledge_text += f"- {k['title']}: {k['content'][:100]}...\n"

        return knowledge_text

    def set_prompt(self, feature: str, prompt: str) -> bool:
        """Define prompt customizado para uma feature."""
        try:
            if feature in self.prompts:
                self.prompts[feature]['prompt'] = prompt
                self._save_json(self.prompts_file, self.prompts)
                return True
        except Exception as e:
            print(f"❌ Erro ao salvar prompt: {e}")
        return False

    def get_prompt(self, feature: str) -> str:
        """Obtém prompt de uma feature."""
        if feature in self.prompts:
            return self.prompts[feature].get('prompt', '')
        return ""

    def list_knowledge(self, category: str = None) -> Dict[str, List]:
        """Lista todos os conhecimentos."""
        if category:
            return {category: self.knowledge.get(category, [])}
        return self.knowledge

    def reset(self):
        """Reseta todos os conhecimentos e prompts customizados."""
        try:
            self.knowledge = {}
            self.prompts = self._default_prompts()
            self._save_json(self.knowledge_file, self.knowledge)
            self._save_json(self.prompts_file, self.prompts)
            print("✅ Sistema resetado com sucesso")
            return True
        except Exception as e:
            print(f"❌ Erro ao resetar: {e}")
            return False
