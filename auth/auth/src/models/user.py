import uuid

from db.users import db
from sqlalchemy import or_, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


user_role = db.Table(
    "user_roles",
    db.Column("user_id", UUID(as_uuid=True), db.ForeignKey("users.id")),
    db.Column("role_id", UUID(as_uuid=True), db.ForeignKey("roles.id")),
)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=True,
    )
    login = db.Column(db.String, unique=True, nullable=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=True)
    admin = db.Column(db.Boolean, default=False)
    country = db.Column(db.String, unique=False, nullable=True)

    Index("user_country_idx", "id", "country", unique=True)

    roles = relationship("Role", secondary=user_role, backref="users", cascade="all, delete")

    def __repr__(self):
        admin_tag = " [ADMIN]" if self.admin_tag else ""
        return f"<User {self.login}>{admin_tag}"

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

    @classmethod
    def get_user_by_universal_login(cls, login: str | None = None, email: str | None = None):
        return cls.query.filter(or_(cls.login == login, cls.email == email)).first()

    def partition_by_country(self):
        countries = {
            "EUROPE": ["GERMANY", "SPAIN", "FRANCE"],
            "ASIA": ["TURKEY", "INDIA", "JAPAN"],
            "NORTHAMERICA": ["CANADA", "USA"],
            "SOUTHAMERICA": ["BRAZIL", "ARGENTINA"],
        }

        for key in countries.keys():
            values = ",".join(countries[key])
            db.session.execute(f"CREATE TABLE {key} PARTITION of {self.__tablename__} FOR VALUES IN({values});")
            db.session.commit()


class LoginRecord(db.Model):
    __tablename__ = "login_records"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=True,
    )
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    auth_date = db.Column(db.DateTime)
    user_agent = db.Column(db.String, unique=False)

    Index("user_agent_active", "user_id", "user_agent")

    def partition_by_auth_date(self, date_from: str, date_to: str):
        """
        Part table login_records by auth date of users
        Args:
            date_from: e.g. '2023-01-15'
            date_to: e.g. '2023-03-25'

        """
        table_name = self.__tablename__ + f"_{date_from}"
        stmt = (
            f"CREATE TABLE {table_name} PARTITION OF {self.__tablename__} "
            f"FOR VALUES FROM ({date_from}) TO ({date_to});"
        )
        db.session.execute(stmt)
        db.session.commit()
