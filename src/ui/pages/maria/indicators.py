import locale

import pandas as pd
import plotly.express as px
import streamlit as st

from external.repositories.appointments_repository import AppointmentsRepository
from external.repositories.orgazination_repository import OrganizationRepository
from external.repositories.patients_repository import PatientsRepository
from external.repositories.tenants_repository import TenantsRepository
from shared.utils.get_datetime import calcular_idade
from state import app_state

locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")


async def indicators_page():
    st.title("📊 Indicadores Maria Saúde")
    tenant_domain = "maria-saude"

    if app_state.user:
        st.success(f"Bem-vindo, {app_state.user.full_name}")

        tenants_repository = TenantsRepository()
        patients_repository = PatientsRepository()
        appointments_repository = AppointmentsRepository()
        orgazination_repository = OrganizationRepository()
        orgazination = await orgazination_repository.list_organization(
            tenant_id=app_state.user.tenant_id,
        )
        organization_df = pd.DataFrame(orgazination)

        tenant = await tenants_repository.get_tenant(by="id", value=app_state.user.tenant_id)

        if tenant and tenant["domain"] != tenant_domain:
            st.error("Acesso negado. Você não tem permissão para acessar esta página.")
            return

        excluded_orgs = {"Cortesia", "Lazy Org", "Gabriel Teste de Organização"}
        organization_list = sorted(
            set(organization_df["organization_name"].unique()) - excluded_orgs
        )

        col_filter1, col_filter2, col_filter3, col_filter4, col_filter5, col_filter6 = st.columns(6)
        with col_filter1:
            organization_options = ["Todas"] + organization_list
            selected_org = st.selectbox(
                "Selecione a Organização",
                options=organization_options,
                index=0,
            )
            if selected_org != "Todas":
                selected_org_ids = organization_df[
                    organization_df["organization_name"] == selected_org
                ]["organization_id"].tolist()
            else:
                selected_org_ids = organization_df["organization_id"].unique().tolist()

        with col_filter2:
            selected_date_range = st.date_input(
                "Selecione o Intervalo de Datas",
                value=(pd.to_datetime("2023-01-01").date(), pd.to_datetime("today").date()),
                min_value=pd.to_datetime("2023-01-01").date(),
                max_value=pd.to_datetime("today").date(),
                format="DD/MM/YYYY",
            )

        if len(selected_date_range) == 2:
            start_date, end_date = selected_date_range
        else:
            start_date = selected_date_range[0]
            end_date = pd.to_datetime("today").date()

        patients = await patients_repository.patients_info(
            tenant_id=app_state.user.tenant_id,
            organization_id=selected_org_ids,
            start_date=start_date,
            end_date=end_date,
        )
        patients_df = pd.DataFrame(patients)
        score = await patients_repository.patients_score(
            tenant_id=app_state.user.tenant_id,
            organization_id=selected_org_ids,
            start_date=start_date,
            end_date=end_date,
        )
        score_df = pd.DataFrame(score)
        appointments = await appointments_repository.video_appointments(
            tenant_id=app_state.user.tenant_id,
            organization_id=selected_org_ids,
            start_date=start_date,
            end_date=end_date,
        )
        appointments_df = pd.DataFrame(appointments)
        risk = await patients_repository.patients_risk_group(
            tenant_id=app_state.user.tenant_id,
            organization_id=selected_org_ids,
            start_date=start_date,
            end_date=end_date,
        )
        chat_appointments = await appointments_repository.chat_info(
            tenant_id=app_state.user.tenant_id,
            organization_id=selected_org_ids,
            start_date=start_date,
            end_date=end_date,
        )
        chat_appointments_df = pd.DataFrame(chat_appointments)
        risk_df = pd.DataFrame(risk)
        if not appointments_df.empty:
            st.subheader("Agendamentos")
            col_a1, col_a2, col_a3, cola4 = st.columns(4)
            with col_a1:
                st.metric(
                    label="Agendamentos realizados",
                    value=f"{len(appointments_df):,}".replace(",", "."),
                    border=True,
                )

            appointments_df["created_at_date"] = pd.to_datetime(
                appointments_df["created_at"]
            ).dt.date
            all_dates = pd.DataFrame(
                {"created_at_date": pd.date_range(start=start_date, end=end_date)}
            )
            all_dates["created_at_date"] = pd.to_datetime(all_dates["created_at_date"]).dt.date

            daily_appointments = (
                appointments_df.groupby("created_at_date").size().reset_index(name="Quantidade")
            )

            daily_appointments_all_dates = all_dates.merge(
                daily_appointments, on="created_at_date", how="left"
            ).fillna(0)

            daily_appointments_all_dates["Data"] = pd.to_datetime(
                daily_appointments_all_dates["created_at_date"]
            ).dt.strftime("%d/%m/%Y")

            fig = px.area(
                daily_appointments_all_dates,
                x="Data",
                y="Quantidade",
                title="Agendamentos por Dia",
                color_discrete_sequence=px.colors.qualitative.Dark24_r,
            )

            fig.update_layout(
                xaxis=dict(
                    rangeslider=dict(visible=False),
                    tickangle=-45,
                ),
                xaxis_title="Data",
                yaxis_title="Quantidade",
            )
            with st.container(border=True):
                st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("Nenhum agendamento encontrado.")

        if not chat_appointments_df.empty:
            st.subheader("Atendimentos via Chat")
            col_c1, col_c2, col_c3, col_c4 = st.columns(4)
            with col_c1:
                st.metric(
                    label="Atendimentos via Chat realizados",
                    value=f"{len(chat_appointments_df):,}".replace(",", "."),
                    border=True,
                )
        else:
            st.warning("Nenhum atendimento via chat encontrado.")

        if not patients_df.empty:
            st.subheader("Análise Cadastral")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    label="Pessoas cadastradas",
                    value=f"{len(patients_df):,}".replace(",", "."),
                    border=True,
                )
            with col2:
                onboarding_list = patients_df[
                    (patients_df["aboard_at"].notna()) | (patients_df["last_message_date"].notna())
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
                        if len(patients_df) == 0
                        else f"{(len(risk_df) / len(patients_df) * 100):.1f} %".replace(".", ",")
                    ),
                    border=True,
                )

            st.subheader("Saúde Populacional")
            col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
            genero_pct = (
                patients_df["gender"].value_counts(normalize=True).mul(100).round(1).reset_index()
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
                    patients_df["birth_date"] = pd.to_datetime(
                        patients_df["birth_date"], format="%Y-%m-%d", errors="coerce"
                    )
                    patients_df["idade"] = patients_df["birth_date"].apply(calcular_idade)
                    if len(patients_df) == 0:
                        media_idade = "N/A"
                        idade_formatada = media_idade
                    else:
                        media_idade = patients_df["idade"].mean()
                        idade_formatada = f"{media_idade:.0f} anos"

                    st.metric(
                        label="Média de Idade",
                        value=idade_formatada,
                        border=True,
                    )

        else:
            st.warning("Nenhum paciente encontrado.")
