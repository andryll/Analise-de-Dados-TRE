import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# =======================
# Config / leitura
# =======================
st.set_page_config(page_title="Análise de Processos", layout="wide")

file_path = "data.csv"
df = pd.read_csv(file_path, sep="\t")

# Converter a coluna de data (aceita formatos dia/mês/ano)
df["Dat. preenchimento"] = pd.to_datetime(df["Dat. preenchimento"], errors="coerce", dayfirst=True)

# Checagem de colunas importantes (ajuste os nomes se necessário)
required_cols = [
    "Tribunal", "Dat. preenchimento",
    "Classe do Processo", "Município",
    "Assunto Principal do Processo", "Unidade"
]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"As seguintes colunas estão faltando no CSV: {missing}. Ajuste os nomes das colunas e tente novamente.")
    st.stop()

# =======================
# Gráficos fixos -> salvar em PNG (barras)
# =======================
# Processos por Tribunal
df_tribunal = df["Tribunal"].dropna().value_counts()
fig, ax = plt.subplots(figsize=(10,5))
sns.barplot(x=df_tribunal.index, y=df_tribunal.values, ax=ax)
ax.set_title("Quantidade de Processos por Tribunal")
ax.set_xlabel("Tribunal")
ax.set_ylabel("Quantidade")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
fig.savefig("processos_por_tribunal.png")
plt.close(fig)

# Processos por Período (mensal) - barras
df_time = df.dropna(subset=["Dat. preenchimento"]).groupby(df["Dat. preenchimento"].dt.to_period("M")).size()
df_time.index = df_time.index.to_timestamp()
# transformar index em string para barras (evita problemas de formatação)
period_labels = df_time.index.strftime("%Y-%m")
fig, ax = plt.subplots(figsize=(12,6))
sns.barplot(x=period_labels, y=df_time.values, ax=ax)
ax.set_title("Quantidade de Processos por Período (mês/ano)")
ax.set_xlabel("Período (YYYY-MM)")
ax.set_ylabel("Quantidade")
plt.xticks(rotation=90)
plt.tight_layout()
fig.savefig("processos_por_periodo.png")
plt.close(fig)

# =======================
# Streamlit App
# =======================
st.title("📊 Análise de Processos por Tribunal")

# Lista de tribunais
tribunais = sorted(df["Tribunal"].dropna().unique().tolist())
tribunal_selecionado = st.selectbox("Selecione o Tribunal:", tribunais)

# Determinar intervalo mínimo/máximo baseado no tribunal selecionado (se houver datas)
mask_trib = df["Tribunal"] == tribunal_selecionado
dates_trib = df.loc[mask_trib, "Dat. preenchimento"].dropna()

if not dates_trib.empty:
    min_date = dates_trib.min().date()
    max_date = dates_trib.max().date()
else:
    # fallback global (se o tribunal não tiver datas)
    all_dates = df["Dat. preenchimento"].dropna()
    if not all_dates.empty:
        min_date = all_dates.min().date()
        max_date = all_dates.max().date()
    else:
        # sem datas no dataset
        today = pd.Timestamp.today().date()
        min_date = today
        max_date = today

# Date input (entrega datetime.date) — garantimos min/max e valor inicial
periodo = st.date_input(
    "Selecione o período (início e fim):",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    key="periodo"
)

# Normalizar retorno do date_input (pode ser um único dia ou tupla)
if isinstance(periodo, (list, tuple)):
    inicio = pd.to_datetime(periodo[0])
    fim = pd.to_datetime(periodo[1])
else:
    inicio = pd.to_datetime(periodo)
    fim = inicio

# Filtrar dados: tribunal + intervalo de datas (inclui inicio e fim)
df_filtrado = df.loc[
    (df["Tribunal"] == tribunal_selecionado) &
    (df["Dat. preenchimento"].notna()) &
    (df["Dat. preenchimento"] >= inicio) &
    (df["Dat. preenchimento"] <= fim)
].copy()

st.write(f"### Total de registros no {tribunal_selecionado} ({inicio.date()} até {fim.date()}): {len(df_filtrado)}")

# Função utilitária para plotar barras horizontais por contagem
def plot_count_horizontal(dataframe, coluna, title, topn=None):
    if dataframe.empty:
        st.info("Nenhum registro no filtro atual.")
        return
    s = dataframe[coluna].dropna().value_counts()
    if s.empty:
        st.info(f"Nenhum valor disponível na coluna '{coluna}' para o filtro atual.")
        return
    if topn:
        s = s.iloc[:topn]
    fig, ax = plt.subplots(figsize=(10,5))
    sns.barplot(x=s.values, y=s.index, ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Quantidade")
    ax.set_ylabel("")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# Plots no Streamlit
st.subheader("Distribuição por Classe do Processo")
plot_count_horizontal(df_filtrado, "Classe do Processo", "Distribuição por Classe do Processo")

st.subheader("Distribuição por Município (top 15)")
plot_count_horizontal(df_filtrado, "Município", "Distribuição por Município", topn=15)

st.subheader("Distribuição por Assunto Principal do Processo (top 15)")
plot_count_horizontal(df_filtrado, "Assunto Principal do Processo", "Distribuição por Assunto Principal do Processo", topn=15)

st.subheader("Distribuição por Unidade (top 15)")
plot_count_horizontal(df_filtrado, "Unidade", "Distribuição por Unidade", topn=15)

# Botões para baixar os PNGs gerados (opcional)
with open("processos_por_tribunal.png", "rb") as f:
    st.download_button("⬇️ Baixar processos_por_tribunal.png", f, file_name="processos_por_tribunal.png")

with open("processos_por_periodo.png", "rb") as f:
    st.download_button("⬇️ Baixar processos_por_periodo.png", f, file_name="processos_por_periodo.png")
