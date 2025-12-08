from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel.ext.asyncio.session import AsyncSession
from pathlib import Path
from typing import Annotated, List
from src.auth.schemas import (
    UserCreateModel,
    UserModel,
    UserLoginModel,
    UserBooksModel,
    EmailModel,
)
from src.auth.service import UserService
from src.db.main import get_session
from src.auth.utils import (
    create_access_token,
    decode_token,
    verify_password,
    create_url_safe_token,
    decode_url_safe_token,
)
from datetime import timedelta, timezone
from src.config import settings
from src.auth.dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
    RoleChecker,
)
from src.db.redis import RedisClient, get_redis
from datetime import datetime
from src.errors import UserAlreadyExists, UserNotFound, InvalidCredentials, InvalidToken

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from src.mail import mail, create_message, email_service

limiter = Limiter(key_func=get_remote_address)
auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(allowed_roles=["admin", "user"])

# Setup Jinja2 templates
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@auth_router.post("/send_test_email")
async def send_test_email(email_data: EmailModel):
    """
    Send a test email using the professional template.
    """
    for email in email_data.addresses:
        # Create a dummy verification token for testing
        token = create_url_safe_token({"email": email})

        email_sent = await email_service.send_verification_email(
            user_email=email, user_name="Test User", token=token
        )

        if not email_sent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send email to {email}",
            )
    return {
        "message": f"Test emails sent successfully to {len(email_data.addresses)} recipient(s)"
    }


@auth_router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
)
async def create_user_account(
    user_data: UserCreateModel, session: Annotated[AsyncSession, Depends(get_session)]
):
    email = user_data.email
    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data, session)

    # Create verification token
    token = create_url_safe_token({"email": new_user.email})

    # Send verification email using professional template
    user_full_name = f"{new_user.first_name} {new_user.last_name}"
    email_sent = await email_service.send_verification_email(
        user_email=new_user.email, user_name=user_full_name, token=token
    )

    # Return user info (excluding sensitive data)
    user_response = {
        "uid": str(new_user.uid),
        "email": new_user.email,
        "username": new_user.username,
        "first_name": new_user.first_name,
        "last_name": new_user.last_name,
        "is_verified": new_user.is_verified,
        "created_at": new_user.created_at.isoformat() if new_user.created_at else None,
    }

    if not email_sent:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Account created, but verification email failed to send. Please contact support.",
                "user": user_response,
                "warning": "email_failed",
            },
        )

    return {
        "message": "Account created successfully. Please check your email to verify your account.",
        "user": user_response,
        "email_sent": True,
    }


@auth_router.get("/verify/{token}", response_class=HTMLResponse)
async def verify_email(
    token: str, request: Request, session: Annotated[AsyncSession, Depends(get_session)]
):
    print(f"===== EMAIL VERIFICATION ATTEMPT =====")
    print(f"Token received: {token[:50]}...")
    try:
        # Decode token with 24 hours max age (86400 seconds)
        data = decode_url_safe_token(token, max_age=86400)
        print(f"Token decoded successfully. Data: {data}")
        email = data.get("email")

        if not email:
            print("Token decoded but no email found in token data")
            return templates.TemplateResponse(
                "verification_error.html",
                {
                    "request": request,
                    "error_message": "Invalid verification token.",
                    "domain": settings.DOMAIN,
                },
                status_code=400,
            )

        user = await user_service.get_user_by_email(email, session)
        if not user:
            return templates.TemplateResponse(
                "verification_error.html",
                {
                    "request": request,
                    "error_message": "User not found.",
                    "domain": settings.DOMAIN,
                },
                status_code=404,
            )

        # Check if already verified
        if user.is_verified:
            return templates.TemplateResponse(
                "verification_success.html",
                {
                    "request": request,
                    "email": user.email,
                    "username": user.username,
                    "redirect_url": f"http://{settings.DOMAIN}/login?verified=true",
                },
            )

        # Update verification status
        user.is_verified = True
        user.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        await user_service.update_user(user, session)

        # Return success HTML page
        return templates.TemplateResponse(
            "verification_success.html",
            {
                "request": request,
                "email": user.email,
                "username": user.username,
                "redirect_url": f"http://{settings.DOMAIN}/login?verified=true",
            },
        )

    except Exception as e:
        # Log the error with full details
        print(
            f"Email verification failed - Error type: {type(e).__name__}, Message: {str(e)}"
        )
        return templates.TemplateResponse(
            "verification_error.html",
            {
                "request": request,
                "error_message": "Token is invalid or expired. Please request a new verification email.",
                "domain": settings.DOMAIN,
            },
            status_code=401,
        )


