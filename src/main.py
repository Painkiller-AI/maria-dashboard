import asyncio

import streamlit as st

from state import app_state
from ui.pages.login import login_page
from ui.pages.maria.indicators import indicators_page

PAGES = {
    # "CEMIG - Visão Geral dos Pacientes": patients_overview_page,
    "Maria Saúde - Indicadores": indicators_page,
}


async def main():
    st.set_page_config(
        page_title="Maria Dashboard",
        layout="wide",
        page_icon="assets/maria-logo.svg",
    )

    st.sidebar.title("Maria Saúde - Dashboard")

    if not app_state.user:
        await login_page()
    else:
        st.sidebar.title("Navegação")
        selected_page = st.sidebar.radio("Escolha uma página", list(PAGES.keys()))
        await PAGES[selected_page]()


if __name__ == "__main__":
    asyncio.run(main())
