from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps.auth import get_current_user
from app.models.user import User
from app.schemas.auth import GoogleAuthRequest, TokenResponse, UserOut
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/sync", response_model=TokenResponse)
def auth_sync(
    body: GoogleAuthRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Exchange a Google ID token for an API JWT and upsert the user."""
    return auth_service.login_with_google(db, body.id_token)


@router.get("/me", response_model=UserOut)
def auth_me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(current_user)
