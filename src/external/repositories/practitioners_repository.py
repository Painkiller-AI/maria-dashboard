import datetime
from typing import Any

from sqlalchemy import bindparam, text

from external.database.connection import db_connection


class PractitionersRepository:
    async def practitioners_info(
        self,
        *,
        tenant_id: str,
        organization_id: list[str] | None = None,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> list[dict[str, Any]] | None:
        async with db_connection.session() as session:
            filters_ca = ["p.care_team_id = ctp.care_team_id"]
            filters_hs = ["p.care_team_id = ctp.care_team_id"]
            params = {}

            if tenant_id:
                filters_ca.append("ca.tenant_id = :tenant_id")
                filters_hs.append("hs.tenant_id = :tenant_id")
                params["tenant_id"] = tenant_id

            if organization_id:
                filters_ca.append("ou.organization_id IN :organization_id")
                filters_hs.append("ou.organization_id IN :organization_id")
                params["organization_id"] = organization_id

            if start_date:
                filters_ca.append("ca.start_at >= :start_date")
                filters_hs.append("hs.created_at >= :start_date")
                params["start_date"] = start_date

            if end_date:
                filters_ca.append("ca.start_at <= :end_date")
                filters_hs.append("hs.created_at <= :end_date")
                params["end_date"] = end_date

            where_clause_ca = " AND ".join(filters_ca) if filters_ca else "1=1"
            where_clause_hs = " AND ".join(filters_hs) if filters_hs else "1=1"

            query = text(f"""
                SELECT DISTINCT
                    ca.practitioner_id,
                    CONCAT(hup2.first_name, ' ', hup2.last_name) AS practitioner_name,
                    ctp.role AS care_team_role
                FROM calendar_appointment ca
                JOIN patients p ON p.id = ca.patient_id
                JOIN human_users hup1 ON hup1.id = p.id
                JOIN users u ON u.id = p.id
                JOIN organizations_users ou ON ou.user_id = u.id
                JOIN organizations o ON o.id::text = ou.organization_id::text
                LEFT JOIN human_users hup2 ON hup2.id = ca.practitioner_id
                LEFT JOIN care_team_practitioners ctp ON ctp.practitioner_id = hup2.id
                LEFT JOIN tenants t ON t.id = ca.tenant_id
                WHERE {where_clause_ca}

                UNION

                SELECT DISTINCT
                    hs.practitioner_id,
                    CONCAT(hup2.first_name, ' ', hup2.last_name) AS practitioner_name,
                    ctp.role AS care_team_role
                FROM healthcare_service hs
                JOIN patients p ON p.id = hs.patient_id
                JOIN human_users hup1 ON hup1.id = p.id
                JOIN users u ON u.id = p.id
                JOIN organizations_users ou ON ou.user_id = u.id
                JOIN organizations o ON o.id::text = ou.organization_id::text
                LEFT JOIN human_users hup2 ON hup2.id = hs.practitioner_id
                LEFT JOIN care_team_practitioners ctp ON ctp.practitioner_id = hup2.id
                LEFT JOIN tenants t ON t.id = hs.tenant_id
                WHERE {where_clause_hs}
            """)
            if organization_id:
                query = query.bindparams(bindparam("organization_id", expanding=True))
            result = await session.execute(query, params)
            rows = result.mappings().all()
            data = [dict(row) for row in rows]
            return data
