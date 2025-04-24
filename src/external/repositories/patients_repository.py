from typing import Any

from sqlalchemy import text

from external.database.connection import db_connection


class PatientsRepository:
    async def count_patients(self, *, tenant_id: str) -> int | None:
        async with db_connection.session() as session:
            query = text("""
            SELECT COUNT(p.id) 
            FROM patients p 
            JOIN users u ON p.id = u.id
            WHERE u.tenant_id = :tenant_id       
            """)

            result = await session.execute(query, {"tenant_id": tenant_id})
            data = result.scalar()

            return data

    async def patients_info(
        self, *, tenant_id: str | None = None, organization_id: str | None = None
    ) -> list[dict[str, Any]] | None:
        async with db_connection.session() as session:
            filters = []
            params = {}

            if tenant_id:
                filters.append("u.tenant_id = :tenant_id")
                params["tenant_id"] = tenant_id

            if organization_id:
                filters.append("ct.organization_id = :organization_id")
                filters.append("ou.organization_id = :organization_id")
                params["organization_id"] = organization_id

            where_clause = " AND ".join(filters) if filters else "1=1"

            query = text(f"""
                SELECT p.id, u.created_at, p.aboard_at, MAX(cm.created_at) AS last_message_date, ou.organization_id, t.domain
                FROM patients p
                JOIN users u ON u.id = p.id
                JOIN organizations_users ou ON ou.user_id = p.id
                INNER JOIN chat_messages cm ON p.id = cm.user_id
                INNER JOIN care_teams ct ON p.care_team_id = ct.id
                left join tenants t on t.id = u.tenant_id
                WHERE {where_clause}
                GROUP BY p.id, u.created_at, p.aboard_at, ou.organization_id, t.domain;
            """)

            result = await session.execute(query, params)
            rows = result.mappings().all()
            data = [dict(row) for row in rows]
            return data

    async def patients_score(
        self, *, tenant_id: str | None = None, organization_id: str | None = None
    ) -> list[dict[str, Any]] | None:
        async with db_connection.session() as session:
            filters = ["n.score IS NOT NULL"]
            params = {}

            if tenant_id:
                filters.append("n.tenant_id = :tenant_id")
                params["tenant_id"] = tenant_id

            if organization_id:
                filters.append("ou.organization_id = :organization_id")
                params["organization_id"] = organization_id

            where_clause = " AND ".join(filters) if filters else "1=1"

            query = text(f"""
            SELECT n.score,
            n.created_at,
            ou.organization_id,
            t.domain
           FROM nps n
             LEFT JOIN organizations_users ou ON ou.user_id = n.patient_id
             LEFT JOIN tenants t ON n.tenant_id = t.id
          WHERE {where_clause};
            """)

            result = await session.execute(query, params)
            rows = result.mappings().all()
            data = [dict(row) for row in rows]
            return data

    async def patients_risk_group(
        self, *, tenant_id: str | None = None, organization_id: str | None = None
    ) -> list[dict[str, Any]] | None:
        async with db_connection.session() as session:
            filters = []
            params = {}

            if tenant_id:
                filters.append("t.id = :tenant_id")
                params["tenant_id"] = tenant_id

            if organization_id:
                filters.append("ou.organization_id = :organization_id")
                params["organization_id"] = organization_id

            where_clause = " AND ".join(filters) if filters else "1=1"

            query = text(f"""
                select
                    distinct on
                    (cpp.patient_id) cpp.patient_id,
                    cp.name as risk_group,
                    ou.organization_id,
                    t.domain
                from
                    public.care_plan_patients cpp
                join public.care_plans cp on
                    cpp.care_plan_id = cp.id
                join organizations_users ou on
                    ou.user_id = cpp.patient_id
                join tenants t on
                    cpp.tenant_id = t.id
                where
                    {where_clause}
                order by
                    cpp.patient_id,
                    cpp.created_at desc;
                        """)

            result = await session.execute(query, params)
            rows = result.mappings().all()
            data = [dict(row) for row in rows]
            return data
