import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from st_aggrid import AgGrid, GridOptionsBuilder



ACCESS_CODE = st.secrets["app"]["access_code"]

st.title("Consulta de Planilha Protegida")


user_code = st.text_input("Digite o código de acesso:", type="password")

if user_code == ACCESS_CODE:
    st.success("Acesso liberado.")

    try:
   
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["GOOGLE_CREDENTIALS"],
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
        )
    except Exception as e:
        st.error(f"Erro ao carregar credenciais: {e}")
        st.stop()

    sheet_link_or_id = st.text_input("Cole o link ou ID da planilha do Google Sheets:")

    if sheet_link_or_id:
   
        if "docs.google.com" in sheet_link_or_id:
            try:
                sheet_id = sheet_link_or_id.split("/d/")[1].split("/")[0]
            except:
                st.error("Link da planilha inválido.")
                st.stop()
        else:
            sheet_id = sheet_link_or_id

        try:
        
            service = build("sheets", "v4", credentials=credentials)
            sheet = service.spreadsheets()

            metadata = sheet.get(spreadsheetId=sheet_id).execute()
            sheet_titles = [s["properties"]["title"] for s in metadata["sheets"]]

            aba_escolhida = st.selectbox("Escolha a aba da planilha:", sheet_titles)

 
            range_name = f"{aba_escolhida}!A1:Z1000"

            result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
            values = result.get("values", [])

            if not values:
                st.warning("A aba está vazia ou o intervalo está incorreto.")
            else:
                df = pd.DataFrame(values[1:], columns=values[0])

                termo = st.text_input("Digite a palavra para buscar:")

                if termo:
                    resultado = df[df.apply(lambda row: row.astype(str).str.contains(termo, case=False).any(), axis=1)]
                    if resultado.empty:
                        st.info("Nenhum resultado encontrado.")
                    else:
                        st.dataframe(resultado)

        except Exception as e:
            st.error(f"Erro ao acessar a planilha: {e}")

