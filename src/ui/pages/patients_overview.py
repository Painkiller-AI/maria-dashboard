import pandas as pd
import streamlit as st

from external.repositories.appointments_repository import AppointmentsRepository
from external.repositories.patients_repository import PatientsRepository
from external.repositories.tenants_repository import TenantsRepository
from state import app_state


async def patients_overview_page():
    st.title("📊 CEMIG")
    organization_id = "cemig"
    # organization_id = None
    # organization_id_test = st.selectbox(
    #     label="Organização",
    #     options=["Todas", "cemig", "materdei", "a3data"],
    #     index=0,
    #     disabled=False,
    # )
    # org_button = st.button("Selecionar organização", key="org_button")
    # if org_button:
    #     if organization_id_test == "cemig":
    #         organization_id = "cemig"
    #     elif organization_id_test == "materdei":
    #         organization_id = "materdei"
    #     elif organization_id_test == "a3data":
    #         organization_id = "materdei"
    #     else:
    #         organization_id = None
    tenant_domain = "maria-saude"

    if app_state.user:
        st.success(f"Bem-vindo, {app_state.user.full_name}")
        with st.container(border=True):
            # st.json(app_state.user.model_dump())

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
            patients_df = pd.DataFrame(patients)

            score = await patients_repository.patients_score(
                tenant_id=app_state.user.tenant_id, organization_id=organization_id
            )
            score_df = pd.DataFrame(score)
            appointments = await appointments_repository.appointments(
                tenant_id=app_state.user.tenant_id, organization_id=organization_id
            )
            appointments_df = pd.DataFrame(appointments)
            risk = await patients_repository.patients_risk_group(
                tenant_id=app_state.user.tenant_id, organization_id=organization_id
            )
            risk_df = pd.DataFrame(risk)
            if patients:
                st.subheader("Pacientes encontrados")
                st.dataframe(patients_df)
            else:
                st.warning("Nenhum paciente encontrado.")
            if score:
                st.subheader("Pacientes com NPS:")
                st.dataframe(score_df)
            else:
                st.warning("Nenhum paciente encontrado com valor de NPS.")
            if appointments:
                st.subheader("Total de consultas agendadas por profissional")
                col1, col2, col3, col4, col5 = st.columns(5, border=False)
                with col1:
                    st.metric(
                        label="Concierge",
                        value=len([a for a in appointments if a["care_team_role"] == "concierge"]),
                        border=True,
                    )
                with col2:
                    st.metric(
                        label="Médicos",
                        value=len([a for a in appointments if a["care_team_role"] == "doctor"]),
                        border=True,
                    )
                with col3:
                    st.metric(
                        label="Psicólogos",
                        value=len(
                            appointments_df[appointments_df["care_team_role"] == "psychologist"]
                        ),
                        border=True,
                    )
                with col4:
                    st.metric(
                        label="Nutricionistas",
                        value=len(
                            appointments_df[appointments_df["care_team_role"] == "nutritionist"]
                        ),
                        border=True,
                    )
                with col5:
                    st.metric(
                        label="Enfermeiros",
                        value=len(
                            appointments_df[
                                appointments_df["care_team_role"].str.contains(
                                    "nurse", case=False, na=False
                                )
                            ]
                        ),
                        border=True,
                    )
                st.subheader("Pacientes com consultas")
                st.dataframe(appointments)
            if risk:
                st.subheader("Pacientes com grupo de risco classificado")
                st.dataframe(risk_df)
            else:
                st.warning("Nenhum paciente encontrado com grupo de risco classificado.")