@auth_router.post("/login")
@limiter.limit("5/minute")  ## ch8 QATA
async def login_user(
    request: Request,
    login_data: UserLoginModel,
    session: Annotated[AsyncSession, Depends(get_session)],
):

    email = login_data.email
    password = login_data.password
    user = await user_service.get_user_by_email(email, session)
    if user is not None:
        password_valid = verify_password(password, user.password_hash)
        if password_valid:
            access_token = create_access_token(
                user_data={
                    "uid": str(user.uid),
                    "email": user.email,
                    "role": user.role,
                },
            )
            refresh_token = create_access_token(
                user_data={
                    "uid": str(user.uid),
                    "email": user.email,
                    "role": user.role,  ## ch3QATA
                },
                expiry=timedelta(seconds=settings.REFRESH_TOKEN_EXPIRY),
                refresh=True,
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Login Successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "uid": str(user.uid),
                        "email": user.email,
                    },
                    "token_type": "bearer",
                },
            )
    raise InvalidCredentials()


@auth_router.get("/refresh_token")
async def get_new_access_token(
    token_details: Annotated[dict, Depends(RefreshTokenBearer())],
):
    print(f"Token details received: {token_details}")
    expiry_timestamp = token_details.get("exp")

    if not expiry_timestamp:
        raise InvalidToken()

    try:
        # Convert timestamp with UTC timezone
        expiry_datetime = datetime.fromtimestamp(expiry_timestamp, tz=timezone.utc)
        current_datetime = datetime.now(timezone.utc)

        print(f"Expiry: {expiry_datetime}, Current: {current_datetime}")

        if expiry_datetime > current_datetime:
            new_access_token = create_access_token(
                user_data=token_details["user"],
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "access_token": new_access_token,
                    "token_type": "bearer",
                },
            )
    except (ValueError, OSError, KeyError) as e:
        print(f"Error in refresh_token: {type(e).__name__}: {str(e)}")
        raise InvalidToken()

    raise InvalidToken()


@auth_router.get("/me", response_model=UserBooksModel)
async def get_logged_in_user(
    current_user: Annotated[dict, Depends(get_current_user)],
    _: bool = Depends(role_checker),
) -> UserBooksModel:
    return current_user  # TODO try to add uid in a good looking way


@auth_router.post("/logout")
async def revoke_token(
    token_details: Annotated[dict, Depends(AccessTokenBearer())],
    redis_client: Annotated[RedisClient, Depends(get_redis)],
):
    jti = token_details.get("jti")
    exp = token_details.get("exp")
    user_id = token_details["user"]["uid"]
    # Calculate remaining time until expiry
    remaining_ttl = exp - int(datetime.now(timezone.utc).timestamp())
    if remaining_ttl > 0:
        await redis_client.add_jti_to_BlockList(jti, user_id, ttl=remaining_ttl)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Token has been revoked successfully."},
    )


## TODO ch6 QATA
@auth_router.post("/forgot-password")
async def forgot_password(email: str, session: AsyncSession = Depends(get_session)):
    # Generate reset token, send email, etc.
    pass


@auth_router.post("/reset-password")
async def reset_password(
    token: str, new_password: str, session: AsyncSession = Depends(get_session)
):
    # Validate reset token, update password
    pass
