from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domains.identity.models import User
from app.domains.identity.repository import UserRepository
from app.domains.identity.schemas import UserIdentity


class IdentityService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserRepository(session)

    def get_or_create_user(self, identity: UserIdentity) -> User:
        external_subject = identity.external_subject.strip()
        user = self.users.get_by_external_subject(external_subject)

        if user is not None:
            changed = False
            if user.email != identity.email:
                user.email = identity.email
                changed = True
            if user.display_name != identity.display_name:
                user.display_name = identity.display_name
                changed = True
            if changed:
                user.updated_at = datetime.now(UTC)
                self.session.commit()
                self.session.refresh(user)
            return user

        user = User(
            external_subject=external_subject,
            email=str(identity.email),
            display_name=identity.display_name.strip(),
        )

        try:
            user = self.users.add(user)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            user = self.users.get_by_external_subject(external_subject)
            if user is None:
                raise

        return user

