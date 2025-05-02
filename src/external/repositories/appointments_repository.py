from typing import Any

from sqlalchemy import text

from external.database.connection import db_connection


class AppointmentsRepository:
    async def video_appointments(
        self, *, tenant_id: str | None = None, organization_id: str | None = None
    ) -> list[dict[str, Any]] | None:
        async with db_connection.session() as session:
            filters = []
            params = {}

            if tenant_id:
                filters.append("ca.tenant_id = :tenant_id")
                params["tenant_id"] = tenant_id

            if organization_id:
                filters.append("ou.organization_id = :organization_id")
                params["organization_id"] = organization_id

            where_clause = " AND ".join(filters) if filters else "1=1"

            query = text(f"""
         SELECT DISTINCT ca.id AS appointment_id,
            concat(hup1.first_name, ' ', hup1.last_name) AS patient_name,
            p.document AS patient_document,
            concat(hup2.first_name, ' ', hup2.last_name) AS practitioner_name,
            ctp.role AS care_team_role,
            ca.created_at,
            ca.start_at,
            round(EXTRACT(epoch FROM ca.start_at - ca.created_at) / 3600::numeric, 0)::integer AS diff_hours,
            (EXTRACT(epoch FROM ca.start_at - ca.created_at) / 3600::numeric) <= 72::numeric AS within_72h,
            ou.organization_id,
            o.name AS organization_name,
            ca.status,
            t.domain
           FROM calendar_appointment ca
             JOIN patients p ON p.id = ca.patient_id
             JOIN human_users hup1 ON hup1.id = p.id
             JOIN users u ON u.id = p.id
             JOIN organizations_users ou ON ou.user_id = u.id
             JOIN organizations o ON o.id::text = ou.organization_id::text
             LEFT JOIN human_users hup2 ON hup2.id = ca.practitioner_id
             LEFT JOIN care_team_practitioners ctp ON ctp.practitioner_id = hup2.id
             LEFT JOIN tenants t ON t.id = ca.tenant_id
            WHERE {where_clause}
            ORDER BY (round(EXTRACT(epoch FROM ca.start_at - ca.created_at) / 3600::numeric, 0)::integer);
            """)

            result = await session.execute(query, params)
            rows = result.mappings().all()
            data = [dict(row) for row in rows]
            return data
