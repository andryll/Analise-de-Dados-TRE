# Análise de Dados do TRE


## Pré-requisitos

Antes de começar, garanta que você tem o Python instalado no seu sistema.

* **Python**: Você pode baixar a versão mais recente em [python.org](https://www.python.org/downloads/).
    * **IMPORTANTE (Para usuários Windows)**: Durante a instalação, marque a caixa que diz **"Add Python to PATH"**. Isso é crucial para que os comandos funcionem no terminal.

## Instalação e Configuração

Siga os passos abaixo para configurar o ambiente e instalar as dependências do projeto.

1.  **Clone ou Baixe o Repositório**

    Baixe o arquivo ZIP do repositório e extraia-o em uma pasta no seu computador.

2. **Baixar os arquivos do TRE**

    Baixe o arquivo de dados do TRE no formato .csv, renomeie para `data.csv` e mova para dentro da pasta do projeto.

3.  **Navegue até a Pasta do Projeto**

    Segure Shift e clique com o botão direito dentro da pasta do projeto e vá na opção "Abrir janela do Powershell aqui".

5.  **Instale as Dependências**
    Instale todas as bibliotecas necessárias listadas no arquivo `requirements.txt` com o comando:
    ```bash
    pip install -r requirements.txt
    ```

## Como Executar a Aplicação

Com tudo instalado, você pode iniciar o servidor web.

1.  **Inicie o Servidor**
    No terminal execute o arquivo principal da aplicação:
    ```bash
    streamlit run app.py
    ```

2.  **Acesse no Navegador**
    Após executar o comando, o terminal exibirá uma mensagem indicando que o servidor está rodando, geralmente em um endereço local. Abra seu navegador e acesse a URL fornecida.
    * Geralmente será: `http://127.0.0.1:5000` ou `http://localhost:5000`

> **Atenção**: Mantenha a janela do terminal aberta enquanto estiver usando a aplicação. Fechá-la irá encerrar o servidor.

### Como Parar a Aplicação

Para parar o servidor, volte ao terminal onde ele está rodando e pressione as teclas `Ctrl + C`.
