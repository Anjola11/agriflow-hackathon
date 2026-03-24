from sqlmodel import SQLModel, Field
import uuid


class Bank(SQLModel, table=True):
    __tablename__ = "banks"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    name: str = Field(index=True)
    code: str = Field(unique=True, index=True)
    active: bool = Field(default=True)
    