"""Identidade visual do app: tema, cartões e cabeçalho."""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stMarkdown, .stText { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 2rem; max-width: 1180px; }
#MainMenu, footer { visibility: hidden; }

.hero { background: linear-gradient(135deg, var(--c1) 0%, var(--c2) 100%); color: #fff;
        padding: 28px 32px; border-radius: 18px; margin-bottom: 1.6rem;
        box-shadow: 0 10px 30px -12px var(--c1); }
.hero h1 { color: #fff !important; font-size: 2.1rem; font-weight: 800; margin: 0; padding: 0; }
.hero p { color: rgba(255,255,255,.88); margin: .35rem 0 0; font-size: 1.02rem; }

.passo { display: flex; align-items: center; gap: 12px; margin: 2.2rem 0 .8rem; }
.passo .n { background: var(--c1); color: #fff; width: 32px; height: 32px; border-radius: 50%;
            display: grid; place-items: center; font-weight: 700; flex-shrink: 0; }
.passo .t { font-size: 1.35rem; font-weight: 700; }
.passo .s { color: #6b7280; font-size: .9rem; margin-left: 4px; }

[data-testid="stMetric"] { background: #fff; border: 1px solid #e8eaee; border-radius: 14px;
        padding: 16px 18px; box-shadow: 0 1px 3px rgba(16,24,40,.06); }
[data-testid="stMetricLabel"] p { color: #6b7280; font-weight: 500; }
[data-testid="stMetricValue"] { font-weight: 700; font-size: 1.55rem; }
[data-testid="stMetricValue"] > div { overflow: visible; text-overflow: clip; white-space: nowrap; }

.cartao { background: #fff; border: 1px solid #e8eaee; border-radius: 14px; padding: 18px 22px;
          box-shadow: 0 1px 3px rgba(16,24,40,.06); margin-bottom: 1rem; }
.selo { display: inline-block; padding: 4px 12px; border-radius: 999px; font-weight: 600; font-size: .85rem; }
.selo.ok { background: #dcfce7; color: #166534; } .selo.at { background: #fef3c7; color: #92400e; }
.selo.ru { background: #fee2e2; color: #991b1b; } .selo.ne { background: #eef2f7; color: #374151; }

.stButton > button, .stDownloadButton > button { border-radius: 10px; font-weight: 600; }
.stButton > button[kind="primary"] { background: var(--c1); border-color: var(--c1); }
[data-testid="stFileUploaderDropzone"] { border-radius: 14px; }
[data-testid="stSidebar"] { background: #f7f8fa; }
.relatorio { background: #fff; border-left: 5px solid var(--c1); border-radius: 12px;
             padding: 6px 26px 18px; box-shadow: 0 1px 3px rgba(16,24,40,.06); }
</style>
"""


def aplicar(cor1: str, cor2: str):
    st.markdown(f"<style>:root {{ --c1: {cor1}; --c2: {cor2}; }}</style>" + CSS, unsafe_allow_html=True)


def cabecalho(icone: str, titulo: str, subtitulo: str):
    st.markdown(f'<div class="hero"><h1>{icone} {titulo}</h1><p>{subtitulo}</p></div>', unsafe_allow_html=True)


def passo(n, titulo: str, sub: str = ""):
    st.markdown(f'<div class="passo"><div class="n">{n}</div><div class="t">{titulo}</div>'
                f'<div class="s">{sub}</div></div>', unsafe_allow_html=True)


def selo(texto: str, tipo: str = "ne") -> str:
    return f'<span class="selo {tipo}">{texto}</span>'


def barras(serie, cor: str, horizontal: bool = False, altura: int = 240, fmt: str = ",.0f"):
    """Gráfico de barras fixo (sem zoom acidental ao rolar a página)."""
    import altair as alt
    import pandas as pd

    df = pd.DataFrame({"rotulo": [str(i) for i in serie.index], "valor": list(serie.values)})
    ordem = list(df["rotulo"])
    eixo_cat = alt.Y if horizontal else alt.X
    eixo_val = alt.X if horizontal else alt.Y
    base = alt.Chart(df).encode(
        eixo_cat("rotulo:N", sort=ordem, title=None, axis=alt.Axis(labelAngle=0, labelLimit=160)),
        eixo_val("valor:Q", title=None, axis=alt.Axis(grid=True, gridOpacity=.35)),
        tooltip=[alt.Tooltip("rotulo:N", title=" "), alt.Tooltip("valor:Q", title="Valor", format=fmt)],
    )
    graf = base.mark_bar(color=cor, cornerRadiusEnd=4) + base.mark_text(
        align="left" if horizontal else "center", baseline="middle" if horizontal else "bottom",
        dx=4 if horizontal else 0, dy=0 if horizontal else -4, fontSize=11, color="#374151"
    ).encode(text=alt.Text("valor:Q", format=fmt))
    st.altair_chart(graf.properties(height=altura).configure_view(stroke=None), width="stretch")
