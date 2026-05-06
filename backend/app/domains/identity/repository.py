from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.identity.models import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_id: UUID) -> User | None:
        return self.session.get(User, user_id)

    def get_by_external_subject(self, external_subject: str) -> User | None:
        statement = select(User).where(User.external_subject == external_subject)
        return self.session.scalar(statement)

    def add(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        self.session.refresh(user)
        return user

