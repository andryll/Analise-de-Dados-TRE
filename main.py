import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# =======================
# Configuração da Página e Leitura dos Dados
# =======================
# Define o título da página e o layout como 'wide' para ocupar mais espaço
st.set_page_config(page_title="Análise de Processos", layout="wide")

# Caminho para o arquivo de dados. O arquivo precisa estar na mesma pasta.
file_path = "data.csv"
try:
    df = pd.read_csv(file_path, sep="\t")
except FileNotFoundError:
    st.error(f"Erro: O arquivo '{file_path}' não foi encontrado.")
    st.info("Por favor, certifique-se de que o arquivo 'data.csv' está na mesma pasta que o programa e tente novamente.")
    st.stop()


# Converte a coluna de data, aceitando o formato dia/mês/ano
df["Dat. preenchimento"] = pd.to_datetime(df["Dat. preenchimento"], errors="coerce", dayfirst=True)

# Verifica se as colunas essenciais para a análise existem no arquivo
required_cols = [
    "Tribunal", "Dat. preenchimento",
    "Classe do Processo", "Município",
    "Assunto Principal do Processo", "Unidade"
]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"As seguintes colunas obrigatórias estão faltando no CSV: {', '.join(missing)}. Verifique o arquivo e tente novamente.")
    st.stop()

# =======================
# Geração dos Gráficos Estáticos (Salvos como Imagem)
# =======================
# Esta seção gera gráficos que não dependem dos filtros do usuário
# e os salva como arquivos de imagem para download.

# 1. Gráfico de Processos por Tribunal
df_tribunal = df["Tribunal"].dropna().value_counts()
fig_trib, ax_trib = plt.subplots(figsize=(10, 5))
sns.barplot(x=df_tribunal.index, y=df_tribunal.values, ax=ax_trib)
ax_trib.set_title("Quantidade de Processos por Tribunal")
ax_trib.set_xlabel("Tribunal")
ax_trib.set_ylabel("Quantidade")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
fig_trib.savefig("processos_por_tribunal.png")
plt.close(fig_trib)

# 2. Gráfico de Processos por Período (Mensal)
df_time = df.dropna(subset=["Dat. preenchimento"]).groupby(df["Dat. preenchimento"].dt.to_period("M")).size()
df_time.index = df_time.index.to_timestamp()
period_labels = df_time.index.strftime("%Y-%m")

fig_per, ax_per = plt.subplots(figsize=(12, 6))
sns.barplot(x=period_labels, y=df_time.values, ax=ax_per)
ax_per.set_title("Quantidade de Processos por Período (Mês/Ano)")
ax_per.set_xlabel("Período (YYYY-MM)")
ax_per.set_ylabel("Quantidade")
plt.xticks(rotation=90)
plt.tight_layout()
fig_per.savefig("processos_por_periodo.png")
plt.close(fig_per)

# =======================
# Interface Interativa do Streamlit
# =======================
st.title("📊 Análise de Processos por Tribunal")

# -- Filtros na Barra Lateral --
st.sidebar.header("Filtros")

# Filtro 1: Seleção de Tribunal (com opção "TODOS")
tribunais_disponiveis = sorted(df["Tribunal"].dropna().unique().tolist())
opcoes_tribunais = ["TODOS OS TRIBUNAIS"] + tribunais_disponiveis
tribunal_selecionado = st.sidebar.selectbox("Selecione o Tribunal:", opcoes_tribunais)

# Filtro 2: Seleção de Período (Datas)
# Determina as datas mínima e máxima com base nos dados do tribunal selecionado
if tribunal_selecionado == "TODOS OS TRIBUNAIS":
    dates_selection = df["Dat. preenchimento"].dropna()
else:
    mask_trib = df["Tribunal"] == tribunal_selecionado
    dates_selection = df.loc[mask_trib, "Dat. preenchimento"].dropna()

if not dates_selection.empty:
    min_date = dates_selection.min().date()
    max_date = dates_selection.max().date()
