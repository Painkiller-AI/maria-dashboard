# ui/pages/01_patients_overview.py
import streamlit as st

from external.repositories.appointments_repository import AppointmentsRepository
from external.repositories.patients_repository import PatientsRepository
from external.repositories.tenants_repository import TenantsRepository


async def patients_overview_page():
    st.title("📊 CEMIG")

    tenant_domain = "maria-saude"
    organization_id = "cemig"
    if tenant_domain:
        patients_repository = PatientsRepository()
        tenants_repository = TenantsRepository()
        appointments_repository = AppointmentsRepository()
        tenant = await tenants_repository.get_tenant(by="domain", value=tenant_domain)
        if tenant:
            patients = await patients_repository.patients_info(
                tenant_id=tenant["id"], organization_id=organization_id
            )
            score = await patients_repository.patients_score(
                tenant_id=tenant["id"], organization_id=organization_id
            )
            appointments = await appointments_repository.appointments(
                tenant_id=tenant["id"], organization_id=organization_id
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
        else:
            st.error("Tenant não encontrado.")
