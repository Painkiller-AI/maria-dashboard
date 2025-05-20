import datetime
from typing import Any

from sqlalchemy import bindparam, text

from external.database.connection import db_connection


class PatientsRepository:
    async def patients_info(
        self,
        *,
        tenant_id: str,
        organization_id: list[str],
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> list[dict[str, Any]] | None:
        async with db_connection.session() as session:
            filters = []
            params = {}

            if tenant_id:
                filters.append("u.tenant_id = :tenant_id")
                params["tenant_id"] = tenant_id

            if organization_id:
                filters.append("ct.organization_id IN :organization_id")
                filters.append("ou.organization_id IN :organization_id")
                params["organization_id"] = organization_id

            if start_date:
                filters.append("u.created_at >= :start_date")
                params["start_date"] = start_date

            if end_date:
                filters.append("u.created_at <= :end_date")
                params["end_date"] = end_date

            where_clause = " AND ".join(filters) if filters else "1=1"

            query = text(f"""
            select
                CONCAT (hu.first_name,
                ' ',
                hu.last_name) as full_name,
                hu.email,
                hu.phone,
                hu.gender,
                hu.birth_date,
                p.id,
                u.created_at,
                p.aboard_at,
                MAX(cm.created_at) as last_message_date,
                ou.organization_id,
                org.name as organization_name,
                t.domain
            from
                patients p
            join human_users hu
                            on
                p.id = hu.id
            join users u on
                u.id = p.id
            join organizations_users ou on
                ou.user_id = p.id
            left join organizations org on
                ou.organization_id = org.id
            left join chat_messages cm on
                p.id = cm.user_id
            left join care_teams ct on
                p.care_team_id = ct.id
            left join tenants t on
                t.id = u.tenant_id
            where {where_clause}
            group by
            hu.first_name,
            hu.last_name,
            hu.email,
            hu.phone,
            hu.gender,
            hu.birth_date,
            p.id,
            u.created_at,
            p.aboard_at,
            ou.organization_id,
            org.name,
            t.domain;
            """)

            if organization_id:
                query = query.bindparams(bindparam("organization_id", expanding=True))

            result = await session.execute(query, params)
            rows = result.mappings().all()
            data = [dict(row) for row in rows]
            return data

    async def patients_score(
        self,
        *,
        tenant_id: str,
        organization_id: list[str] | None = None,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> list[dict[str, Any]] | None:
        async with db_connection.session() as session:
            filters = ["n.score IS NOT NULL"]
            params = {}

            if tenant_id:
                filters.append("n.tenant_id = :tenant_id")
                params["tenant_id"] = tenant_id

            if organization_id:
                filters.append("ou.organization_id IN :organization_id")
                params["organization_id"] = organization_id

            if start_date:
                filters.append("n.created_at >= :start_date")
                params["start_date"] = start_date

            if end_date:
                filters.append("n.created_at <= :end_date")
                params["end_date"] = end_date

            where_clause = " AND ".join(filters) if filters else "1=1"

            query = text(f"""
            SELECT n.score,
            n.created_at,
            ou.organization_id,
            org.name as organization_name,
            t.domain
           FROM nps n
             LEFT JOIN organizations_users ou ON ou.user_id = n.patient_id
              LEFT JOIN organizations org ON ou.organization_id = org.id
             LEFT JOIN tenants t ON n.tenant_id = t.id
          WHERE {where_clause};
            """)

            if organization_id:
                query = query.bindparams(bindparam("organization_id", expanding=True))

            result = await session.execute(query, params)
            rows = result.mappings().all()
            data = [dict(row) for row in rows]
            return data

    async def patients_risk_group(
        self,
        *,
        tenant_id: str,
        organization_id: list[str] | None = None,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> list[dict[str, Any]] | None:
        async with db_connection.session() as session:
            filters = ["lcp.rn = 1"]
            params = {}

            if tenant_id:
                filters.append("lcp.tenant_id = :tenant_id")
                params["tenant_id"] = tenant_id

            if organization_id:
                filters.append("ou.organization_id IN :organization_id")
                params["organization_id"] = organization_id

            if start_date:
                filters.append("lcp.created_at >= :start_date")
                params["start_date"] = start_date

            if end_date:
                filters.append("lcp.created_at <= :end_date")
                params["end_date"] = end_date

            where_clause = " AND ".join(filters) if filters else "1=1"

            query = text(f"""
                        with latest_care_plan as (
                        select
                            cp.*,
                            cpp.patient_id as patient_id,
                            row_number() over (partition by cpp.patient_id
                        order by
                            cp.created_at desc) as rn
                        from
                            care_plan_patients cpp
                        join care_plans cp on
                            cp.id = cpp.care_plan_id

                        )

                        select
                            lcp.*,
                            ou.organization_id,
                            org.name as organization_name,
                            t.domain
                        from
                            latest_care_plan lcp
                        join organizations_users ou on
                            ou.user_id = lcp.patient_id
                        left join organizations org on
                            ou.organization_id = org.id
                        join tenants t on
                            lcp.tenant_id = t.id
                        where {where_clause};
                         
                        """)

            if organization_id:
                query = query.bindparams(bindparam("organization_id", expanding=True))

            result = await session.execute(query, params)
            rows = result.mappings().all()
            data = [dict(row) for row in rows]
            return data

    async def patients_health_group(
        self,
        *,
        tenant_id: str,
        organization_id: list[str] | None = None,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> list[dict[str, Any]] | None:
        async with db_connection.session() as session:
            filters = []
            params = {}

            if tenant_id:
                filters.append("u.tenant_id = :tenant_id")
                params["tenant_id"] = tenant_id

            if organization_id:
                filters.append("ou.organization_id IN :organization_id")
                params["organization_id"] = organization_id

            if start_date:
                filters.append("u.created_at >= :start_date")
                params["start_date"] = start_date

            if end_date:
                filters.append("u.created_at <= :end_date")
                params["end_date"] = end_date

            where_clause = " AND ".join(filters) if filters else "1=1"

            query = text(f"""
                        select
                            p.id as patient_id,
                            p.document,
                            p.aboard_at,
                            u.created_at,
                            STRING_AGG(DISTINCT hg."name", ', ') AS conditions,
                            ou.organization_id,
                            org.name as organization_name,
                            t.domain
                        from
                            patients p
                        join human_users hu on
                            p.id = hu.id
                        join users u on
                            u.id = p.id
                        join organizations_users ou on
                            ou.user_id = p.id
                        left join group_users gu on
                            gu.user_id = u.id
                        left join health_groups hg 
                        on gu.group_id = hg.id
                        left join organizations org on
                            ou.organization_id = org.id
                        left join tenants t on
                            t.id = u.tenant_id
                        where {where_clause}
                        GROUP BY
                            p.id, p.document, p.aboard_at, u.created_at, ou.organization_id, org.name, t.domain;

                         
                        """)

            if organization_id:
                query = query.bindparams(bindparam("organization_id", expanding=True))

            result = await session.execute(query, params)
            rows = result.mappings().all()
            data = [dict(row) for row in rows]
            return data

    async def patients_csat(
        self,
        *,
        tenant_id: str,
        organization_id: list[str] | None = None,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> list[dict[str, Any]] | None:
        async with db_connection.session() as session:
            filters = []
            params = {}

            if tenant_id:
                filters.append("c.tenant_id = :tenant_id")
                params["tenant_id"] = tenant_id

            if organization_id:
                filters.append("ou.organization_id IN :organization_id")
                params["organization_id"] = organization_id

            if start_date:
                filters.append("c.rated_at >= :start_date")
                params["start_date"] = start_date

            if end_date:
                filters.append("c.rated_at <= :end_date")
                params["end_date"] = end_date

            where_clause = " AND ".join(filters) if filters else "1=1"

            query = text(f"""
                        select
                            COUNT(*) as total,
                            COUNT(*) filter (
                            where c.rating = 5) as promoters,
                            COUNT(*) filter (
                            where c.rating <= 3) as detractors,
                            ROUND(
                            100.0 * (
                            COUNT(*) filter (where c.rating = 5) - 
                            COUNT(*) filter (where c.rating <= 3)
                            ) / nullif(COUNT(*), 0),
                            2
                        ) as result
                        from
                            csat c
                        join organizations_users ou on
                            ou.user_id = c.patient_id
                        where {where_clause};
                        """)

            if organization_id:
                query = query.bindparams(bindparam("organization_id", expanding=True))

            result = await session.execute(query, params)
            rows = result.mappings().all()
            data = [dict(row) for row in rows]
            return data
