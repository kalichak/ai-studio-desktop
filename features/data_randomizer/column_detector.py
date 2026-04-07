"""Detecção inteligente de tipos de coluna com regex avançado."""
import re
from collections import Counter

def detectar_tipos(linhas, sep):
    """
    Analisa as colunas e determina o tipo de dado predominante em cada uma.
    Usa uma abordagem de 'votação' para evitar falsos positivos em linhas sujas.
    """
    if not linhas:
        return {}

    num_colunas = len(linhas[0].split(sep))

    # PROTEÇÃO: Se separador errado criar muitas colunas, aborta
    if num_colunas > 500:
        print(f"⚠️ AVISO: Separador pode estar errado ({num_colunas} colunas detectadas)")
        return {i: "texto" for i in range(min(num_colunas, 50))}

    contagem_tipos = {i: Counter() for i in range(num_colunas)}

    # Analisa uma amostra maior para melhor precisão (até 100 linhas)
    amostra = linhas[:100]

    for linha in amostra:
        campos = linha.split(sep)
        for i, c in enumerate(campos):
            if i >= num_colunas: break

            c = c.strip()
            if not c:
                continue

            # Regras de detecção (Inteligência)
            if re.match(r"^[^@]+@[^@]+\.[^@]+$", c):
                contagem_tipos[i]["email"] += 1
            elif re.match(r"^\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}$", c):
                contagem_tipos[i]["cnpj"] += 1
            elif re.match(r"^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$", c):
                contagem_tipos[i]["cpf"] += 1
            elif re.match(r"^\d{2}[-/.]\d{2}[-/.]\d{4}", c) or re.match(r"^\d{4}[-/.]\d{2}[-/.]\d{2}", c):
                contagem_tipos[i]["data"] += 1
            elif re.match(r"^\d+([.,]\d{2})?$", c) and ("." in c or "," in c):
                contagem_tipos[i]["valor"] += 1
            elif c.isdigit():
                contagem_tipos[i]["numero"] += 1
            elif c.upper() in ['ml','KG', 'LT', 'SAC', 'UN', 'TAM', 'CT', 'BD', 'L', 'GL', 'BBP', 'CX', 'PC', 'MT', 'M', 'CM', 'ML']:
                contagem_tipos[i]["unidade_medida"] += 1
            elif re.fullmatch(r"[A-Z]{2}", c.upper()):
                contagem_tipos[i]["uf"] += 1
            elif any(x in c.upper() for x in ["LTDA", "S.A", " SA", "EIRELI", "MEI", "INC"]):
                contagem_tipos[i]["empresa"] += 1
            elif " " in c and sum(1 for char in c if char.isalpha()) > 3:
                # Nome de pessoa geralmente tem espaço e letras
                contagem_tipos[i]["pessoa"] += 1
            else:
                contagem_tipos[i]["texto"] += 1

    tipos_finais = {}

    # Define o tipo vencedor para cada coluna
    for i, counter in contagem_tipos.items():
        if not counter:
            tipos_finais[i] = "texto"
        else:
            # Pega o tipo mais comum na coluna
            comum = counter.most_common(1)[0]
            tipo, qtd = comum
            # Se a confiança for muito baixa (menos de 30% das linhas não vazias), assume texto
            total = sum(counter.values())
            if (qtd / total) > 0.3:
                tipos_finais[i] = tipo
            else:
                tipos_finais[i] = "texto"

    return tipos_finais
