import datetime as dt

import numpy as np
import pandas as pd
import streamlit as st

from src.analise import analisar, resumo_equipe
from src.pauta import pauta_reuniao

st.set_page_config(page_title="Performance Comercial", page_icon="📈", layout="wide")
st.title("📈 Performance Comercial")
st.caption("Descubra no meio do mês quem não vai bater a meta, por quê, e o que fazer a respeito.")

COLUNAS = {
    "vendedor": "Nome do vendedor",
    "meta": "Meta do mês (R$)",
    "vendas_ate_hoje": "Vendido até hoje (R$)",
    "propostas_enviadas": "Propostas enviadas no mês",
    "negocios_fechados": "Negócios fechados no mês",
    "ticket_medio": "Ticket médio (R$)",
    "media_atingimento_3m": "Atingimento médio nos últimos 3 meses (%)",
}

with st.sidebar:
    st.subheader("Período")
    hoje = st.date_input("Data de referência", dt.date.today(), format="DD/MM/YYYY")
    inicio = hoje.replace(day=1)
    fim = (inicio + dt.timedelta(days=32)).replace(day=1)
    feriados = st.number_input("Feriados no mês", 0, 5, 0)
    dias_mes = int(np.busday_count(inicio, fim)) - feriados
    dias_passados = max(1, min(int(np.busday_count(inicio, hoje + dt.timedelta(days=1))), dias_mes))
    st.write(f"Dias úteis: **{dias_passados} de {dias_mes}**")
    st.divider()
    modelo = pd.DataFrame(columns=list(COLUNAS.values()))
    st.download_button("Baixar planilha modelo", modelo.to_csv(index=False).encode("utf-8-sig"),
                       "modelo_equipe.csv")
    usar_exemplo = st.toggle("Usar equipe de exemplo")

st.header("1 · Dados da equipe")
st.write("Envie a planilha do mês (CSV ou Excel) ou preencha a tabela direto aqui.")
arq = st.file_uploader("Planilha da equipe", type=["csv", "xlsx", "xls"])

if arq:
    bruto = pd.read_excel(arq) if arq.name.lower().endswith(("xlsx", "xls")) else pd.read_csv(arq, sep=None, engine="python")
    st.write("**Indique qual coluna da sua planilha corresponde a cada informação:**")
    cols = st.columns(len(COLUNAS))
    mapa = {}
    for (chave, rotulo), c in zip(COLUNAS.items(), cols):
        sugestao = next((i for i, x in enumerate(bruto.columns) if str(x).strip().lower() in (chave, rotulo.lower())), 0)
        mapa[chave] = c.selectbox(rotulo, bruto.columns, index=sugestao)
    base = pd.DataFrame({k: bruto[v] for k, v in mapa.items()})
elif usar_exemplo:
    base = pd.read_csv("data/equipe_exemplo.csv")
else:
    base = pd.DataFrame([{k: (None if k == "vendedor" else 0) for k in COLUNAS}])

base = st.data_editor(base, num_rows="dynamic", width="stretch",
                      column_config={k: st.column_config.Column(v) for k, v in COLUNAS.items()})

for c in COLUNAS:
    if c != "vendedor":
        base[c] = pd.to_numeric(base[c], errors="coerce").fillna(0)
base = base[(base["vendedor"].notna()) & (base["meta"] > 0)]
if base.empty:
    st.info("Preencha ao menos um vendedor com meta para ver a análise.")
    st.stop()
base["propostas_enviadas"] = base["propostas_enviadas"].replace(0, 1)

d = analisar(base, dias_passados, dias_mes)
eq = resumo_equipe(d)

st.header("2 · Projeção do mês")
k = st.columns(4)
k[0].metric("Meta da equipe", f"R$ {eq['meta_equipe']:,.0f}")
k[1].metric("Projeção de fechamento", f"R$ {eq['projecao_equipe']:,.0f}", f"{eq['atingimento_equipe_pct'] - 100:.1f}% vs meta")
k[2].metric("🔴 Em risco", eq["em_risco"])
k[3].metric("🟡 Em atenção", eq["em_atencao"])

st.bar_chart(d.set_index("vendedor")["atingimento_proj_pct"], y_label="Projeção (% da meta)")
st.dataframe(
    d[["vendedor", "risco", "atingimento_proj_pct", "tendencia_vs_media", "necessario_por_dia",
       "conversao_pct", "ticket_medio", "gargalo"]].rename(columns={
        "vendedor": "Vendedor", "risco": "Status", "atingimento_proj_pct": "Projeção %",
        "tendencia_vs_media": "vs média 3m (p.p.)", "necessario_por_dia": "R$/dia necessário",
        "conversao_pct": "Conversão %", "ticket_medio": "Ticket", "gargalo": "Gargalo"}),
    hide_index=True, width="stretch")

st.header("3 · Reunião")
st.markdown(pauta_reuniao(d, eq, dias_mes - dias_passados))
