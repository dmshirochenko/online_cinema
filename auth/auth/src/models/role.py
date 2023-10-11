import uuid

from sqlalchemy.dialects.postgresql import UUID

from db.users import db


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=True,
    )
    role = db.Column(db.String(32), unique=True, nullable=True)

    def __repr__(self):
        return str(self.role)
