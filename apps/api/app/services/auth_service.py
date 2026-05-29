import uuid

from fastapi import HTTPException, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.auth import TokenResponse, UserOut

GOOGLE_ISSUERS = {"accounts.google.com", "https://accounts.google.com"}


def verify_google_id_token(token: str) -> dict:
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GOOGLE_CLIENT_ID is not configured",
        )
    try:
        payload = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.google_client_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token",
        ) from exc

    if payload.get("iss") not in GOOGLE_ISSUERS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token issuer",
        )
    if not payload.get("email"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google account email is required",
        )
    if not payload.get("email_verified"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google account email is not verified",
        )
    return payload


def sync_user_from_google(db: Session, google_payload: dict) -> User:
    email = str(google_payload["email"]).lower()
    name = google_payload.get("name")

    user = db.scalar(select(User).where(User.email == email))
    if user:
        user.name = name
        user.oauth_provider = "google"
    else:
        user = User(
            id=uuid.uuid4(),
            email=email,
            name=name,
            oauth_provider="google",
        )
        db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_with_google(db: Session, id_token_str: str) -> TokenResponse:
    google_payload = verify_google_id_token(id_token_str)
    user = sync_user_from_google(db, google_payload)
    access_token = create_access_token(user_id=user.id, email=user.email)
    return TokenResponse(
        access_token=access_token,
        user=UserOut.model_validate(user),
    )
