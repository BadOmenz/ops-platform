from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.domains.demo.schemas import DemoSessionRead
from app.domains.demo.service import DemoSessionService

router = APIRouter(prefix="/demo", tags=["demo"])


def get_demo_session_service(session: Session = Depends(get_db_session)) -> DemoSessionService:
    return DemoSessionService(session)


@router.post("/sessions", response_model=DemoSessionRead, status_code=201)
def create_demo_session(
    service: DemoSessionService = Depends(get_demo_session_service),
) -> DemoSessionRead:
    return service.create_session()
