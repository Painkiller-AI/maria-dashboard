from shared.constants.groups_by_imc_range import groups_by_imc_range
from shared.utils.calculate_imc import calculate_imc


def get_imc_groups(height: int, weight: float) -> list[str]:
    groups = []

    imc = calculate_imc(height=height, weight=weight)

    if imc is None:
        return groups

    for (lower, upper), t in groups_by_imc_range.items():
        if lower <= imc < upper:
            groups.extend(t)
            break

    return groups
