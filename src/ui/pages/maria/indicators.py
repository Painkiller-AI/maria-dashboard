import pandas as pd
import plotly.express as px
import streamlit as st

from external.repositories.appointments_repository import AppointmentsRepository
from external.repositories.patients_repository import PatientsRepository
from external.repositories.tenants_repository import TenantsRepository
from shared.utils.get_datetime import calcular_idade
from state import app_state


async def indicators_page():
    st.title("📊 Indicadores Maria Saúde")
    tenant_domain = "maria-saude"

    if app_state.user:
        st.success(f"Bem-vindo, {app_state.user.full_name}")

        tenants_repository = TenantsRepository()
        patients_repository = PatientsRepository()
        appointments_repository = AppointmentsRepository()

        tenant = await tenants_repository.get_tenant(by="id", value=app_state.user.tenant_id)

        if tenant and tenant["domain"] != tenant_domain:
            st.error("Acesso negado. Você não tem permissão para acessar esta página.")
            return

        patients = await patients_repository.patients_info(
            tenant_id=app_state.user.tenant_id,
        )
        patients_df = pd.DataFrame(patients)
        score = await patients_repository.patients_score(
            tenant_id=app_state.user.tenant_id,
        )
        score_df = pd.DataFrame(score)
        appointments = await appointments_repository.video_appointments(
            tenant_id=app_state.user.tenant_id,
        )
        appointments_df = pd.DataFrame(appointments)
        risk = await patients_repository.patients_risk_group(
            tenant_id=app_state.user.tenant_id,
        )
        risk_df = pd.DataFrame(risk)
        excluded_orgs = {"Cortesia", "Lazy Org"}
        organization_list = sorted(set(patients_df["organization_name"].unique()) - excluded_orgs)
        col_filter1, col_filter2, col_filter3, col_filter4, col_filter5, col_filter6 = st.columns(6)
        with col_filter1:
            organization_options = ["Todas"] + organization_list
            selected_org = st.selectbox(
                "Selecione a Organização",
                options=organization_options,
                index=0,
            )
            if selected_org != "Todas":
                filtered_patients_df = patients_df[patients_df["organization_name"] == selected_org]
                filtered_appointments_df = appointments_df[
                    appointments_df["organization_name"] == selected_org
                ]
                filtered_risk_df = risk_df[risk_df["organization_name"] == selected_org]
            else:
                filtered_patients_df = patients_df[
                    ~patients_df["organization_name"].isin(excluded_orgs)
                ]
                filtered_appointments_df = appointments_df[
                    ~appointments_df["organization_name"].isin(excluded_orgs)
                ]
                filtered_risk_df = risk_df[~risk_df["organization_name"].isin(excluded_orgs)]

        with col_filter2:
            selected_date_range = st.date_input(
                "Selecione o Intervalo de Datas",
                value=(pd.to_datetime("2023-01-01").date(), pd.to_datetime("today").date()),
                min_value=pd.to_datetime("2023-01-01").date(),
                max_value=pd.to_datetime("today").date(),
                format="DD-MM-YYYY",
            )

            if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
                start_date, end_date = selected_date_range
                filtered_patients_df = filtered_patients_df[
                    (filtered_patients_df["created_at"].dt.date >= start_date)
                    & (filtered_patients_df["created_at"].dt.date <= end_date)
                ]
                filtered_appointments_df = filtered_appointments_df[
                    (filtered_appointments_df["start_at"].dt.date >= start_date)
                    & (filtered_appointments_df["start_at"].dt.date <= end_date)
                ]
        if filtered_appointments_df is not None:
            st.subheader("Agendamentos")
            col_a1, col_a2, col_a3, cola4 = st.columns(4)
            # st.write(filtered_appointments_df)
            with col_a1:
                st.metric(
                    label="Agendamentos realizados",
                    value=f"{len(filtered_appointments_df):,}".replace(",", "."),
                    border=True,
                )
        else:
            st.warning("Nenhum agendamento encontrado.")

        if (filtered_patients_df is not None) and (filtered_risk_df is not None):
            st.subheader("Análise Cadastral")
            # st.write(filtered_patients_df)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    label="Pessoas cadastradas",
                    value=f"{len(filtered_patients_df):,}".replace(",", "."),
                    border=True,
                )
            with col2:
                onboarding_list = filtered_patients_df[
                    (filtered_patients_df["aboard_at"].notna())
                    | (filtered_patients_df["last_message_date"].notna())
                ]
                st.metric(
                    label="Pessoas com Onboarding realizado",
                    value=f"{len(onboarding_list):,}".replace(",", "."),
                    border=True,
                )
            with col3:
                st.metric(
                    label="Responderam Questionário de Risco",
                    value=(
                        "N/A"
                        if len(filtered_patients_df) == 0
                        else f"{(len(filtered_risk_df) / len(filtered_patients_df) * 100):.1f} %".replace(
                            ".", ","
                        )
                    ),
                    border=True,
                )
            st.subheader("Saúde Populacional")
            col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
            genero_pct = (
                filtered_patients_df["gender"]
                .value_counts(normalize=True)
                .mul(100)
                .round(1)
                .reset_index()
            )
            genero_pct_filtrado = genero_pct[genero_pct["gender"].isin(["male", "female"])]

            genero_pct_filtrado["gender"] = genero_pct_filtrado["gender"].replace(
                {"male": "Masculino", "female": "Feminino"}
            )
            genero_pct_filtrado.columns = ["Gênero", "Percentual"]
            with col_s1:
                with st.container(border=True):
                    st.text("Sexo Biológico")
                    fig = px.bar(
                        genero_pct_filtrado,
                        x="Percentual",
                        y="Gênero",
                        orientation="h",
                        text="Percentual",
                        color="Gênero",
                        color_discrete_sequence=px.colors.qualitative.Dark24,
                    )

                    fig.update_traces(
                        texttemplate="%{text}%", textposition="outside", marker=dict(opacity=0.8)
                    )

                    fig.update_layout(
                        xaxis_title="%",
                        yaxis_title="",
                        bargap=0.4,
                        showlegend=False,
                    )

                    st.plotly_chart(fig)
                with col_s2:
                    filtered_patients_df["birth_date"] = pd.to_datetime(
                        filtered_patients_df["birth_date"], format="%Y-%m-%d", errors="coerce"
                    )
                    filtered_patients_df["idade"] = filtered_patients_df["birth_date"].apply(
                        calcular_idade
                    )
                    if len(filtered_patients_df) == 0:
                        media_idade = "N/A"
                        idade_formatada = media_idade
                    else:
                        media_idade = filtered_patients_df["idade"].mean()
                        idade_formatada = f"{media_idade:.0f} anos"

                    st.metric(
                        label="Média de Idade",
                        value=idade_formatada,
                        border=True,
                    )

        else:
            st.warning("Nenhum paciente encontrado.")
