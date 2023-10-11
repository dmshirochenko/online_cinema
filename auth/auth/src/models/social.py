import uuid

from db.users import db
from models.user import User
from sqlalchemy import or_
from sqlalchemy.dialects.postgresql import UUID


class SocialAccount(db.Model):
    __tablename__ = "social_account"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=True,
    )
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    user = db.relationship(User, backref=db.backref("social_accounts", lazy=True))

    social_id = db.Column(db.Text, nullable=False)
    social_name = db.Column(db.Text, nullable=False)

    __table_args__ = (db.UniqueConstraint("social_id", "social_name", name="social_pk"),)

    def __repr__(self):
        return f"<SocialAccount {self.social_name}:{self.user_id}>"

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

    @classmethod
    def get_user_by_universal_login(cls, login: str | None = None, email: str | None = None):
        return cls.query.filter(or_(cls.social_id == login, cls.social_id == email)).first()
