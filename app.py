import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from st_aggrid import AgGrid, GridOptionsBuilder


# Código secreto da equipe (altere para seu código real)
ACCESS_CODE = "suacodesecreto"

st.title("Consulta de Planilha Protegida")

# Campo de autenticação simples
user_code = st.text_input("Digite o código de acesso:", type="password")

if user_code == ACCESS_CODE:
    st.success("Acesso liberado.")

    try:
        # Carregar credenciais da conta de serviço
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["GOOGLE_CREDENTIALS"],
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
        )
    except Exception as e:
        st.error(f"Erro ao carregar credenciais: {e}")
        st.stop()

    # Inputs da planilha
    sheet_link_or_id = st.text_input("Cole o link ou ID da planilha do Google Sheets:")
    sheet_tab_name = st.text_input("Nome exato da aba (ex: Página1):")
    search_term = st.text_input("Digite a palavra para buscar:")

    if sheet_link_or_id and sheet_tab_name:
        # Extrair ID da planilha caso o usuário cole o link inteiro
        if "docs.google.com" in sheet_link_or_id:
            try:
                sheet_id = sheet_link_or_id.split("/d/")[1].split("/")[0]
            except:
                st.error("Link da planilha inválido.")
                st.stop()
        else:
            sheet_id = sheet_link_or_id  # Supõe que é só o ID

        range_name = f"{sheet_tab_name}!A1:Z1000"

        try:
            # Conectar à API
            service = build("sheets", "v4", credentials=credentials)
            sheet = service.spreadsheets()

            # Buscar dados
            result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
            values = result.get("values", [])

            if not values:
                st.warning("A planilha está vazia ou o intervalo/aba está incorreto.")
            else:
                df = pd.DataFrame(values[1:], columns=values[0])

                if search_term:
                    resultado = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
                    if resultado.empty:
                        st.info("Nenhum resultado encontrado.")
                    else:
                        st.dataframe(resultado)
                else:
                    st.info("Digite um termo para buscar.")

        except Exception as e:
            st.error(f"Erro ao acessar a planilha: {e}")
