from datetime import datetime, timedelta
from typing import Optional

import pandas as pd


def obter_lista_meses() -> tuple[list[str], dict[str, int]]:
    meses = {
        "Janeiro": 1,
        "Fevereiro": 2,
        "Março": 3,
        "Abril": 4,
        "Maio": 5,
        "Junho": 6,
        "Julho": 7,
        "Agosto": 8,
        "Setembro": 9,
        "Outubro": 10,
        "Novembro": 11,
        "Dezembro": 12,
    }
    return list(meses.keys()), meses


def obter_lista_anos() -> list[int]:
    ano_atual = datetime.now().year
    return list(range(2024, ano_atual + 1))


def obter_numero_mes(mes_selecionado: str, meses: dict[str, int]) -> int:
    return meses[mes_selecionado]


def calcular_idade(birth_date: Optional[datetime]) -> Optional[int]:
    if birth_date is None:
        return None

    data_atual = datetime.now()
    idade = data_atual.year - birth_date.year
    if (data_atual.month, data_atual.day) < (birth_date.month, birth_date.day):
        idade -= 1

    return idade


def mesclar_e_filtrar_usuarios_ativos(
    df1: pd.DataFrame, df2: pd.DataFrame, dias_inatividade: int
) -> pd.DataFrame:
    colunas_comuns = ["patient_name", "patient_document", "organization_id", "created_at"]

    df1_common = df1[colunas_comuns].copy()
    df2_common = df2[colunas_comuns].copy()

    df = pd.concat([df1_common, df2_common], ignore_index=True)

    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

    df = df.sort_values(by="created_at", ascending=False)
    df = df.drop_duplicates(
        subset=["patient_name", "patient_document", "organization_id"], keep="first"
    )

    data_atual = pd.Timestamp.now()
    df["inactive_60_days"] = (data_atual - df["created_at"]) >= timedelta(days=dias_inatividade)
    df.reset_index(drop=True, inplace=True)

    return df
