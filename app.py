import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from st_aggrid import AgGrid, GridOptionsBuilder

def autenticar_google_sheets():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    info = {
        "type": st.secrets["google_service_account"]["type"],
        "project_id": st.secrets["google_service_account"]["project_id"],
        "private_key_id": st.secrets["google_service_account"]["private_key_id"],
        "private_key": st.secrets["google_service_account"]["private_key"].replace("\\n", "\n"),
        "client_email": st.secrets["google_service_account"]["client_email"],
        "client_id": st.secrets["google_service_account"]["client_id"],
        "auth_uri": st.secrets["google_service_account"]["auth_uri"],
        "token_uri": st.secrets["google_service_account"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["google_service_account"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["google_service_account"]["client_x509_cert_url"],
        "universe_domain": st.secrets["google_service_account"]["universe_domain"]
    }
    credentials = Credentials.from_service_account_info(info, scopes=scopes)
    client = gspread.authorize(credentials)
    return client
# --- Autenticação Google Sheets ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

# Lê o JSON do secrets.toml como string e carrega com google.oauth2
import json
creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)

# --- Sessão de senha interna da equipe ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acesso restrito")
    senha = st.text_input("Digite a senha de acesso da equipe:", type="password")
    if st.button("Entrar"):
        if senha == "minha_senha_segura":  # substitua pela sua senha real
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Senha incorreta. Tente novamente.")
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
