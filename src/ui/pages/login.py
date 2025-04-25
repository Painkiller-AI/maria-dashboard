import streamlit as st

from external.gateways.maria_api_gateway import MariaApiGateway
from external.repositories.tenants_repository import TenantsRepository
from state import app_state


async def login_page():
    cola, colb, colc = st.columns(3)
    with colb:
        with open("assets/maria-logo.svg", "r") as f:
            svg = f.read()

        # Insere o SVG + texto "Login" lado a lado
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 24px;">
                <div style="display: flex; align-items: center; height: 40px;">{svg}</div>
                <h2 style="margin: 0; display: flex; align-items: center; height: 40px;">Login</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tenants_repository = TenantsRepository()
        tenants = await tenants_repository.list_tenants()

        tenant_domain = st.selectbox("Empresa", options=[tenant["domain"] for tenant in tenants])
        email = st.text_input("E-mail")
        password = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            try:
                maria_api = MariaApiGateway()
                user = await maria_api.login(
                    tenant_domain=tenant_domain,
                    email=email,
                    password=password,
                )
                app_state.user = user
                st.success("Login realizado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao fazer login: {e}")
