from datetime import datetime
from typing import Optional


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


def obter_numero_mes(
    mes_selecionado: str, meses: dict[str, int]
) -> int:  # Usando 'dict' para tipagem nativa
    return meses[mes_selecionado]


def calcular_idade(birth_date: Optional[datetime]) -> Optional[int]:
    if birth_date is None:
        return None

    data_atual = datetime.now()
    idade = data_atual.year - birth_date.year
    if (data_atual.month, data_atual.day) < (birth_date.month, birth_date.day):
        idade -= 1

    return idade
