import asyncio

import streamlit as st

from ui.pages.patients_overview import patients_overview_page


async def main():
    st.set_page_config(
        page_title="Maria Dashboard",
        layout="wide",
        page_icon="assets/maria-logo.svg",
    )

    st.sidebar.title("Maria Saúde - Dashboard")

    await patients_overview_page()


if __name__ == "__main__":
    asyncio.run(main())
