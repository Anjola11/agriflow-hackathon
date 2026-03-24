from fastapi import APIRouter, Depends, status, Response, Cookie
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.schemas import (
    UserCreateInput,
    UserCreateResponse,
    LoginInput,
    LoginResponse,
    AdminLoginInput,
    AdminLoginResponse,
    RenewAccessTokenResponse,
    LogoutResponse
)
from src.db.main import get_session
from src.auth.services import AuthServices
from src.config import Config
from src.utils.auth import access_token_expiry, refresh_token_expiry
from src.utils.dependencies import get_current_user



auth_router = APIRouter()


cookie_settings = {
    "httponly": True,
    "secure": Config.IS_PRODUCTION,
    "samesite": "none" if Config.IS_PRODUCTION else "lax"
}


def get_auth_services() -> AuthServices:
    return AuthServices()



@auth_router.post('/signup', response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_input: UserCreateInput, 
    response: Response,
    session: AsyncSession = Depends(get_session),
    auth_services: AuthServices = Depends(get_auth_services)
    ):

    user = await auth_services.create_user(user_input, session)

    response.set_cookie(
        key="access_token",
        value=user.get("access_token"),
        **cookie_settings,
        max_age= int(access_token_expiry.total_seconds())
    )

    response.set_cookie(
        key="refresh_token",
        value=user.get("refresh_token"),
        **cookie_settings,
        max_age= int(refresh_token_expiry.total_seconds())
    )
    return {
        "success": True,
        "message": "Registration successful",
        "data": user
    }


@auth_router.post('/login', response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    login_input: LoginInput,
    response: Response,
    session: AsyncSession = Depends(get_session),
    auth_services: AuthServices = Depends(get_auth_services)
    ):

    user = await auth_services.login(login_input, session)

    response.set_cookie(
        key="access_token",
        value=user.get("access_token"),
        **cookie_settings,
        max_age= int(access_token_expiry.total_seconds())
    )

    response.set_cookie(
        key="refresh_token",
        value=user.get("refresh_token"),
        **cookie_settings,
        max_age= int(refresh_token_expiry.total_seconds())
    )
    return {
        "success": True,
        "message": "Login successful",
        "data": user
    }


@auth_router.post('/renew-access-token', response_model=RenewAccessTokenResponse, status_code=status.HTTP_200_OK)
async def renew_access_token(
    response: Response,
    session: AsyncSession = Depends(get_session),
    auth_services: AuthServices = Depends(get_auth_services),
    refresh_token: str | None = Cookie(default=None)
    ):

    tokens = await auth_services.renewAccessToken(refresh_token, session)

    response.set_cookie(
        key="access_token",
        value=tokens.get("access_token"),
        **cookie_settings,
        max_age= int(access_token_expiry.total_seconds())
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens.get("refresh_token"),
        **cookie_settings,
        max_age= int(refresh_token_expiry.total_seconds())
    )
    return {
        "success": True,
        "message": "Access token renewed",
        "data": tokens
    }


@auth_router.post('/logout', response_model=LogoutResponse, status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    auth_services: AuthServices = Depends(get_auth_services),
    access_token: str | None = Cookie(default=None),
    refresh_token: str | None = Cookie(default=None)
    ):

    result = await auth_services.logout(response, access_token, refresh_token)
    
    return result


@auth_router.post('/admin/login', response_model=AdminLoginResponse, status_code=status.HTTP_200_OK)
async def admin_login(
    login_input: AdminLoginInput,
    response: Response,
    session: AsyncSession = Depends(get_session),
    auth_services: AuthServices = Depends(get_auth_services)
    ):

    admin = await auth_services.admin_login(login_input, session)

    response.set_cookie(
        key="access_token",
        value=admin.get("access_token"),
        **cookie_settings,
        max_age= int(access_token_expiry.total_seconds())
    )

    response.set_cookie(
        key="refresh_token",
        value=admin.get("refresh_token"),
        **cookie_settings,
        max_age= int(refresh_token_expiry.total_seconds())
    )
    return {
        "success": True,
        "message": "Admin login successful",
        "data": admin
    }

@auth_router.get("/me")
async def get_me(current_user = Depends(get_current_user), auth_services: AuthServices = Depends(get_auth_services)):
    return await auth_services.get_me(current_user)





