import pandas as pd


def calculate_nps(
    df: pd.DataFrame,
) -> tuple[int, float, float, float] | None:
    """
    Calcula o NPS (Net Promoter Score) baseado nas notas de NPS fornecidas em um DataFrame.

    Parâmetros:
        df (pd.DataFrame): DataFrame contendo a coluna 'nps_score' com as notas de NPS dos clientes.

    Retorno:
        tuple: Retorna uma tupla com:
            - NPS (int): O valor calculado do NPS
            - Percenteagem de promotores (float)
            - Percenteagem de detratores (float)
            - Percenteagem de neutros (float)
    """
    try:
        detratores = df[df["score"] <= 6]
        neutros = df[(df["score"] >= 7) & (df["score"] <= 8)]
        promotores = df[df["score"] >= 9]

        total = len(df)
        perc_detratores = len(detratores) / total * 100
        perc_promotores = len(promotores) / total * 100
        perc_neutros = len(neutros) / total * 100

        nps = perc_promotores - perc_detratores
        return (
            round(nps),
            round(perc_promotores, 1),
            round(perc_detratores, 1),
            round(perc_neutros, 1),
        )

    except Exception as e:
        print(f"Erro ao tentar calcular NPS: {e}")
        return None
