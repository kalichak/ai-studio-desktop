# 🤖 AI Studio Desktop

> Assistente de código inteligente com Google Gemini + Flet

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org/)
[![Flet](https://img.shields.io/badge/Flet-0.25+-purple.svg)](https://flet.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://claude.ai/chat/LICENSE)

---

## ✨ Funcionalidades

### ✅ Implementadas

* 💬 **Chat com IA** - Conversação contextual com múltiplos modelos Gemini
* 📂 **Análise de Projeto** - Avaliação automática de arquitetura e código
* 🐛 **Correção de Logs** - Debug inteligente com sugestões de solução

### 🔜 Preparadas (Templates prontos)

* 🤖 **Central de Automações** - Geração de testes, docs, refatoração
* 🎲 **Randomizador de Dados** - Geração de dados fake para testes

---

## 🚀 Instalação Rápida

```bash
# 1. Clone ou baixe o projeto
git clone <seu-repo>
cd ai-studio-desktop

# 2. Crie a estrutura (automático)
python setup_project.py

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure sua chave API
# Edite o arquivo .env e adicione:
# GEMINI_API_KEY=sua_chave_aqui

# 5. Execute!
python main.py
```

---

## 📁 Estrutura do Projeto

```
ai-studio-desktop/
├── main.py                    # 🎯 Aplicação principal
├── config/settings.py         # ⚙️ Configurações
├── core/gemini_client.py      # 🧠 Cliente API
├── features/                  # 🎨 Módulos de funcionalidades
│   ├── chat/
│   ├── project_analyzer/
│   ├── log_fixer/
│   ├── automations/          # 🔜
│   └── data_randomizer/      # 🔜
├── shared/components.py       # 🧩 Componentes reutilizáveis
└── utils/file_helpers.py      # 🛠️ Utilitários
```

---

## 🎯 Como Adicionar Nova Feature

```python
# 1. Crie a pasta
mkdir features/minha_feature
touch features/minha_feature/{__init__,service,view}.py

# 2. Implemente service.py (lógica)
class MinhaFeatureService:
    def __init__(self, gemini_client):
        self.client = gemini_client
  
    async def fazer_algo(self, dados, model):
        prompt = f"Faça algo com {dados}"
        async for chunk in self.client.generate_stream(prompt, model):
            yield chunk

# 3. Implemente view.py (UI)
class MinhaFeatureView:
    def __init__(self, page, service, get_model_fn):
        # Seus componentes Flet aqui
        pass

# 4. Adicione ao main.py
from features.minha_feature.service import MinhaFeatureService
from features.minha_feature.view import MinhaFeatureView
```

✅ **Pronto!** Feature adicionada sem modificar código existente.

---

## 🏗️ Arquitetura

### Princípios Aplicados

* ✅ **Clean Architecture** - Separação clara de responsabilidades
* ✅ **Low Code** - Adicione features com 2 arquivos apenas
* ✅ **DRY** - Componentes reutilizáveis em `shared/`
* ✅ **Single Responsibility** - Cada módulo tem um propósito único

### Camadas

```
┌─────────────────────────────────┐
│  UI Layer (features/*/view.py)  │  ← Interface Flet
├─────────────────────────────────┤
│ Service Layer (features/*/      │  ← Lógica de negócio
│              service.py)         │
├─────────────────────────────────┤
│  Core (gemini_client.py)        │  ← API Gemini
└─────────────────────────────────┘
```

---

## 📊 Exemplo: Randomizador de Dados

```python
from features.data_randomizer.service import DataRandomizerService

randomizer = DataRandomizerService()

# Gerar CPF válido
cpf = randomizer.randomize_value("cpf")
# Output: "123.456.789-01"

# Gerar dataset completo
schema = {
    "nome": "name",
    "email": "email",
    "telefone": "phone",
    "cpf": "cpf"
}

dados = randomizer.randomize_dataset(schema, count=100)
# Output: [
#   {"nome": "João Silva", "email": "abc@gmail.com", ...},
#   ...
# ]
```

**Tipos suportados:** `string`, `email`, `phone`, `cpf`, `cnpj`, `date`, `datetime`, `int`, `float`, `bool`, `uuid`, `url`, `name`, `address`, `company`

---

## 🤖 Exemplo: Automações

```python
from features.automations.service import AutomationsService

automator = AutomationsService(gemini_client)

# Gerar testes unitários
async for chunk in automator.run_automation("generate_tests", code, model):
    print(chunk, end="")

# Criar documentação
async for chunk in automator.run_automation("create_docs", code, model):
    print(chunk, end="")
```

**Automações disponíveis:**

* `generate_tests` - Testes unitários (pytest/unittest)
* `create_docs` - Documentação técnica completa
* `refactor_code` - Refatoração com boas práticas
* `security_scan` - Análise de vulnerabilidades

---

## ⚙️ Configuração Avançada

### Customizar modelos prioritários

```python
# config/settings.py
PRIORITY_MODELS = [
    "models/seu-modelo-customizado",
    "models/gemini-1.5-flash-latest",
]
```

### Adicionar extensões de arquivo

```python
# config/settings.py
ALLOWED_EXTENSIONS = [
    '.py', '.js', '.ts', '.java',
    '.kt', '.swift'  # 👈 Adicione novos
]
```

---

## 🐛 Troubleshooting

| Problema                 | Solução                                               |
| ------------------------ | ------------------------------------------------------- |
| Erro 429 (Rate Limit)    | Troque para `gemini-1.5-flash`(maior limite gratuito) |
| Modelos não aparecem    | Verifique chave API e clique em ↻ Recarregar           |
| Arquivos não são lidos | Confirme extensões suportadas (`.py`,`.js`, etc)   |

---

## 📚 Recursos

* 📖 [Documentação Flet](https://flet.dev/docs)
* 🤖 [Google Gemini API](https://ai.google.dev/docs)
* 🔑 [Obter API Key](https://makersuite.google.com/app/apikey)

---

## 📄 Licença

MIT © 2024 - Use livremente!

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

**Desenvolvido com ❤️ usando Flet + Google Gemini**
