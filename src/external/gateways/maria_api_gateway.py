from httpx import AsyncClient

from settings import get_settings
from shared.schemas.user_profile_schema import UserProfileSchema

settings = get_settings()


class MariaApiGateway:
    async def login(self, *, tenant_domain: str, email: str, password: str) -> UserProfileSchema:
        async with AsyncClient() as http:
            # Login
            login_response = await http.post(
                f"{settings.MARIA_API_URL}/login",
                json={"email": email, "password": password},
                headers={"X-Tenant-Domain": tenant_domain},
                timeout=10,
            )
            login_response.raise_for_status()
            login_data = login_response.json()

            token = login_data.get("access_token")

            # Get user data
            profile_response = await http.get(
                f"{settings.MARIA_API_URL}/staff/status",
                headers={
                    "X-Tenant-Domain": tenant_domain,
                    "Authorization": f"Bearer {token}",
                },
                timeout=10,
            )
            profile_response.raise_for_status()
            profile_data = profile_response.json()

            user_profile = UserProfileSchema(**profile_data)

            if not user_profile.active or user_profile.role.name != "Administrador Geral":
                raise Exception("Você não tem permissão para acessar o sistema.")

            return user_profile
