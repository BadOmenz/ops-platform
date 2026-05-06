from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.domains.identity.models import User
from app.domains.identity.schemas import UserRead

router = APIRouter(prefix="/identity", tags=["identity"])


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user

