# ui/pages/01_patients_overview.py
import streamlit as st

from external.repositories.patients_repository import PatientsRepository
from external.repositories.tenants_repository import TenantsRepository


async def patients_overview_page():
    st.title("📊 Pacientes por Tenant")

    tenant_domain = st.text_input("Tenant Domain", placeholder="Digite o domínio do tenant. Ex: maria-saude, bp, test...")

    if tenant_domain:
        patients_repository = PatientsRepository()
        tenants_repository = TenantsRepository()
        tenant = await tenants_repository.get_tenant(by="domain", value=tenant_domain)
        if tenant:
            count = await patients_repository.count_patients(tenant_id=tenant["id"])

            if count is not None:
                st.success(f"Total de pacientes: {count}")
            else:
                st.warning("Nenhum paciente encontrado.")
        else:
            st.error("Tenant não encontrado.")
