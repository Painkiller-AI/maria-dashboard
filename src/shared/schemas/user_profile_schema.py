from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class RoleSchema(BaseModel):
    id: UUID
    name: str
    description: str | None = None


class UserType(Enum):
    user = "user"
    bot = "bot"
    human = "human"
    patient = "patient"
    practitioner = "practitioner"


class UserProfileSchema(BaseModel):
    id: str
    tenant_id: str
    first_name: str
    last_name: str
    active: bool
    type: UserType
    email: str | None = None
    phone: str | None = None
    role: RoleSchema
    permissions: list[str] = []
    image_url: HttpUrl | None = None
    metadata: dict | None = None
    created_at: datetime
    updated_at: datetime

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def has_permissions(self, permissions: list[str], match_all: bool = True) -> bool:
        if match_all:
            return all(permission in self.permissions for permission in permissions)
        else:
            return any(permission in self.permissions for permission in permissions)
