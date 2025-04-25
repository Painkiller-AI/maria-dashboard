import asyncio

import streamlit as st

from state import app_state
from ui.pages.login import login_page
from ui.pages.patients_overview import patients_overview_page


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
        await patients_overview_page()


if __name__ == "__main__":
    asyncio.run(main())
