"""
Script para verificar e criar TODOS os arquivos necessários.
Execute: python fix_structure.py
"""
import os
from pathlib import Path

def check_and_report():
    """Verifica quais arquivos existem e quais faltam."""
    
    print("🔍 Verificando estrutura do projeto...\n")
    
    required_files = {
        "Raiz": [
            "main.py",
            "requirements.txt",
            ".env"
        ],
        "config/": [
            "config/__init__.py",
            "config/settings.py"
        ],
        "core/": [
            "core/__init__.py",
            "core/gemini_client.py"
        ],
        "shared/": [
            "shared/__init__.py",
            "shared/components.py"
        ],
        "utils/": [
            "utils/__init__.py",
            "utils/file_helpers.py"
        ],
        "features/chat/": [
            "features/__init__.py",
            "features/chat/__init__.py",
            "features/chat/service.py",
            "features/chat/view.py"
        ],
        "features/project_analyzer/": [
            "features/project_analyzer/__init__.py",
            "features/project_analyzer/service.py",
            "features/project_analyzer/view.py"
        ],
        "features/log_fixer/": [
            "features/log_fixer/__init__.py",
            "features/log_fixer/service.py",
            "features/log_fixer/view.py"
        ],
        "features/automations/": [
            "features/automations/__init__.py",
            "features/automations/service.py",
            "features/automations/view.py"
        ],
        "features/document_processor/": [
            "features/document_processor/__init__.py",
            "features/document_processor/service.py",
            "features/document_processor/view.py"
        ],
        "features/data_randomizer/": [
            "features/data_randomizer/__init__.py",
            "features/data_randomizer/service.py"
        ]
    }
    
    missing_files = []
    existing_files = []
    
    for category, files in required_files.items():
        print(f"\n {category}")
        for file in files:
            if os.path.exists(file):
                print(f"{file}")
                existing_files.append(file)
            else:
                print(f"{file} - FALTANDO")
                missing_files.append(file)
    
    # Resumo
    print("\n" + "="*60)
    print(f"Resumo:")
    print(f"Existem: {len(existing_files)} arquivos")
    print(f"Faltam: {len(missing_files)} arquivos")
    print("="*60)
    
    return missing_files

def create_missing_init_files(missing_files):
    """Cria arquivos __init__.py faltantes."""
    print("\n🔧 Criando arquivos __init__.py...\n")
    
    init_files = [f for f in missing_files if f.endswith("__init__.py")]
    
    for file in init_files:
        Path(file).parent.mkdir(parents=True, exist_ok=True)
        Path(file).touch()
        print(f"  ✅ Criado: {file}")
    
    return init_files

def show_instructions(missing_files):
    """Mostra instruções para arquivos que precisam de conteúdo."""
    
    code_files = [f for f in missing_files if not f.endswith("__init__.py")]
    
    if not code_files:
        print("\n🎉 Todos os arquivos necessários existem!")
        return
    
    print("\n📝 Arquivos que precisam ser criados manualmente:\n")
    
    file_instructions = {
        "features/project_analyzer/view.py": "Cole o conteúdo do artifact 'features/project_analyzer/view.py (CORRIGIDO - Com cancelamento)'",
        "features/log_fixer/service.py": "Cole o conteúdo do artifact 'features/log_fixer/service.py'",
        "features/log_fixer/view.py": "Cole o conteúdo do artifact 'features/log_fixer/view.py (NOVO - Com cancelamento)'",
        "features/automations/view.py": "Cole o conteúdo do artifact 'features/automations/view.py'",
        "features/document_processor/service.py": "Cole o conteúdo do artifact 'features/document_processor/service.py'",
        "features/document_processor/view.py": "Cole o conteúdo do artifact 'features/document_processor/view.py'",
    }
    
    for file in code_files:
        instruction = file_instructions.get(file, "Veja os artifacts fornecidos")
        print(f"\n {file}")
        print(f"{instruction}")

def main():
    print("="*60)
    print("Fix Structure - Correção Automática")
    print("="*60)
    
    # Verifica estrutura
    missing_files = check_and_report()
    
    if not missing_files:
        print("\nEstrutura completa! Tudo OK.")
        return
    
    # Cria __init__.py
    created = create_missing_init_files(missing_files)
    
    # Atualiza lista de faltantes
    remaining = [f for f in missing_files if f not in created]
    
    # Mostra instruções
    show_instructions(remaining)
    
    print("\n" + "="*60)
    print("Arquivos __init__.py criados automaticamente!")
    print("Copie o conteúdo dos artifacts para os arquivos listados acima")
    print("="*60)
    
    # Comandos úteis
    print("\nComandos úteis:")
    print("  python fix_structure.py    # Executar novamente para verificar")
    print("  python main.py             # Executar aplicação")
    print()

if __name__ == "__main__":
    main()