else:
    # Se não houver datas no dataset, usa o dia de hoje
    today = pd.Timestamp.today().date()
    min_date, max_date = today, today

periodo = st.sidebar.date_input(
    "Selecione o período (início e fim):",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    key="periodo"
)

# Garante que o período selecionado tenha data de início e fim
if len(periodo) == 2:
    inicio, fim = pd.to_datetime(periodo[0]), pd.to_datetime(periodo[1])
else:
    # Fallback caso o date_input retorne apenas um dia
    inicio = fim = pd.to_datetime(periodo[0])

# -- Aplicação dos Filtros --
# Filtra o dataframe com base na seleção do usuário
if tribunal_selecionado == "TODOS OS TRIBUNAIS":
    df_filtrado = df[
        (df["Dat. preenchimento"].notna()) &
        (df["Dat. preenchimento"] >= inicio) &
        (df["Dat. preenchimento"] <= fim)
    ].copy()
else:
    df_filtrado = df[
        (df["Tribunal"] == tribunal_selecionado) &
        (df["Dat. preenchimento"].notna()) &
        (df["Dat. preenchimento"] >= inicio) &
        (df["Dat. preenchimento"] <= fim)
    ].copy()


st.write(f"### Total de registros para **{tribunal_selecionado}** de **{inicio.strftime('%d/%m/%Y')}** até **{fim.strftime('%d/%m/%Y')}**: **{len(df_filtrado)}**")

# -- Função para Gerar Gráficos --
def plot_count_horizontal(dataframe, coluna, title, topn=None):
    """Função para criar e exibir um gráfico de barras horizontal."""
    if dataframe.empty or coluna not in dataframe.columns:
        st.warning(f"Nenhum registro encontrado para '{coluna}' com os filtros aplicados.")
        return

    s = dataframe[coluna].dropna().value_counts()
    if s.empty:
        st.info(f"Não há dados disponíveis na coluna '{coluna}' para o período selecionado.")
        return

    if topn:
        s = s.head(topn)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=s.values, y=s.index, ax=ax, orient='h')
    ax.set_title(title, fontsize=16)
    ax.set_xlabel("Quantidade", fontsize=12)
    ax.set_ylabel("") # O label do eixo y já são os nomes das categorias
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# -- Exibição dos Gráficos Dinâmicos --
st.markdown("---")
st.header("Análises Detalhadas")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 15 Municípios")
    plot_count_horizontal(df_filtrado, "Município", "Top 15 Municípios por Nº de Processos", topn=15)

    st.subheader("Top 15 Assuntos Principais")
    plot_count_horizontal(df_filtrado, "Assunto Principal do Processo", "Top 15 Assuntos por Nº de Processos", topn=15)

with col2:
    st.subheader("Classes de Processo")
    plot_count_horizontal(df_filtrado, "Classe do Processo", "Distribuição por Classe do Processo")

    st.subheader("Top 15 Unidades")
    plot_count_horizontal(df_filtrado, "Unidade", "Top 15 Unidades por Nº de Processos", topn=15)


# -- Seção de Download dos Gráficos Estáticos --
st.markdown("---")
st.header("Download de Gráficos Gerais")
st.write("Faça o download dos gráficos que mostram a visão geral de todos os dados, sem filtros.")

col_dl1, col_dl2 = st.columns(2)

with col_dl1:
    with open("processos_por_tribunal.png", "rb") as f:
        st.download_button(
            label="⬇️ Baixar Processos por Tribunal",
            data=f,
            file_name="processos_por_tribunal.png",
            mime="image/png"
        )
    st.image("processos_por_tribunal.png")

with col_dl2:
    with open("processos_por_periodo.png", "rb") as f:
        st.download_button(
            label="⬇️ Baixar Processos por Período",
            data=f,
            file_name="processos_por_periodo.png",
            mime="image/png"
        )
    st.image("processos_por_periodo.png")

