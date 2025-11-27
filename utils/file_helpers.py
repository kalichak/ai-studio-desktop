"""Utilitários para manipulação de arquivos."""
import os
from config.settings import settings

def read_project_files(directory: str) -> tuple[str, int]:
    """
    Lê arquivos de código de um diretório.
    
    Returns:
        tuple: (conteúdo_concatenado, quantidade_de_arquivos)
    """
    content = ""
    count = 0
    
    for root, dirs, files in os.walk(directory):
        # Remove pastas ignoradas
        dirs[:] = [d for d in dirs if d not in settings.IGNORE_FOLDERS]
        
        for file in files:
            if any(file.endswith(ext) for ext in settings.ALLOWED_EXTENSIONS):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content += f"\n--- {path} ---\n{f.read()}\n"
                        count += 1
                except Exception:
                    pass  # Ignora arquivos com erro de leitura
    
    return content, count