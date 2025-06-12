import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

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

                # Escolha colunas para busca
                colunas_para_busca = st.multiselect("Selecione as colunas para buscar:", options=df.columns, default=df.columns.tolist())

                termo = st.text_input("Digite a palavra para buscar:")

                # Limpar termo (remover espaços nas extremidades)
                termo_limpo = termo.strip()

                if termo_limpo and len(termo_limpo) > 1:  # busca só com termos relevantes (mais de 1 caractere)
                    # Filtrar nas colunas selecionadas
                    mask = df[colunas_para_busca].apply(lambda col: col.astype(str).str.contains(termo_limpo, case=False, na=False)).any(axis=1)
                    resultado = df[mask]

                    if resultado.empty:
                        st.info("Nenhum resultado encontrado.")
                    else:
                        st.dataframe(resultado)
                elif termo_limpo:
                    st.info("Digite pelo menos 2 caracteres para a busca.")
                else:
                    st.info("Digite algo para buscar na tabela.")

        except Exception as e:
            st.error(f"Erro ao acessar a planilha: {e}")
