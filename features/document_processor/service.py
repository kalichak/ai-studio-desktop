"""Serviço de processamento de documentos (CSV, Excel, TXT)."""
import pandas as pd
import io
from typing import Dict, List, Any, Tuple
from core.gemini_client import GeminiClient

class DocumentProcessorService:
    """Processa e analisa documentos estruturados."""
    
    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client
        self.current_data = None
        self.current_filename = None
    
    def load_file(self, file_path: str) -> Tuple[bool, str, pd.DataFrame]:
        """
        Carrega arquivo CSV, Excel ou TXT.
        
        Returns:
            Tuple: (sucesso, mensagem, dataframe)
        """
        try:
            if file_path.endswith('.csv'):
                # Tenta diferentes encodings
                for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        break
                    except:
                        continue
                else:
                    return False, "Erro ao decodificar CSV", None
            
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            
            elif file_path.endswith('.txt'):
                # Detecta separador automaticamente
                with open(file_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline()
                    separator = self._detect_separator(first_line)
                df = pd.read_csv(file_path, sep=separator, encoding='utf-8')
            
            else:
                return False, "Formato não suportado. Use CSV, Excel ou TXT", None
            
            self.current_data = df
            self.current_filename = file_path.split('/')[-1]
            
            msg = f"✅ Arquivo carregado: {len(df)} linhas, {len(df.columns)} colunas"
            return True, msg, df
        
        except Exception as e:
            return False, f"Erro ao carregar arquivo: {str(e)}", None
    
    def _detect_separator(self, line: str) -> str:
        """Detecta separador de arquivo texto."""
        separators = [',', ';', '\t', '|']
        counts = {sep: line.count(sep) for sep in separators}
        return max(counts, key=counts.get)
    
    def get_file_info(self) -> Dict[str, Any]:
        """Retorna informações do arquivo carregado."""
        if self.current_data is None:
            return {"error": "Nenhum arquivo carregado"}
        
        df = self.current_data
        
        return {
            "filename": self.current_filename,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "column_types": {col: str(df[col].dtype) for col in df.columns},
            "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB",
            "preview": df.head(5).to_dict('records')
        }
    
    def analyze_columns(self) -> Dict[str, Any]:
        """Analisa características de cada coluna."""
        if self.current_data is None:
            return {"error": "Nenhum arquivo carregado"}
        
        df = self.current_data
        analysis = {}
        
        for col in df.columns:
            col_data = df[col]
            analysis[col] = {
                "tipo": str(col_data.dtype),
                "nulos": int(col_data.isnull().sum()),
                "unicos": int(col_data.nunique()),
                "amostra": list(col_data.dropna().head(3).astype(str))
            }
            
            # Detecta tipo semântico
            if col_data.dtype in ['int64', 'float64']:
                analysis[col]["tipo_semantico"] = "Numérico"
                analysis[col]["min"] = float(col_data.min())
                analysis[col]["max"] = float(col_data.max())
                analysis[col]["media"] = float(col_data.mean())
            
            elif self._is_date_column(col_data):
                analysis[col]["tipo_semantico"] = "Data/Hora"
            
            elif self._is_email_column(col_data):
                analysis[col]["tipo_semantico"] = "Email"
            
            elif self._is_phone_column(col_data):
                analysis[col]["tipo_semantico"] = "Telefone"
            
            elif self._is_cpf_column(col_data):
                analysis[col]["tipo_semantico"] = "CPF/CNPJ"
            
            else:
                analysis[col]["tipo_semantico"] = "Texto"
        
        return analysis
    
    def _is_date_column(self, series: pd.Series) -> bool:
        """Verifica se coluna é data."""
        try:
            pd.to_datetime(series.dropna().head(10))
            return True
        except:
            return False
    
    def _is_email_column(self, series: pd.Series) -> bool:
        """Verifica se coluna é email."""
        sample = series.dropna().astype(str).head(10)
        return sample.str.contains('@').sum() > len(sample) * 0.7
    
    def _is_phone_column(self, series: pd.Series) -> bool:
        """Verifica se coluna é telefone."""
        sample = series.dropna().astype(str).head(10)
        return sample.str.match(r'^\(?[\d\s\-\(\)]+\)?$').sum() > len(sample) * 0.7
    
    def _is_cpf_column(self, series: pd.Series) -> bool:
        """Verifica se coluna é CPF/CNPJ."""
        sample = series.dropna().astype(str).head(10)
        # Padrão: XXX.XXX.XXX-XX ou XX.XXX.XXX/XXXX-XX
        pattern = r'^\d{3}\.\d{3}\.\d{3}-\d{2}$|^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$'
        return sample.str.match(pattern).sum() > len(sample) * 0.5
    
    def filter_data(self, column: str, value: str, operation: str = "equals") -> pd.DataFrame:
        """
        Filtra dados baseado em critério.
        
        Args:
            column: Nome da coluna
            value: Valor para filtrar
            operation: 'equals', 'contains', 'greater', 'less'
        """
        if self.current_data is None:
            return None
        
        df = self.current_data
        
        if operation == "equals":
            return df[df[column] == value]
        elif operation == "contains":
            return df[df[column].astype(str).str.contains(value, case=False, na=False)]
        elif operation == "greater":
            return df[df[column] > float(value)]
        elif operation == "less":
            return df[df[column] < float(value)]
        
        return df
    
    def export_data(self, df: pd.DataFrame, output_path: str, format: str = "csv") -> Tuple[bool, str]:
        """
        Exporta dados processados.
        
        Args:
            df: DataFrame para exportar
            output_path: Caminho do arquivo de saída
            format: 'csv' ou 'excel'
        """
        try:
            if format == "csv":
                df.to_csv(output_path, index=False, encoding='utf-8-sig')
            elif format == "excel":
                df.to_excel(output_path, index=False)
            else:
                return False, "Formato não suportado"
            
            return True, f"✅ Arquivo exportado: {output_path}"
        
        except Exception as e:
            return False, f"Erro ao exportar: {str(e)}"
    
    async def analyze_with_ai(self, question: str, model: str):
        """
        Analisa dados usando IA.
        
        Args:
            question: Pergunta sobre os dados
            model: Modelo Gemini para usar
        """
        if self.current_data is None:
            yield "❌ Nenhum arquivo carregado"
            return
        
        # Prepara contexto
        info = self.get_file_info()
        analysis = self.analyze_columns()
        
        prompt = f"""Você é um analista de dados. Analise este dataset e responda a pergunta.

**Dataset: {info['filename']}**
- Linhas: {info['rows']}
- Colunas: {info['columns']}

**Colunas disponíveis:**
{self._format_columns_for_prompt(analysis)}

**Preview dos dados (primeiras 5 linhas):**
```
{self.current_data.head(5).to_string()}
```

**Pergunta do usuário:**
{question}

Forneça uma resposta clara e, se aplicável, sugira análises ou transformações nos dados.
"""
        
        async for chunk in self.client.generate_stream(prompt, model):
            yield chunk
    
    def _format_columns_for_prompt(self, analysis: Dict) -> str:
        """Formata análise de colunas para o prompt."""
        lines = []
        for col, info in analysis.items():
            tipo = info.get('tipo_semantico', info['tipo'])
            lines.append(f"- {col}: {tipo} ({info['unicos']} valores únicos)")
        return "\n".join(lines)