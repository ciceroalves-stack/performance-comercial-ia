"""Monta a pauta da reunião semanal e os roteiros de coaching 1:1, sem depender de API externa."""

ROTEIRO = {
    "Volume baixo de propostas (prospecção)": (
        "Quais clientes da sua carteira você ainda não procurou este mês?",
        "Bloquear 2h por dia para prospecção e enviar 5 propostas a mais nesta semana."),
    "Conversão baixa (negociação/fechamento)": (
        "Nas últimas propostas que não fecharam, qual foi a objeção que mais apareceu?",
        "Revisar juntos as 3 últimas propostas perdidas e treinar a resposta às objeções."),
    "Ticket baixo (mix/oferta)": (
        "Que produto complementar faria sentido para os clientes que você atende?",
        "Incluir um produto complementar em toda proposta enviada nesta semana."),
    "Sem gargalo claro": (
        "O que mudou na sua rotina em relação aos meses em que você bateu a meta?",
        "Acompanhar o funil todos os dias por uma semana para achar a causa."),
}


def _brl(v):
    return f"R$ {v:,.0f}".replace(",", ".")


def pauta_reuniao(d, eq: dict, dias_restantes: int) -> str:
    t = ["### Pauta da reunião semanal",
         f"**Equipe:** projeção de **{eq['atingimento_equipe_pct']}%** da meta "
         f"({_brl(eq['projecao_equipe'])} de {_brl(eq['meta_equipe'])}). "
         f"{eq['em_risco']} em risco e {eq['em_atencao']} em atenção. Faltam {dias_restantes} dias úteis."]

    if eq["atingimento_equipe_pct"] < 100:
        gap = eq["meta_equipe"] - eq["projecao_equipe"]
        t.append(f"Para fechar a meta, a equipe precisa de **{_brl(gap)}** além do ritmo atual.")

    gargalos = d[d["risco"] != "🟢 No ritmo"]["gargalo"].value_counts()
    if len(gargalos):
        t.append(f"Gargalo mais comum na equipe: **{gargalos.index[0].lower()}**. Vale um treinamento coletivo sobre isso.")

    t.append("\n**Conversas 1:1**")
    for _, v in d.iterrows():
        if v["risco"] == "🟢 No ritmo":
            continue
        pergunta, compromisso = ROTEIRO[v["gargalo"]]
        tend = v["tendencia_vs_media"]
        hist = f"{abs(tend)} p.p. {'abaixo' if tend < 0 else 'acima'} da média dos últimos 3 meses"
        t.append(f"\n**{v['vendedor']}** · {v['risco']} · projeção {v['atingimento_proj_pct']}% ({hist})\n"
                 f"- Gargalo: {v['gargalo']}\n"
                 f"- Pergunta de abertura: _\"{pergunta}\"_\n"
                 f"- Compromisso da semana: {compromisso}\n"
                 f"- Precisa vender {_brl(v['necessario_por_dia'])} por dia útil até o fim do mês")

    top = d[d["risco"] == "🟢 No ritmo"].sort_values("atingimento_proj_pct", ascending=False)
    if len(top):
        nomes = ", ".join(f"{r.vendedor} ({r.atingimento_proj_pct}%)" for r in top.itertuples())
        t.append(f"\n**Reconhecimento:** {nomes} 👏 — peça para compartilharem com a equipe o que está funcionando.")
    return "\n".join(t)
