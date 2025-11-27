import pandas as pd
import random
import string
from datetime import datetime, timedelta

class DataRandomizerService:
    """Randomizador de dados offline - lê CSV/XLSX e gera dataset randomizado."""

    def load_document(self, file_path: str):
        """Carrega o documento e detecta formato automaticamente."""
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        elif file_path.endswith(".txt"):
            df = pd.read_csv(file_path, sep="\t")
        else:
            raise ValueError("Formato não suportado: Use CSV, XLSX ou TXT")

        return df

    def detect_column_type(self, series):
        """Detecta o tipo de coluna com heurística simples."""
        sample = str(series.iloc[0])

        if sample.isdigit():
            return "number"
        if "@" in sample:
            return "email"
        if any(x.isdigit() for x in sample) and any(x.isalpha() for x in sample):
            return "mixed"
        if "-" in sample and len(sample) >= 8:
            return "date"

        return "text"

    def randomize_value(self, col_type):
        """Gera um novo valor baseado no tipo detectado."""
        if col_type == "number":
            return random.randint(1, 9999)
        if col_type == "email":
            name = ''.join(random.choices(string.ascii_lowercase, k=7))
            domain = random.choice(["gmail.com", "outlook.com", "hotmail.com"])
            return f"{name}@{domain}"
        if col_type == "date":
            start = datetime(2000, 1, 1)
            end = datetime(2025, 12, 31)
            delta = end - start
            random_days = random.randint(0, delta.days)
            return (start + timedelta(days=random_days)).strftime("%Y-%m-%d")
        if col_type == "mixed":
            return ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        return ''.join(random.choices(string.ascii_letters, k=12))

    def randomize_dataframe(self, df: pd.DataFrame):
        """Randomiza todos os valores de todas as colunas."""
        randomized = pd.DataFrame()

        for col in df.columns:
            col_type = self.detect_column_type(df[col])
            randomized[col] = [self.randomize_value(col_type) for _ in range(len(df))]

        return randomized
