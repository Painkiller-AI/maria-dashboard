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

    async def chat_appointments(
        self, *, tenant_id: str | None = None, organization_id: str | None = None
    ) -> list[dict[str, Any]] | None:
        async with db_connection.session() as session:
            filters = []
            params = {}

            if tenant_id:
                filters.append("hs.tenant_id = :tenant_id")
                params["tenant_id"] = tenant_id

            if organization_id:
                filters.append("ou.organization_id = :organization_id")
                params["organization_id"] = organization_id

            where_clause = " AND ".join(filters) if filters else "1=1"

            query = text(f"""
                            select
                                concat(hup1.first_name, ' ', hup1.last_name) as patient_name,
                                p.document as patient_document,
                                p.id as patient_id,
                                concat(hup2.first_name, ' ', hup2.last_name) as practitioner_name,
                                hs.practitioner_id,
                                hs.id as hs_id,
                                hs.thread_id,
                                hs.isconsultation,
                                hs.groups,
                                hs.medications,
                                hs.video_consultation,
                                hs.isdirty,
                                hs.created_at,
                                hs.updated_at,
                                hs.title,
                                hs.service_type,
                                hs.external_referral,
                                hs.transcript,
                                hs.specialty,
                                hs.medical_certificate,
                                hs.certificate_days,
                                hs.prescription,
                                hs.exam,
                                hs.outcome,
                                hs.transfer_to,
                                hs.summary,
                                hs.rating,
                                hs.rated_at,
                                ctp.role as care_team_role,
                                ou.organization_id,
                                o.name as organization_name,
                                hs.tenant_id,
                                t.domain
                            from
                                healthcare_service hs
                            join patients p on
                                p.id = hs.patient_id
                            join human_users hup1 on
                                hup1.id = p.id
                            join users u on
                                u.id = p.id
                            join organizations_users ou on
                                ou.user_id = u.id
                            join organizations o on
                                o.id::text = ou.organization_id::text
                            left join human_users hup2 on
                                hup2.id = hs.practitioner_id
                            left join care_team_practitioners ctp on
                                ctp.practitioner_id = hup2.id
                            left join tenants t on
                                t.id = hs.tenant_id
                            where {where_clause}
            """)

            result = await session.execute(query, params)
            rows = result.mappings().all()
            data = [dict(row) for row in rows]
            return data
