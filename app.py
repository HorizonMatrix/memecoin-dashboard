# app.py – Dashboard Top 100 Memecoins | E‑CSI
# ============================================================
# Executar:  streamlit run app.py
# Dependências: streamlit  •  pandas  •  numpy

import streamlit as st
import pandas as pd
import numpy as np

FILE_PATH = "top100_memecoins_ecsi.xlsx"   # <- Excel gerado pelo script Python

# ---------------------------------------------------------------------
@st.cache_data(show_spinner="📥 A carregar Top 100 memecoins…")
def load_data(path: str = FILE_PATH) -> pd.DataFrame:
    df = pd.read_excel(path)
    # Converter campos numéricos seguros
    for col in ["E-CSI", "market_cap", "twitter_followers"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ Ficheiro top100_memecoins_ecsi.xlsx não encontrado. Corre o script gerador primeiro ou coloca-o na pasta do app.")
    st.stop()

# ---------------------------------------------------------------------
# Sidebar – filtros
st.sidebar.header("Filtros de Pesquisa")
faixas = ["Fraca", "Moderada", "Forte", "Muito forte", "Extremamente forte"]
sel_faixa = st.sidebar.multiselect("Faixa E‑CSI", options=faixas, default=faixas)

min_cap_m = int(df["market_cap"].min() // 1_000_000)
max_cap_m = int(df["market_cap"].max() // 1_000_000)
cap_range = st.sidebar.slider("Market Cap (milhões USD)", min_cap_m, max_cap_m, (min_cap_m, max_cap_m))

# Aplicar filtros
df_f = df[df["faixa_ecsi"].isin(sel_faixa)]
df_f = df_f[(df_f["market_cap"] / 1_000_000).between(*cap_range)]

# ---------------------------------------------------------------------
# KPIs principais
st.title("🤑 Dashboard – Top 100 Memecoins | E‑CSI")
st.caption("Dados CoinGecko (plano demo) – Junho 2025 • Enhanced Crypto Strength Index")

c1, c2, c3 = st.columns(3)
c1.metric("Tokens", len(df_f))
c2.metric("E‑CSI médio", f"{df_f['E-CSI'].mean():.2f}")
c3.metric("Cap. Total", f"${df_f['market_cap'].sum()/1_000_000_000:.2f} B")

st.divider()

# ---------------------------------------------------------------------
# Ranking por E‑CSI
st.subheader("Ranking (E‑CSI)")
st.dataframe(
    df_f.sort_values("E-CSI", ascending=False)[[
        "rank", "token", "name", "E-CSI", "faixa_ecsi", "market_cap", "twitter_followers"
    ]].reset_index(drop=True),
    use_container_width=True,
)

# ---------------------------------------------------------------------
# Gráfico – Followers vs E‑CSI
st.subheader("Followers Twitter × E‑CSI")
st.scatter_chart(
    df_f.dropna(subset=["twitter_followers", "E-CSI"]),
    x="twitter_followers",
    y="E-CSI",
)

# Rodapé
st.caption("© 2025 • Fórmula E‑CSI = 0.25·Volume + 0.25·Performance + 0.15·ATH + 0.15·Stability + 0.20·Social")
