"""Utilitários para manipulação de arquivos com detecção automática de encoding."""
import chardet

def detect_encoding(file_path):
    """Detecta o encoding do arquivo lendo os primeiros bytes."""
    try:
        with open(file_path, 'rb') as f:
            rawdata = f.read(10000)
        result = chardet.detect(rawdata)
        encoding = result.get('encoding') or 'utf-8'
        print(f"📝 Encoding detectado: {encoding}")
        return encoding
    except Exception as e:
        print(f"⚠️ Erro ao detectar encoding, usando UTF-8: {e}")
        return 'utf-8'
