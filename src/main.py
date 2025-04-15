import asyncio
import streamlit as st
from ui.pages.patients_overview import patients_overview_page





async def main():
    st.set_page_config(page_title="Maria Dashboard", layout="centered", page_icon="assets/maria-logo.svg",)

    st.sidebar.title("Maria Saúde - Dashboard")
    st.sidebar.markdown("Use o menu acima para navegar.")

    await patients_overview_page()

if __name__ == "__main__":
    asyncio.run(main())