"""File picker nativo do Windows usando tkinter."""
import tkinter as tk
from tkinter import filedialog
import os

def select_file(title: str = "Selecionar Arquivo", filetypes=None) -> str:
    """
    Abre dialog nativo para selecionar arquivo.

    Args:
        title: Título do dialog
        filetypes: Lista de tuplas (descrição, extensão). Ex: (("CSV files", "*.csv"), ("All files", "*.*"))

    Returns:
        Caminho do arquivo selecionado ou string vazia
    """
    try:
        # Cria janela invisível
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        if filetypes is None:
            filetypes = [("All files", "*.*")]

        # Abre dialog de seleção de arquivo
        file_path = filedialog.askopenfilename(
            title=title,
            filetypes=filetypes
        )

        root.destroy()
        return file_path if file_path else ""

    except Exception as e:
        print(f"❌ Erro ao abrir file picker: {e}")
        return ""

def select_folder(title: str = "Selecionar Pasta") -> str:
    """
    Abre dialog nativo para selecionar pasta.

    Args:
        title: Título do dialog

    Returns:
        Caminho da pasta selecionada ou string vazia
    """
    try:
        # Cria janela invisível
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        # Abre dialog de seleção de pasta
        folder_path = filedialog.askdirectory(title=title)

        root.destroy()
        return folder_path if folder_path else ""

    except Exception as e:
        print(f"❌ Erro ao abrir folder picker: {e}")
        return ""

def select_multiple_files(title: str = "Selecionar Arquivos", filetypes=None) -> list:
    """
    Abre dialog nativo para selecionar múltiplos arquivos.

    Args:
        title: Título do dialog
        filetypes: Lista de tuplas (descrição, extensão)

    Returns:
        Lista de caminhos selecionados
    """
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        if filetypes is None:
            filetypes = [("All files", "*.*")]

        files = filedialog.askopenfilenames(
            title=title,
            filetypes=filetypes
        )

        root.destroy()
        return list(files) if files else []

    except Exception as e:
        print(f"❌ Erro ao abrir file picker: {e}")
        return []
