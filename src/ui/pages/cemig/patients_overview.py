import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from pandas.tseries.offsets import MonthBegin, MonthEnd

from external.repositories.appointments_repository import AppointmentsRepository
from external.repositories.patients_repository import PatientsRepository
from external.repositories.tenants_repository import TenantsRepository
from shared.utils.calculate_nps import calculate_nps
from state import app_state


async def patients_overview_page():
    st.title("📊 CEMIG")
    organization_id = "cemig"
    tenant_domain = "maria-saude"
    ano = 2025
    mes = 3
    data_limite = pd.to_datetime(f"{ano}-{mes}-01") + MonthEnd(0)
    data_inicio = pd.to_datetime(f"{ano}-{mes}-01") - MonthBegin(0)

    if app_state.user:
        st.success(f"Bem-vindo, {app_state.user.full_name}")
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
        if score:
            with st.container(border=True, key="nps container"):
                st.header("Índice NPS")
                score_filtro = (score_df["created_at"].dt.year == ano) & (
                    score_df["created_at"].dt.month == mes
                )
                score_df_filtered = score_df[score_filtro]
                nps, perc_promotores, perc_detratores, perc_neutros = calculate_nps(
                    score_df_filtered
                )

                fig = go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=nps,
                        delta={"reference": 0},
                        gauge={
                            "axis": {"range": [None, 100]},
                            "bar": {"color": "black"},
                            "steps": [
                                {"range": [0, 50], "color": "red"},
                                {"range": [50, 75], "color": "yellow"},
                                {"range": [75, 100], "color": "green"},
                            ],
                        },
                    )
                )

                fig.update_layout(height=400)

                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                st.download_button(
                    label="Baixar dados do NPS",
                    data=score_df_filtered.to_csv(index=False).encode("utf-8"),
                    file_name="nps.csv",
                    mime="text/csv",
                )
        else:
            st.warning("Nenhum paciente encontrado com valor de NPS.")

        if appointments:
            with st.container(border=True, key="appointments container"):
                st.header("Índices de agendamentos")
                appointments_filtro = (appointments_df["created_at"].dt.year == ano) & (
                    appointments_df["created_at"].dt.month == mes
                )
                appointments_df_filtered = appointments_df[appointments_filtro]
                appointments_within_72h = appointments_df_filtered[
                    appointments_df_filtered["within_72h"] == True
                ]
                total_appointments = appointments_df_filtered.shape[0]
                total_appointments_within_72h = appointments_within_72h.shape[0]
                perc_appointments_within_72h = (
                    total_appointments_within_72h / total_appointments * 100
                )
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Agendamentos realizados em até 72 horas de demanda eletiva")
                    st.markdown(
                        f"**✅ Percentual em até 72h:** {perc_appointments_within_72h:.1f}%"
                    )
                    st.markdown(f"**📆 Agendamentos ≤ 72h:** {total_appointments_within_72h}")
                    st.markdown(
                        f"**📋 Total de agendamentos na competência:** {total_appointments}"
                    )
                with col2:
                    st.subheader("Taxa de absenteísmo")
                    no_show_count = appointments_df_filtered[
                        appointments_df_filtered["status"] == "no_show"
                    ].shape[0]
                    total_appointments_count = appointments_df_filtered[
                        appointments_df_filtered["status"].isin(["no_show", "completed"])
                    ].shape[0]

                    no_show_rate = (
                        (no_show_count / total_appointments_count) * 100
                        if total_appointments_count
                        else 0
                    )

                    st.markdown(f"**📉 Taxa de Faltas:** {no_show_rate:.1f}%")
                    st.markdown(f"**🚫 Total de Faltosos:** {no_show_count}")
                    st.markdown(f"**📅 Agendadas e Não Realizadas:** {total_appointments_count}")

                st.download_button(
                    label="Baixar dados de Agendamentos",
                    data=appointments_df_filtered.to_csv(index=False).encode("utf-8"),
                    file_name="appointments.csv",
                    mime="text/csv",
                )

    else:
        st.warning("Nenhum agendamento de consulta encontrado.")
