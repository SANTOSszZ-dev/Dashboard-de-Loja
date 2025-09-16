import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# CONFIGURAÇÃO INICIAL
# =========================
st.set_page_config(page_title="Dashboard E-commerce Shopee",
                   layout="wide")

st.title("📊 Dashboard E-commerce - Shopee")

# =========================
# CARREGAR DADOS
# =========================
@st.cache_data
def load_data():
    df = pd.read_excel("Data base 26.08 a 15.09.xlsx")
    return df

df = load_data()

# =========================
# PRÉ-PROCESSAMENTO
# =========================
df["Data de criação do pedido"] = pd.to_datetime(df["Data de criação do pedido"], errors="coerce")

# Filtros interativos
st.sidebar.header("Filtros")
status_filter = st.sidebar.multiselect("Status do Pedido", df["Status do pedido"].unique(), default=df["Status do pedido"].unique())
df_filtered = df[df["Status do pedido"].isin(status_filter)]

# =========================
# KPIs
# =========================
total_pedidos = len(df_filtered)
pedidos_concluidos = len(df_filtered[df_filtered["Status do pedido"] == "CONCLUÍDO"])
pedidos_cancelados = len(df_filtered[df_filtered["Status do pedido"] == "CANCELADO"])
receita_total = df_filtered["Valor Total"].sum()
ticket_medio = receita_total / pedidos_concluidos if pedidos_concluidos > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("📦 Total Pedidos", total_pedidos)
col2.metric("✅ Concluídos", pedidos_concluidos)
col3.metric("❌ Cancelados", pedidos_cancelados)
col4.metric("💰 Receita Total", f"R$ {receita_total:,.2f}")
col5.metric("🎯 Ticket Médio", f"R$ {ticket_medio:,.2f}")

# =========================
# GRÁFICOS
# =========================

# 1. Vendas por data
vendas_por_data = df_filtered.groupby(df_filtered["Data de criação do pedido"].dt.date)["Valor Total"].sum().reset_index()
fig1 = px.line(vendas_por_data, x="Data de criação do pedido", y="Valor Total", title="📅 Vendas por Dia")
st.plotly_chart(fig1, use_container_width=True)

# 2. Status dos pedidos
fig2 = px.pie(df_filtered, names="Status do pedido", title="📊 Distribuição dos Pedidos")
st.plotly_chart(fig2, use_container_width=True)

# 3. Top produtos
top_produtos = df_filtered.groupby("Nome do Produto")["Quantidade"].sum().sort_values(ascending=False).head(10).reset_index()
fig3 = px.bar(top_produtos, x="Quantidade", y="Nome do Produto", orientation="h", title="🏆 Top 10 Produtos Vendidos")
st.plotly_chart(fig3, use_container_width=True)

# =========================
# TABELA DE PEDIDOS
# =========================
st.subheader("📋 Tabela de Pedidos")
st.dataframe(df_filtered)

# =========================
# MAPA DE PEDIDOS
# =========================
if "UF" in df_filtered.columns:
    pedidos_por_estado = df_filtered.groupby("UF")["ID do pedido"].count().reset_index()
    fig4 = px.choropleth(pedidos_por_estado, locations="UF", locationmode="geojson-id",
                         color="ID do pedido", scope="south america",
                         title="🗺️ Pedidos por Estado (Brasil)")
    st.plotly_chart(fig4, use_container_width=True)
