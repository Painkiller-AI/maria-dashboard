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
