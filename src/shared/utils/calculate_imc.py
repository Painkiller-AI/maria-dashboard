def calculate_imc(
    *,
    height: int,
    weight: float,
) -> float | None:
    try:
        if height <= 0 or weight <= 0:
            raise ValueError()

        imc = weight / (height / 100) ** 2

        return round(imc, 2)

    except Exception:
        print(f"Error when try to calculate imc from height: {height} and weight: {weight}")
        return None
