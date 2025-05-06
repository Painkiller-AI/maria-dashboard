from typing import Any

from sqlalchemy import text

from external.database.connection import db_connection


class OrganizationRepository:
    async def list_organization(
        self,
        *,
        tenant_id: str,
    ) -> list[dict[str, Any]] | None:
        async with db_connection.session() as session:
            filters = []
            params = {}

            if tenant_id:
                filters.append("o.tenant_id = :tenant_id")
                params["tenant_id"] = tenant_id

            where_clause = " AND ".join(filters) if filters else "1=1"

            query = text(f"""
            select
                o.id AS organization_id,
                o.name AS organization_name,
                o.tenant_id
            from
                organizations o
            where {where_clause};
            """)

            result = await session.execute(query, params)
            rows = result.mappings().all()
            data = [dict(row) for row in rows]
            return data
