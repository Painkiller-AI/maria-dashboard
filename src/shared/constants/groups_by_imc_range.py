groups_by_imc_range = {
    (40, float("inf")): [
        "OBESIDADE GRAU 3",
        "-OBESIDADE GRAU 2",
        "-OBESIDADE GRAU 1",
        "-SOBREPESO",
    ],
    (35, 40): [
        "OBESIDADE GRAU 2",
        "-OBESIDADE GRAU 3",
        "-OBESIDADE GRAU 1",
        "-SOBREPESO",
    ],
    (30, 35): [
        "OBESIDADE GRAU 1",
        "-OBESIDADE GRAU 3",
        "-OBESIDADE GRAU 2",
        "-SOBREPESO",
    ],
    (25, 30): [
        "SOBREPESO",
        "-OBESIDADE GRAU 3",
        "-OBESIDADE GRAU 2",
        "-OBESIDADE GRAU 1",
    ],
    (0, 25): [
        "-SOBREPESO",
        "-OBESIDADE GRAU 3",
        "-OBESIDADE GRAU 2",
        "-OBESIDADE GRAU 1",
    ],
}
