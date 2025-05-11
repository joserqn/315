import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Função para autenticar e retornar cliente gspread
def autenticar_google_sheets():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = Credentials.from_service_account_file(
        "credentials.json", scopes=scopes
    )
    client = gspread.authorize(credentials)
    return client

# Função principal
def main():
    import streamlit as st

# Função de autenticação
def autenticar():
    st.title("Acesso restrito")
    senha = st.text_input("Digite a senha de acesso", type="password")
    if senha == "9~3WaOxD&X$0":
        st.session_state["autenticado"] = True
        st.rerun()
    elif senha != "":
        st.warning("Senha incorreta.")

# Verifica se o usuário está autenticado
if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
    autenticar()
else:
    # CONTEÚDO PRINCIPAL DA APLICAÇÃO
    st.title("Consulta de Planilha")
    st.write("Bem-vindo à aplicação!")
    # (Aqui você pode colocar carregamento da planilha, filtros, buscas etc.)

    st.title("Consulta de Planilha do Google Sheets")

    planilha_id = st.text_input("Digite o ID da planilha do Google Sheets:")

    if planilha_id:
        try:
            client = autenticar_google_sheets()
            sheet = client.open_by_key(planilha_id)
            abas = sheet.worksheets()

            nomes_abas = [aba.title for aba in abas]
            aba_escolhida = st.selectbox("Escolha a aba para visualizar:", nomes_abas)

            worksheet = sheet.worksheet(aba_escolhida)
            dados = worksheet.get_all_records()
            df = pd.DataFrame(dados)

            st.success("Planilha carregada com sucesso!")
            st.dataframe(df)

        except Exception as e:
            st.error(f"Erro ao acessar a planilha: {str(e)}")

if __name__ == "__main__":
    main()
