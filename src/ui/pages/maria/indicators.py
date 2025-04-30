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
        appointments = await appointments_repository.appointments(
            tenant_id=app_state.user.tenant_id,
        )
        appointments_df = pd.DataFrame(appointments)
        risk = await patients_repository.patients_risk_group(
            tenant_id=app_state.user.tenant_id,
        )
        risk_df = pd.DataFrame(risk)

        if patients and risk:
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
                    value=f"{(len(risk_df) / len(patients_df) * 100):.1f}".replace(".", ",") + "%",
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

                    media_idade = patients_df["idade"].mean()
                    st.metric(
                        label="Média de Idade",
                        value=f"{(media_idade):.0f} anos",
                        border=True,
                    )

        else:
            st.warning("Nenhum paciente encontrado.")
