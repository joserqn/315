import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Código secreto da equipe (altere para seu código real)
ACCESS_CODE = "suacodesecreto"

st.title("Consulta de Planilha Protegida")

# Campo de autenticação simples
user_code = st.text_input("Digite o código de acesso:", type="password")

if user_code == ACCESS_CODE:
    st.success("Acesso liberado.")

    try:
        creds_dict = dict(st.secrets["GOOGLE_CREDENTIALS"])

        # Verificações explícitas da private_key
        private_key = creds_dict.get("private_key")
        if not private_key:
            st.error("Erro: 'private_key' não encontrada nas credenciais.")
            st.stop()
        if "-----BEGIN PRIVATE KEY-----" not in private_key or "-----END PRIVATE KEY-----" not in private_key:
            st.error("Erro: 'private_key' parece estar mal formatada.")
            st.stop()

        # Criar credenciais
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
        )

    except Exception as e:
        st.error(f"Erro ao carregar credenciais: {e}")
        st.stop()


    # --- Acesso à planilha ---
st.title("🔎 Consulta de dados protegidos")

url = st.text_input("Cole o link da planilha do Google Sheets aqui:")

if url:
    try:
        # Extrair o ID do Google Sheets
        import re
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
        if not match:
            st.error("URL inválida. Certifique-se de colar o link correto da planilha.")
        else:
            sheet_id = match.group(1)

            # Conecta ao Google Sheets
            client = gspread.authorize(creds)
            sheet = client.open_by_key(sheet_id)

            aba = st.selectbox("Escolha a aba da planilha:", [ws.title for ws in sheet.worksheets()])
            worksheet = sheet.worksheet(aba)
            dados = worksheet.get_all_records()
            df = pd.DataFrame(dados)

            st.success("Dados carregados com sucesso!")

            # Interface com AgGrid
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_pagination(paginationAutoPageSize=True)
            gb.configure_default_column(groupable=True, editable=False)
            gridOptions = gb.build()

            AgGrid(df, gridOptions=gridOptions, fit_columns_on_grid_load=True)

    except Exception as e:
        st.error(f"Erro ao acessar a planilha: {e}")

