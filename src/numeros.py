"""Converte números escritos do jeito brasileiro (ou americano) em valores numéricos."""
import re

import pandas as pd


def para_numero(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    t = str(v).strip().replace("R$", "").replace("%", "").replace("\xa0", "").replace(" ", "")
    neg = t.startswith("(") and t.endswith(")") or t.startswith("-")
    t = t.strip("()-")
    if not t:
        return None
    if "," in t and "." in t:  # 1.234,56 (BR) ou 1,234.56 (US)
        t = t.replace(".", "").replace(",", ".") if t.rfind(",") > t.rfind(".") else t.replace(",", "")
    elif "," in t:  # 1234,56 ou 1,234,567
        t = t.replace(",", "") if re.fullmatch(r"\d{1,3}(,\d{3}){2,}", t) else t.replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+", t):  # 30.000 / 1.234.567 = milhar
        t = t.replace(".", "")
    try:
        x = float(t)
    except ValueError:
        return None
    return -x if neg else x


def coluna_numerica(s: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(s):
        return s.astype(float)
    return s.map(para_numero).astype(float)
