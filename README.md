# 📈 Performance Comercial

> Projeta o fechamento do mês de cada vendedor, identifica **onde está o gargalo** (prospecção, conversão ou ticket) e monta a **pauta da reunião semanal** com roteiros de coaching 1:1.

## Problema de negócio

Passei 12 anos como gerente de vendas. O padrão é sempre o mesmo: o gerente descobre que alguém não vai bater a meta na última semana do mês, quando já não dá para reagir. E quando descobre, a conversa vira "precisa vender mais", sem diagnóstico do *porquê*.

## Como funciona

1. **Entrada real**: envie a planilha da equipe (CSV ou Excel, com qualquer nome de coluna, porque você indica qual é qual) ou preencha a tabela direto na tela. Há uma planilha modelo para baixar.
2. **Calendário automático**: dias úteis do mês e dias já passados calculados a partir da data, com campo para feriados.
3. **Projeção pelo ritmo atual**: vendas até hoje ÷ dias úteis passados × dias úteis do mês.
4. **Semáforo de risco**: 🟢 ≥100% · 🟡 85–99% · 🔴 <85% da meta projetada.
5. **Diagnóstico do gargalo**, comparando cada vendedor com a mediana da equipe:
   - poucas propostas → problema de **prospecção**
   - baixa conversão → problema de **negociação**
   - ticket baixo → problema de **mix/oferta**
6. **Quanto falta por dia**: a meta transformada em número diário, que é como o vendedor pensa.
7. **Pauta da reunião**: resumo da equipe, gargalo mais comum, roteiro 1:1 (pergunta de abertura + compromisso da semana) para quem está em risco e reconhecimento para quem está bem.

## Por que isso importa

Coaching genérico não muda resultado. Saber que um vendedor envia poucas propostas e outro perde na negociação muda completamente a conversa com cada um. E a ferramenta entrega isso na metade do mês, não no fim.

## Como usar

Abra o app, envie a planilha da equipe ou preencha a tabela. Para só conhecer a ferramenta, ative **Usar equipe de exemplo** na barra lateral. Não precisa de nenhuma chave ou cadastro.

## Publicar

Em [share.streamlit.io](https://share.streamlit.io), crie um app apontando para este repositório e o arquivo `app.py`.
