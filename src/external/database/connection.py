# external/database/connection.py
from contextlib import asynccontextmanager
from typing import AsyncIterator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from settings import get_settings

settings = get_settings()


class DBConnection:
    def __init__(self, uri: str = str(settings.DATABASE_URI)):
        self.engine = create_async_engine(
            uri,
            echo=True,
            pool_pre_ping=True,
            poolclass=NullPool,
        )
        self.__sessionmaker = async_sessionmaker(
            autocommit=False, bind=self.engine, autoflush=False
        )
        

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self.__sessionmaker is None:
            raise Exception("DBConnectionHandler is not initialized")

        session = self.__sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


db_connection = DBConnection()
