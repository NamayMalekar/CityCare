"""Auth routes — sign up (open) and log in (open)."""
from fastapi import APIRouter, status

from app.controllers import auth as auth_controller
from app.schemas.user import SignupIn, LoginIn, UserOut, TokenOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupIn):
    return await auth_controller.signup(payload)


@router.post("/login", response_model=TokenOut)
async def login(payload: LoginIn):
    return await auth_controller.login(payload)
