from uuid import UUID

from pydantic import BaseModel, Field


class GoogleAuthRequest(BaseModel):
    id_token: str = Field(description="Google OAuth ID token from the client")


class UserOut(BaseModel):
    id: UUID
    email: str
    name: str | None
    oauth_provider: str | None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
