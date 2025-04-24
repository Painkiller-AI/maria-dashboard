import streamlit as st

from external.repositories.appointments_repository import AppointmentsRepository
from external.repositories.patients_repository import PatientsRepository
from external.repositories.tenants_repository import TenantsRepository
from state import app_state


async def patients_overview_page():
    st.title("📊 CEMIG")
    organization_id = "cemig"
    tenant_domain = "maria-saude"

    if app_state.user:
        st.success(f"Bem-vindo, {app_state.user.full_name}")
        st.json(app_state.user.model_dump())

        tenants_repository = TenantsRepository()
        patients_repository = PatientsRepository()
        appointments_repository = AppointmentsRepository()

        tenant = await tenants_repository.get_tenant(by="id", value=app_state.user.tenant_id)

        if tenant and tenant["domain"] != tenant_domain:
            st.error("Acesso negado. Você não tem permissão para acessar esta página.")
            return

        patients = await patients_repository.patients_info(
            tenant_id=app_state.user.tenant_id, organization_id=organization_id
        )
        score = await patients_repository.patients_score(
            tenant_id=app_state.user.tenant_id, organization_id=organization_id
        )
        appointments = await appointments_repository.appointments(
            tenant_id=app_state.user.tenant_id, organization_id=organization_id
        )
        risk = await patients_repository.patients_risk_group(
            tenant_id=app_state.user.tenant_id, organization_id=organization_id
        )
        if patients:
            st.subheader("Pacientes encontrados:")
            st.dataframe(patients)
        else:
            st.warning("Nenhum paciente encontrado.")
        if score:
            st.subheader("Pacientes com NPS:")
            st.dataframe(score)
        else:
            st.warning("Nenhum paciente encontrado.")
        if appointments:
            st.subheader("Pacientes com consultas:")
            st.dataframe(appointments)
        if risk:
            st.subheader("Pacientes com grupo de risco:")
            st.dataframe(risk)
        else:
            st.warning("Nenhum paciente encontrado.")
