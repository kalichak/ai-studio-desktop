"""Configurações centralizadas da aplicação."""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # UI
    WINDOW_WIDTH = 1366
    WINDOW_HEIGHT = 768
    APP_TITLE = "AI Studio Desktop"
    
    # Modelos Prioritários
    PRIORITY_MODELS = [
        "models/gemini-1.5-flash-latest",
        "models/gemini-1.5-pro-latest",
        "models/gemini-pro-latest",
    ]
    
    # Análise de Projeto
    IGNORE_FOLDERS = ['.git', '__pycache__', 'venv', 'env', 'node_modules', 
                     '.idea', '.vscode', 'dist', 'build', 'bin', 'obj']
    ALLOWED_EXTENSIONS = ['.py', '.js', '.ts', '.html', '.css', '.json', 
                         '.sql', '.md', '.java', '.c', '.cpp', '.txt', 
                         '.cs', '.go', '.rs']
    
    # Segurança Gemini
    SAFETY_SETTINGS = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

settings = Settings()