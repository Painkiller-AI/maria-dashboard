import streamlit as st

from external.gateways.maria_api_gateway import MariaApiGateway
from external.repositories.tenants_repository import TenantsRepository
from state import app_state


async def login_page():
    st.title("🔐 Login")

    tenants_repository = TenantsRepository()
    tenants = await tenants_repository.list_tenants()

    tenant_domain = st.selectbox("Tenant", options=[tenant["domain"] for tenant in tenants])
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
