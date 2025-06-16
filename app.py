# ========== DASHBOARD INTERATIVO (2 PÁGINAS) ==========
st.set_page_config(page_title="Memecoin Dashboard E-CSI", layout="wide")

# Sidebar para navegação
pagina = st.sidebar.radio("Página:", ["Dashboard", "Detalhe do Token"])

# Limpa valores nulos nas métricas sociais
for col in ["twitter_followers", "engagement", "sentiment_pct"]:
    if col in df.columns:
        df[col] = df[col].fillna(0)

if pagina == "Dashboard":
    st.title("💸 Dashboard – Top 100 Memecoins | E-CSI + Social")
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
    # Aplicar filtros
    df_filt = df[
        df["faixa_ecsi"].isin(faixas)
        & (df.market_cap >= cap_min*1_000_000)
        & (df.market_cap <= cap_max*1_000_000)
        & (df.engagement >= eng_min)
        & (df.engagement <= eng_max)
        & (df.sentiment_pct >= sent_min)
        & (df.sentiment_pct <= sent_max)
    ]
    col1, col2, col3 = st.columns(3)
    col1.metric("Tokens", len(df_filt))
    col2.metric("E-CSI médio", round(df_filt["E-CSI"].mean(),2))
    col3.metric("Cap. Total", f"${df_filt['market_cap'].sum()/1e9:,.2f} B")

    # Ranking
    st.subheader("Ranking (E-CSI)")
    cols = [
        "rank", "token", "name", "E-CSI", "faixa_ecsi", "market_cap",
        "twitter_followers", "engagement", "sentiment_pct"
    ]
    st.dataframe(
        df_filt[cols].sort_values("E-CSI", ascending=False).reset_index(drop=True),
        use_container_width=True
    )

    # Gráfico Followers × E-CSI
    import matplotlib.pyplot as plt
    st.subheader("Followers Twitter × E-CSI")
    fig, ax = plt.subplots()
    ax.scatter(df_filt["twitter_followers"], df_filt["E-CSI"], alpha=0.8)
    ax.set_xlabel("Followers (Twitter)")
    ax.set_ylabel("E-CSI")
    ax.grid(True, ls=":", alpha=0.4)
    st.pyplot(fig)

elif pagina == "Detalhe do Token":
    st.title("🔎 Detalhes do Token – Top 100")
    df["ident"] = df["name"] + " (" + df["token"] + ")"
    escolha = st.selectbox("Escolhe um token:", df["ident"].sort_values())
    sel_row = df[df["ident"] == escolha].iloc[0]

    st.markdown("""
        <style>
            .metric-big .stMetric {font-size: 32px !important;}
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Token", sel_row['token'])
    col2.metric("Rank CG", int(sel_row['rank']))
    col3.metric("Market Cap", f"${sel_row['market_cap']/1e6:,.1f}M")
    col4.metric("Followers", int(sel_row['twitter_followers']))

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("E-CSI", sel_row['E-CSI'])
    col6.metric("Faixa", sel_row['faixa_ecsi'])
    col7.metric("Engagement", f"{sel_row['engagement']:.5f}")
    col8.metric("Sentiment", f"{sel_row['sentiment_pct']*100:.1f}%")

    with st.expander("Mais detalhes e histórico"):
        st.write(f"**Variação 24h:** {sel_row['price_change_24h%']:.2f}%")
        st.write(f"**Variação 30d:** {sel_row['price_change_30d%']:.2f}%")
        st.write(f"**ATH change:** {sel_row['ath_change_pct']:.2f}%")
        if "twitter_handle" in sel_row and pd.notna(sel_row["twitter_handle"]) and sel_row["twitter_handle"]:
            st.markdown(f"[Twitter Oficial](https://twitter.com/{sel_row['twitter_handle']})")
        st.dataframe(sel_row)
