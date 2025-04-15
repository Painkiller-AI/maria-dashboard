import re
from unicodedata import normalize


class StringFormatter:
    @staticmethod
    def format_cpf(cpf: str) -> str:
        """
        Formats a string of digits into a CPF format (xxx.xxx.xxx-xx).
        """
        cpf = re.sub(r"[^\d]", "", cpf)

        if len(cpf) != 11:
            raise ValueError("CPF must have 11 digits.")

        formatted_cpf = re.sub(r"(\d{3})(\d{3})(\d{3})(\d{2})", r"\1.\2.\3-\4", cpf)

        return formatted_cpf

    @staticmethod
    def zfill_format_cpf(cpf: str) -> str:
        """
        Formats a string of digits into a CPF format (xxx.xxx.xxx-xx) and pads with zeros if necessary.
        """
        cpf = re.sub(r"[^\d]", "", cpf)
        if len(cpf) == 0:
            raise ValueError("CPF must have digits.")
        cpf = cpf.zfill(11)
        return re.sub(r"(\d{3})(\d{3})(\d{3})(\d{2})", r"\1.\2.\3-\4", cpf)

    @staticmethod
    def clean_cpf(cpf: str) -> str:
        """
        Removes any formatting from a CPF, returning only the digits.
        """
        return re.sub(r"[^\d]", "", cpf)

    @staticmethod
    def normalize_float_str(value: str) -> str:
        """
        Normalizes a string to a float format by removing any non-numeric characters
        and replacing commas with dots.
        """
        return re.sub(r"[^(\d\.)]", "", value.strip().replace(",", "."))

    @staticmethod
    def unaccent(text: str) -> str:
        return normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII")

    @staticmethod
    def sluggerize(text: str) -> str:
        return StringFormatter.unaccent(text.replace(" ", "").lower())
