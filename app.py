# -*- coding: utf-8 -*-
"""
Dashboard Interativo – Top 100 Memecoins (E-CSI + Social)
=========================================================
Mostra ranking, filtros, e análise social (followers, engagement, sentimento)

Requisitos: streamlit • pandas • numpy • matplotlib
Ficheiro: top100_memecoins_ecsi.xlsx (export do script)
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Dashboard Memecoins E-CSI",
    layout="wide",
)
st.title("💸 Dashboard – Top 100 Memecoins | E-CSI + Social")

@st.cache_data
def carregar_dados():
    df = pd.read_excel("top100_memecoins_ecsi.xlsx")
    # Corrigir NaN sociais
    df["twitter_followers"] = df["twitter_followers"].fillna(0).astype(int)
    df["engagement"] = df["engagement"].fillna(0)
    df["sentiment_pct"] = df["sentiment_pct"].fillna(0)
    return df

df = carregar_dados()

# ---- Filtros laterais ----
st.sidebar.header("Filtros de Pesquisa")
faixas = st.sidebar.multiselect(
    "Faixa E-CSI",
    options=list(df["faixa_ecsi"].unique()),
    default=list(df["faixa_ecsi"].unique()),
)
cap_min, cap_max = st.sidebar.slider(
    "Market Cap (milhões USD)",
    int(df.market_cap.min()//1_000_000),
    int(df.market_cap.max()//1_000_000),
    (int(df.market_cap.min()//1_000_000), int(df.market_cap.max()//1_000_000)),
)
eng_min, eng_max = st.sidebar.slider(
    "Engagement",
    float(df.engagement.min()), float(df.engagement.max()),
    (float(df.engagement.min()), float(df.engagement.max())),
)
sent_min, sent_max = st.sidebar.slider(
    "Sentiment (%)",
    float(df.sentiment_pct.min()), float(df.sentiment_pct.max()),
    (float(df.sentiment_pct.min()), float(df.sentiment_pct.max())),
)

# ---- Aplicar filtros ----
df_filt = df[
    df["faixa_ecsi"].isin(faixas)
    & (df.market_cap >= cap_min*1_000_000)
    & (df.market_cap <= cap_max*1_000_000)
    & (df.engagement >= eng_min)
    & (df.engagement <= eng_max)
    & (df.sentiment_pct >= sent_min)
    & (df.sentiment_pct <= sent_max)
]

# ---- KPIs topo ----
col1, col2, col3 = st.columns(3)
col1.metric("Tokens", len(df_filt))
col2.metric("E-CSI médio", round(df_filt["E-CSI"].mean(),2))
col3.metric("Cap. Total", f"${df_filt['market_cap'].sum()/1e9:,.2f} B")

# ---- Ranking principal ----
st.subheader("Ranking (E-CSI)")
cols = [
    "rank", "token", "name", "E-CSI", "faixa_ecsi", "market_cap",
    "twitter_followers", "engagement", "sentiment_pct"
]
st.dataframe(
    df_filt[cols].sort_values("E-CSI", ascending=False).reset_index(drop=True),
    use_container_width=True
)

# ---- Gráfico Followers × E-CSI ----
st.subheader("Followers Twitter × E-CSI")
fig, ax = plt.subplots()
ax.scatter(df_filt["twitter_followers"], df_filt["E-CSI"], alpha=0.8)
ax.set_xlabel("Followers (Twitter)")
ax.set_ylabel("E-CSI")
ax.grid(True, ls=":", alpha=0.4)
st.pyplot(fig)

# ---- Detalhes por token ----
st.subheader("🔎 Detalhes do Token – Top 100")
opt_token = st.selectbox(
    "Escolhe um token:",
    df["name"] + " (" + df["token"] + ")",
)
sel_row = df[df["name"] + " (" + df["token"] + ")" == opt_token].iloc[0]

colA, colB, colC, colD = st.columns(4)
colA.metric("Token", sel_row["token"])
colB.metric("Rank CG", sel_row["rank"])
colC.metric("Market Cap", f"${sel_row['market_cap']/1e6:,.1f}M")
colD.metric("Followers", int(sel_row["twitter_followers"]))
colA.metric("E-CSI", sel_row["E-CSI"])
colB.metric("Faixa", sel_row["faixa_ecsi"])
colC.metric("Engagement", round(sel_row["engagement"],4))
colD.metric("Sentiment", f"{sel_row['sentiment_pct']*100:.1f}%")
