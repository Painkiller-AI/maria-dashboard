from httpx import AsyncClient

from settings import get_settings

settings = get_settings()


class MariaApiGateway:
    async def check_elegibility(self, *, tenant_domain: str, cpf: str) -> bool | None:
        async with AsyncClient() as http:
            response = await http.post(
                f"{settings.MARIA_API_URL}/eligibility/check",
                data={"document": cpf},
                headers={
                    "X-Tenant-Domain": tenant_domain,
                    "Authorization": f"Bearer {settings.MARIA_API_SUPER_TOKEN}",
                },
                timeout=10,
            )

            if response.status_code != 200:
                return None

            data = response.json()
            return data.get("eligible")
