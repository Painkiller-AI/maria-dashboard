import datetime
from typing import Any

from sqlalchemy import bindparam, text

from external.database.connection import db_connection


class AppointmentsRepository:
    async def video_appointments_info(
        self,
        *,
        tenant_id: str,
        organization_id: list[str] | None = None,
        roles: list[str] | None = None,
        practitioner_id: list[str] | None = None,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> list[dict[str, Any]] | None:
        async with db_connection.session() as session:
            filters = ["p.care_team_id = ctp.care_team_id"]
            params = {}

            if tenant_id:
                filters.append("ca.tenant_id = :tenant_id")
                params["tenant_id"] = tenant_id

            if organization_id:
                filters.append("ou.organization_id IN :organization_id")
                params["organization_id"] = organization_id

            if start_date:
                filters.append("ca.start_at >= :start_date")
                params["start_date"] = start_date

            if end_date:
                filters.append("ca.start_at <= :end_date")
                params["end_date"] = end_date

            if practitioner_id:
                filters.append("ca.practitioner_id IN :practitioner_id")
                params["practitioner_id"] = practitioner_id
            if roles:
                filters.append("ctp.role IN :roles")
                params["roles"] = roles

            where_clause = " AND ".join(filters) if filters else "1=1"

            query = text(f"""
         SELECT ca.id AS appointment_id,
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
            if organization_id:
                query = query.bindparams(bindparam("organization_id", expanding=True))
            if practitioner_id:
                query = query.bindparams(bindparam("practitioner_id", expanding=True))
            if roles:
                query = query.bindparams(bindparam("roles", expanding=True))
            result = await session.execute(query, params)
            rows = result.mappings().all()
            data = [dict(row) for row in rows]
            return data

    async def chat_info(
        self,
        *,
        tenant_id: str,
        organization_id: list[str] | None = None,
        roles: list[str] | None = None,
        practitioner_id: list[str] | None = None,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> list[dict[str, Any]] | None:
        async with db_connection.session() as session:
            filters = ["p.care_team_id = ctp.care_team_id"]
            params = {}

            if tenant_id:
                filters.append("hs.tenant_id = :tenant_id")
                params["tenant_id"] = tenant_id

            if organization_id:
                filters.append("ou.organization_id IN :organization_id")
                params["organization_id"] = organization_id

            if start_date:
                filters.append("hs.created_at >= :start_date")
                params["start_date"] = start_date

            if end_date:
                filters.append("hs.created_at <= :end_date")
                params["end_date"] = end_date
            if practitioner_id:
                filters.append("hs.practitioner_id IN :practitioner_id")
                params["practitioner_id"] = practitioner_id
            if roles:
                filters.append("ctp.role IN :roles")
                params["roles"] = roles

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
            if organization_id:
                query = query.bindparams(bindparam("organization_id", expanding=True))
            if practitioner_id:
                query = query.bindparams(bindparam("practitioner_id", expanding=True))
            if roles:
                query = query.bindparams(bindparam("roles", expanding=True))
            result = await session.execute(query, params)
            rows = result.mappings().all()
            data = [dict(row) for row in rows]
            return data

    async def feedback_ia(
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
                filters.append("f.tenant_id = :tenant_id")
                params["tenant_id"] = tenant_id

            if organization_id:
                filters.append("ou.organization_id IN :organization_id")
                params["organization_id"] = organization_id

            if start_date:
                filters.append("f.created_at >= :start_date")
                params["start_date"] = start_date

            if end_date:
                filters.append("f.created_at <= :end_date")
                params["end_date"] = end_date

            where_clause = " AND ".join(filters) if filters else "1=1"

            query = text(f"""
                            select
                                f.user_id,
                                f.feedback,
                                ou.organization_id,
                                f.tenant_id,
                                max(f.created_at)
                            from
                                feedbacks f
                            inner join organizations_users ou on
                                f.user_id = ou.user_id
                            where {where_clause}
                            group by
                                f.user_id,
                                f.feedback,
                                ou.organization_id,
                                f.tenant_id;
            """)
            if organization_id:
                query = query.bindparams(bindparam("organization_id", expanding=True))
            result = await session.execute(query, params)
            rows = result.mappings().all()
            data = [dict(row) for row in rows]
            return data

    async def all_digital_interactions(
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
                filters.append("adi.tenant_id = :tenant_id")
                params["tenant_id"] = tenant_id

            if organization_id:
                filters.append("adi.organization_id IN :organization_id")
                params["organization_id"] = organization_id

            if start_date:
                filters.append("adi.interaction_date >= :start_date")
                params["start_date"] = start_date

            if end_date:
                filters.append("adi.interaction_date <= :end_date")
                params["end_date"] = end_date

            where_clause = " AND ".join(filters) if filters else "1=1"

            query = text(f"""
                            with concierge_interactions as (
                                select
                                    hs.patient_id,
                                    hs.created_at as interaction_date,
                                    'Concierge' as type,
                                    hs.tenant_id,
                                    ou.organization_id
                                from
                                    healthcare_service hs
                                inner join organizations_users ou on
                                    hs.patient_id = ou.user_id
                                inner join practitioners p on
                                    hs.practitioner_id = p.id
                                where
                                    p.title ilike 'Concierge'
                                    and hs.outcome <> 'abandonment'
                                ),
                                feedbacks_ia as (
                                select
                                    f.user_id as patient_id,
                                    f.created_at as interaction_date,
                                    'Feedback' as type,
                                    f.tenant_id,
                                    ou.organization_id
                                from
                                    feedbacks f
                                inner join organizations_users ou on
                                    f.user_id = ou.user_id

                                ),
                                symptoms_triages as (
                                select
                                    i.user_id as patient_id,
                                    i.ended_at as interaction_date,
                                    'Symptoms' as type,
                                    i.tenant_id,
                                    ou.organization_id
                                from
                                    interactions i
                                inner join organizations_users ou on
                                    i.user_id = ou.user_id
                                where
                                    i.ended_at is not null
                                ),
                                validation_tasks as (
                                select
                                    t.patient_id,
                                    t.created_at as interaction_date,
                                    'Validation' as type,
                                    t.tenant_id,
                                    ou.organization_id
                                from
                                    tasks t
                                inner join organizations_users ou on
                                    t.patient_id = ou.user_id
                                where
                                    t.title like '%Validar%'
                                ),
                                all_digital_interactions as (
                                select
                                    patient_id,
                                    interaction_date,
                                    type,
                                    tenant_id,
                                    organization_id
                                from
                                    concierge_interactions
                                union all
                                select
                                    patient_id,
                                    interaction_date,
                                    type,
                                    tenant_id,
                                    organization_id
                                from
                                    feedbacks_ia
                                union all
                                select
                                    patient_id,
                                    interaction_date,
                                    type,
                                    tenant_id,
                                    organization_id
                                from
                                    symptoms_triages
                                union all
                                select
                                    patient_id,
                                    interaction_date,
                                    type,
                                    tenant_id,
                                    organization_id
                                from
                                    validation_tasks
                                )
                                select
                                    patient_id,
                                    interaction_date,
                                    type,
                                    tenant_id,
                                    organization_id
                                from
                                    all_digital_interactions adi
                                where {where_clause}
                                order by
                                    patient_id,
                                    interaction_date;
            """)
            if organization_id:
                query = query.bindparams(bindparam("organization_id", expanding=True))
            result = await session.execute(query, params)
            rows = result.mappings().all()
            data = [dict(row) for row in rows]
            return data

    async def tasks_info(
        self,
        *,
        tenant_id: str,
        organization_id: list[str] | None = None,
        owner_id: list[str] | None = None,
        author_id: list[str] | None = None,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> list[dict[str, Any]] | None:
        async with db_connection.session() as session:
            filters = []
            params = {}

            if tenant_id:
                filters.append("t.tenant_id = :tenant_id")
                params["tenant_id"] = tenant_id

            if organization_id:
                filters.append("ou.organization_id IN :organization_id")
                params["organization_id"] = organization_id

            if start_date:
                filters.append("t.created_at >= :start_date")
                params["start_date"] = start_date

            if end_date:
                filters.append("t.created_at <= :end_date")
                params["end_date"] = end_date

            if owner_id:
                filters.append("t.owner IN :owner_id")
                params["owner_id"] = owner_id
            if author_id:
                filters.append("t.author IN :author_id")
                params["author_id"] = author_id

            where_clause = " AND ".join(filters) if filters else "1=1"

            query = text(f"""
                select
                    t.id,
                    t.title,
                    t.description,
                    t.priority,
                    concat(hup2.first_name, ' ', hup2.last_name) AS owner_name,
                    concat(hup3.first_name, ' ', hup3.last_name) AS author_name,
                    concat(hup1.first_name, ' ', hup1.last_name) AS patient_name,
                    t.metadata,
                    t.completed_at,
                    t.created_at,
                    t.updated_at,
                    t.status,
                    t.deadline,
                    t.tenant_id,
                    ou.organization_id
                from
                    tasks t
                join patients p on
                    p.id = t.patient_id
                join human_users hup1 on
                    hup1.id = t.patient_id
                join users u on
                    u.id = t.patient_id
                join organizations_users ou on
                    ou.user_id = u.id
                join organizations o on
                    o.id::text = ou.organization_id::text
                left join human_users hup2 on
                    hup2.id = t.owner_id
                left join human_users hup3 on
                    hup3.id = t.author_id
                where {where_clause};
            """)
            if organization_id:
                query = query.bindparams(bindparam("organization_id", expanding=True))
            if owner_id:
                query = query.bindparams(bindparam("owner_id", expanding=True))
            if author_id:
                query = query.bindparams(bindparam("author_id", expanding=True))
            result = await session.execute(query, params)
            rows = result.mappings().all()
            data = [dict(row) for row in rows]
            return data

    async def intent_log_info(
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
                filters.append("il.tenant_id = :tenant_id")
                params["tenant_id"] = tenant_id

            if organization_id:
                filters.append("ou.organization_id IN :organization_id")
                params["organization_id"] = organization_id

            if start_date:
                filters.append("il.created_at >= :start_date")
                params["start_date"] = start_date

            if end_date:
                filters.append("il.created_at <= :end_date")
                params["end_date"] = end_date

            where_clause = " AND ".join(filters) if filters else "1=1"

            query = text(f"""
                    select
                        il.message_id,
                        il.intent_theme,
                        il.intent_verb ,
                        il.action,
                        il.provider,
                        il.created_at,
                        cm.user_id,
                        concat(hu.first_name, ' ', hu.last_name) as patient_name,
                        ou.organization_id,
                        org.name as organization_name,
                        t.domain
                    from
                        intent_log il
                    join chat_messages cm
                    on
                        il.message_id = cm.id
                    join human_users hu
                    on
                        cm.user_id = hu.id
                    join organizations_users ou 
                    on
                        ou.user_id = hu.id
                    join organizations org
                    on
                        org.id = ou.organization_id
                    join tenants t
                    on
                        t.id = org.tenant_id
                    where {where_clause};
            """)
            if organization_id:
                query = query.bindparams(bindparam("organization_id", expanding=True))
            result = await session.execute(query, params)
            rows = result.mappings().all()
            data = [dict(row) for row in rows]
            return data
