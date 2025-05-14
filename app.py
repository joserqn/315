import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Código secreto da equipe
ACCESS_CODE = "suacodesecreto"  # ← Altere aqui

st.title("Consulta de Planilha Protegida")

# Campo de autenticação simples
user_code = st.text_input("Digite o código de acesso:", type="password")

if user_code == ACCESS_CODE:
    st.success("Acesso liberado.")

    # Carregar credenciais da conta de serviço a partir do secrets
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["GOOGLE_CREDENTIALS"],
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )

    # ID da planilha do Google Sheets (coloque o seu aqui)
    SHEET_ID = "SEU_ID_DA_PLANILHA"  # ← Ex: "1Lksd89ASDFKJlsdf..."

    # Nome da aba ou intervalo (range) desejado
    RANGE = "Página1!A1:Z1000"

    try:
        # Conectar à API
        service = build("sheets", "v4", credentials=credentials)
        sheet = service.spreadsheets()

        # Buscar dados
        result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE).execute()
        values = result.get("values", [])

        if not values:
            st.warning("Planilha vazia ou intervalo inválido.")
        else:
            # Converter para DataFrame
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

else:
    if user_code:
        st.error("Código incorreto.")
