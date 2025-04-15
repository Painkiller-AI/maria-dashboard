from typing import Literal

from sqlalchemy import text

from external.database.connection import db_connection


class TenantsRepository:
    async def get_tenant(self, *, by: Literal["id", "domain"], value: str):
        async with db_connection.session() as session:
            if by not in {"id", "domain"}:
                raise ValueError()

            query = text(f"SELECT * FROM tenants WHERE {by} = :value")

            result = await session.execute(query, {"value": value})
            data = result.mappings().fetchone()

            return data if data else None
