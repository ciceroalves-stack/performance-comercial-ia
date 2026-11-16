import datetime as dt

import numpy as np
import pandas as pd
import streamlit as st

from src.analise import analisar, resumo_equipe
from src.numeros import coluna_numerica
from src.pauta import pauta_reuniao
from src.ui import aplicar, barras, cabecalho, passo, selo

st.set_page_config(page_title="Performance Comercial", page_icon="📈", layout="wide")
aplicar("#2563eb", "#7c3aed")
cabecalho("📈", "Performance Comercial",
          "Descubra no meio do mês quem não vai bater a meta, por quê, e o que conversar com cada vendedor.")

COLUNAS = {
    "vendedor": "Vendedor",
    "meta": "Meta do mês (R$)",
    "vendas_ate_hoje": "Vendido até hoje (R$)",
    "propostas_enviadas": "Propostas enviadas",
    "negocios_fechados": "Negócios fechados",
    "ticket_medio": "Ticket médio (R$)",
    "media_atingimento_3m": "Atingimento médio 3 meses (%)",
}


def brl(v):
    return "R$ " + f"{v:,.0f}".replace(",", ".")


with st.sidebar:
    st.markdown("### 📅 Período")
    hoje = st.date_input("Data de referência", dt.date.today(), format="DD/MM/YYYY")
    inicio = hoje.replace(day=1)
    fim = (inicio + dt.timedelta(days=32)).replace(day=1)
    feriados = st.number_input("Feriados em dia útil neste mês", 0, 5, 0)
    dias_mes = max(1, int(np.busday_count(inicio, fim)) - feriados)
    dias_passados = max(1, min(int(np.busday_count(inicio, hoje + dt.timedelta(days=1))), dias_mes))
    st.progress(dias_passados / dias_mes, text=f"{dias_passados} de {dias_mes} dias úteis")
    st.divider()
    st.markdown("### 📥 Planilha")
    modelo = pd.DataFrame(columns=list(COLUNAS.values()))
    st.download_button("Baixar planilha modelo", modelo.to_csv(index=False, sep=";").encode("utf-8-sig"),
                       "modelo_equipe.csv", width="stretch")
    st.divider()
    st.markdown("### 🧪 Conhecer a ferramenta")
    usar_exemplo = st.toggle("Usar equipe de demonstração")

passo(1, "Dados da equipe", "envie a planilha do mês ou preencha a tabela")
arq = st.file_uploader("Planilha da equipe (CSV ou Excel)", type=["csv", "xlsx", "xls"])

if arq:
    try:
        bruto = (pd.read_excel(arq, dtype=str) if arq.name.lower().endswith(("xlsx", "xls"))
                 else pd.read_csv(arq, sep=None, engine="python", encoding_errors="ignore", dtype=str))
    except Exception as e:
        st.error(f"Não consegui abrir a planilha: {e}")
        st.stop()
    with st.expander("🔗 Ligar as colunas da sua planilha", expanded=True):
        cols = st.columns(4)
        mapa = {}
        for i, (chave, rotulo) in enumerate(COLUNAS.items()):
            nomes = [str(x).strip().lower() for x in bruto.columns]
            sug = next((j for j, x in enumerate(nomes) if x in (chave, rotulo.lower())
                        or rotulo.lower().split(" (")[0] in x), min(i, len(bruto.columns) - 1))
            mapa[chave] = cols[i % 4].selectbox(rotulo, bruto.columns, index=sug)
    base = pd.DataFrame({k: bruto[v].values for k, v in mapa.items()}).dropna(how="all")
elif usar_exemplo:
    base = pd.read_csv("data/equipe_exemplo.csv")
else:
    base = pd.DataFrame([{k: (None if k == "vendedor" else 0) for k in COLUNAS}])

for c in COLUNAS:
    if c != "vendedor":
        base[c] = coluna_numerica(base[c])
base = st.data_editor(base, num_rows="dynamic", width="stretch", hide_index=True,
                      column_config={k: st.column_config.Column(v) for k, v in COLUNAS.items()})


for c in COLUNAS:
    if c != "vendedor":
        base[c] = coluna_numerica(base[c]).fillna(0)
base = base[base["vendedor"].notna() & (base["vendedor"].astype(str).str.strip() != "") & (base["meta"] > 0)]
if base.empty:
    st.info("Preencha ao menos **um vendedor com meta** para ver a análise.")
    st.stop()
base["propostas_enviadas"] = base["propostas_enviadas"].clip(lower=1)
base["media_atingimento_3m"] = base["media_atingimento_3m"].where(base["media_atingimento_3m"] > 0, 100)

d = analisar(base, dias_passados, dias_mes)
eq = resumo_equipe(d)

passo(2, "Projeção do mês", f"ritmo de {dias_passados} dias úteis projetado para {dias_mes}")
ating = eq["atingimento_equipe_pct"]
tipo = "ok" if ating >= 100 else "at" if ating >= 85 else "ru"
st.markdown(f'<div class="cartao" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px">'
            f'<div><span style="color:#6b7280">A equipe deve fechar o mês em</span><br>'
            f'<span style="font-size:1.4rem;font-weight:800">{str(round(ating, 1)).replace(".", ",")}% da meta</span></div>'
            f'{selo("No ritmo" if tipo == "ok" else "Atenção" if tipo == "at" else "Risco de não bater", tipo)}</div>',
            unsafe_allow_html=True)

k = st.columns(4)
k[0].metric("Meta da equipe", brl(eq["meta_equipe"]))
k[1].metric("Projeção de fechamento", brl(eq["projecao_equipe"]), f"{ating - 100:+.1f}% vs meta".replace(".", ","))
k[2].metric("🔴 Em risco", eq["em_risco"])
k[3].metric("🟡 Em atenção", eq["em_atencao"])

st.markdown("##### Projeção por vendedor (% da meta)")
barras(d.set_index("vendedor")["atingimento_proj_pct"], "#2563eb", horizontal=True, altura=40 + 34 * len(d), fmt=".0f")

st.dataframe(
    d[["vendedor", "risco", "atingimento_proj_pct", "tendencia_vs_media", "necessario_por_dia",
       "conversao_pct", "ticket_medio", "gargalo"]],
    hide_index=True, width="stretch",
    column_config={
        "vendedor": "Vendedor", "risco": "Status",
        "atingimento_proj_pct": st.column_config.ProgressColumn("Projeção", format="%.0f%%", min_value=0,
                                                                max_value=max(130, float(d["atingimento_proj_pct"].max()))),
        "tendencia_vs_media": st.column_config.NumberColumn("vs média 3m", format="%+.1f p.p."),
        "necessario_por_dia": st.column_config.NumberColumn("Precisa por dia", format="R$ %.0f"),
        "conversao_pct": st.column_config.NumberColumn("Conversão", format="%.1f%%"),
        "ticket_medio": st.column_config.NumberColumn("Ticket", format="R$ %.0f"),
        "gargalo": "Gargalo"})

passo(3, "Reunião semanal", "pauta e conversas 1:1")
with st.container(border=True):
    st.markdown(pauta_reuniao(d, eq, dias_mes - dias_passados))
