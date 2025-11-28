# AI Studio Desktop

Uma plataforma desktop para desenvolvedores construída com Python e Flet, integrando ferramentas inteligentes powered by Google Gemini. Desenvolvida seguindo princípios de Clean Architecture para garantir modularidade, escalabilidade e baixo acoplamento.

## Visão Geral

Ambiente completo para acelerar o fluxo de trabalho de desenvolvimento através de IA, oferecendo análise de código, depuração inteligente, chat contextual e processamento de dados em uma única aplicação desktop.

## Funcionalidades

### Chat com IA
Interface de conversação com modelos Gemini, mantendo histórico e contexto entre mensagens.

### Analisador de Projeto
Análise automatizada de arquitetura e organização de código-fonte, identificando padrões e estruturas do projeto.

### Corretor de Logs
Análise inteligente de logs de erro com identificação de causa raiz e sugestões de correção.

### Processador de Documentos
Carregamento e análise de arquivos CSV e Excel com capacidade de fazer queries em linguagem natural sobre os dados.

### Randomizador de Dados
Geração de datasets sintéticos baseados em arquivos modelo para ambientes de teste.

### Central de Automações
Automações para geração de testes unitários, documentação e refatoração de código.

## Instalação

### Requisitos
- Python 3.10 ou superior
- Chave de API do Google Gemini

### Passos

Clonar o repositório:
```bash
git clone https://github.com/seu-usuario/ai-studio-desktop.git
cd ai-studio-desktop
```

Criar e ativar ambiente virtual:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

Instalar dependências:
```bash
pip install -r requirements.txt
```

Configurar API:
Crie o arquivo `.env` na raiz do projeto:
```
GEMINI_API_KEY=sua_chave_aqui
```

Executar aplicação:
```bash
python main.py
```

## Arquitetura

O projeto utiliza Clean Architecture com separação clara de responsabilidades:
```
project/
├── core/                    # Cliente Gemini e serviços centrais
├── features/                # Módulos de funcionalidades
│   ├── chat/
│   ├── project_analyzer/
│   ├── log_debugger/
│   ├── document_processor/
│   ├── data_randomizer/
│   └── automations/
├── shared/                  # Componentes reutilizáveis
├── config/                  # Configurações
├── utils/                   # Utilitários
└── main.py                  # Ponto de entrada
```

Cada feature contém:
- `view.py` - Camada de apresentação (UI Flet)
- `service.py` - Lógica de negócio

### Cliente Gemini

O módulo `core/gemini_client.py` implementa:
- Rate limiting automático
- Sistema de retry para falhas transitórias
- Operações assíncronas com asyncio
- Cancelamento de tarefas
- Suporte a mensagens multimodais

## Configuração

Principais configurações em `config/settings.py`:

- `PRIORITY_MODELS` - Modelos Gemini prioritários na interface
- `IGNORE_FOLDERS` - Diretórios excluídos da análise de projeto
- `ALLOWED_EXTENSIONS` - Tipos de arquivo processados

## Problemas Conhecidos

### Bug Crítico
Em `features/automations/service.py`, a verificação do tipo de automação referencia o dicionário incorreto:
```python
# Atual (incorreto)
if automation_type not in self.automations:

# Correção necessária
if automation_type not in self.ai_automations:
```

### Limitações
- Configurações de pastas e extensões são estáticas, requerendo edição de código
- Scripts externos não persistem entre sessões
- Falhas na inicialização de módulos podem não ser visíveis ao usuário

## Melhorias Futuras

### Sistema de Configurações Persistentes
Implementar arquivo de configuração no diretório do usuário para:
- Extensões permitidas customizáveis
- Pastas ignoradas personalizáveis
- Persistência de scripts externos
- Preferências de interface

### Feedback de Erros
Substituir logs de console por notificações na interface usando Snackbars ou banners do Flet.

### Gerenciador de Tarefas
Criar `TaskManager` centralizado para:
- Registro de tarefas assíncronas
- Cancelamento global de operações
- Monitoramento de execuções

### Funcionalidades Offline
Expandir capacidades que não dependem da API, agregando valor mesmo sem conexão.

## Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Distribuído sob a Licença MIT.
