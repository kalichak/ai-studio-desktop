import pandas as pd
import random
import string
from datetime import datetime, timedelta
from .column_detector import detectar_tipos
from .anonymizer_core import anonimizar
from utils.file_utils import detect_encoding

class DataRandomizerService:
    """Randomizador de dados com detecção inteligente de tipos e anonimização."""

    def load_document(self, file_path: str):
        """Carrega o documento e detecta formato automaticamente."""
        try:
            if file_path.endswith(".csv"):
                # Detecta encoding automaticamente
                encoding = detect_encoding(file_path)
                df = pd.read_csv(file_path, encoding=encoding)
            elif file_path.endswith(".xlsx"):
                df = pd.read_excel(file_path)
            elif file_path.endswith(".xls"):
                df = pd.read_excel(file_path)
            elif file_path.endswith(".txt"):
                encoding = detect_encoding(file_path)
                df = pd.read_csv(file_path, sep="\t", encoding=encoding)
            else:
                raise ValueError("Formato não suportado: Use CSV, XLSX, XLS ou TXT")

            print(f"✅ Arquivo carregado: {len(df)} linhas, {len(df.columns)} colunas")
            return df
        except UnicodeDecodeError as e:
            print(f"❌ Erro de codificação: {e}")
            # Tenta com encoding alternativo
            try:
                encoding = detect_encoding(file_path)
                if file_path.endswith(".csv"):
                    df = pd.read_csv(file_path, encoding=encoding, errors='replace')
                elif file_path.endswith(".txt"):
                    df = pd.read_csv(file_path, sep="\t", encoding=encoding, errors='replace')
                else:
                    raise ValueError("Formato não suportado")
                print(f"✅ Arquivo carregado com encoding {encoding}")
                return df
            except Exception as ex:
                print(f"❌ Erro ao carregar arquivo: {ex}")
                raise

    def detect_column_type_simple(self, series):
        """Detecção simples de tipo (fallback)."""
        sample = str(series.iloc[0])

        if sample.isdigit():
            return "numero"
        if "@" in sample:
            return "email"
        if any(x.isdigit() for x in sample) and any(x.isalpha() for x in sample):
            return "mixed"
        if "-" in sample and len(sample) >= 8:
            return "data"

        return "texto"

    def detect_column_types(self, df: pd.DataFrame):
        """
        Detecta tipos de coluna usando análise de padrão.
        Retorna dict {coluna: tipo}
        """
        tipos = {}

        for col_name in df.columns:
            # Pega os primeiros 100 valores não-nulos
            valores = df[col_name].dropna().astype(str).head(100).tolist()

            if not valores:
                tipos[col_name] = "texto"
                continue

            # Simula uma linha com separador para usar o detector
            # Cria uma "linha" juntando os valores
            linha_simulada = "|DUMMY|".join(valores)

            # Usa o detector do DATA FAKE SUITE
            tipos_detectados = detectar_tipos([linha_simulada], sep="|DUMMY|")

            # Pega o tipo da primeira coluna (índice 0)
            if 0 in tipos_detectados:
                tipos[col_name] = tipos_detectados[0]
            else:
                tipos[col_name] = self.detect_column_type_simple(df[col_name])

        return tipos

    def anonymize_dataframe(self, df: pd.DataFrame):
        """Anonimiza todos os valores usando estrutura preservada."""
        anonymized = df.copy()

        # Detecta tipos de coluna
        tipos = self.detect_column_types(df)

        for col in df.columns:
            col_type = tipos.get(col, "texto")
            anonymized[col] = df[col].astype(str).apply(
                lambda x: anonimizar(x, col_type) if pd.notna(x) else x
            )

        return anonymized

    def randomize_value(self, col_type):
        """Gera um novo valor baseado no tipo detectado (modo legacy)."""
        if col_type == "numero":
            return random.randint(1, 9999)
        if col_type == "email":
            name = ''.join(random.choices(string.ascii_lowercase, k=7))
            domain = random.choice(["gmail.com", "outlook.com", "hotmail.com"])
            return f"{name}@{domain}"
        if col_type == "data":
            start = datetime(2000, 1, 1)
            end = datetime(2025, 12, 31)
            delta = end - start
            random_days = random.randint(0, delta.days)
            return (start + timedelta(days=random_days)).strftime("%Y-%m-%d")
        if col_type == "mixed":
            return ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        return ''.join(random.choices(string.ascii_letters, k=12))

    def randomize_dataframe(self, df: pd.DataFrame):
        """Randomiza todos os valores (modo legacy - mantém compatibilidade)."""
        tipos = self.detect_column_types(df)
        randomized = pd.DataFrame()

        for col in df.columns:
            col_type = tipos.get(col, "texto")
            randomized[col] = [self.randomize_value(col_type) for _ in range(len(df))]

        return randomized

