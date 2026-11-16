"""Projeção de fechamento do mês e classificação de risco por vendedor."""
import pandas as pd


def analisar(df: pd.DataFrame, dias_uteis_passados: int, dias_uteis_mes: int) -> pd.DataFrame:
    d = df.copy()
    ritmo = d["vendas_ate_hoje"] / dias_uteis_passados
    d["projecao"] = (ritmo * dias_uteis_mes).round(0)
    d["atingimento_proj_pct"] = (d["projecao"] / d["meta"] * 100).round(1)
    d["falta"] = (d["meta"] - d["vendas_ate_hoje"]).clip(lower=0)
    restantes = max(dias_uteis_mes - dias_uteis_passados, 1)
    d["necessario_por_dia"] = (d["falta"] / restantes).round(0)
    d["conversao_pct"] = (d["negocios_fechados"] / d["propostas_enviadas"] * 100).round(1)
    d["tendencia_vs_media"] = ((d["atingimento_proj_pct"] - d["media_atingimento_3m"])).round(1)

    def risco(row):
        if row.atingimento_proj_pct >= 100: return "🟢 No ritmo"
        if row.atingimento_proj_pct >= 85: return "🟡 Atenção"
        return "🔴 Risco"

    def gargalo(row):
        if row.propostas_enviadas < d["propostas_enviadas"].median() * 0.7:
            return "Volume baixo de propostas (prospecção)"
        if row.conversao_pct < d["conversao_pct"].median() * 0.75:
            return "Conversão baixa (negociação/fechamento)"
        if row.ticket_medio < d["ticket_medio"].median() * 0.75:
            return "Ticket baixo (mix/oferta)"
        return "Sem gargalo claro"

    d["risco"] = d.apply(risco, axis=1)
    d["gargalo"] = d.apply(gargalo, axis=1)
    return d.sort_values("atingimento_proj_pct")


def resumo_equipe(d: pd.DataFrame) -> dict:
    return {
        "meta_equipe": float(d["meta"].sum()),
        "projecao_equipe": float(d["projecao"].sum()),
        "atingimento_equipe_pct": round(d["projecao"].sum() / d["meta"].sum() * 100, 1),
        "em_risco": int((d["risco"] == "🔴 Risco").sum()),
        "em_atencao": int((d["risco"] == "🟡 Atenção").sum()),
    }
