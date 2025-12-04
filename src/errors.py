from typing import Any, Callable
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI, status
from sqlalchemy.exc import SQLAlchemyError


class BooklyException(Exception):
    """this is the Base exception class for Bookly application."""

    pass


class InvalidToken(BooklyException):
    """User has provided an invalid token or expired token."""

    pass


class RevokedToken(BooklyException):
    """User has provided a token that has been revoked."""

    pass


class AccessTokenRequired(BooklyException):
    """User has provided a refresh token where access token is required."""

    pass


class RefreshTokenRequired(BooklyException):
    """User has provided an access token where refresh token is required."""

    pass


class UserAlreadyExists(BooklyException):
    """User with given email already exists."""

    pass


class InvalidCredentials(BooklyException):
    """User has provided invalid credentials, user has provided wrong email or password."""

    pass


class InsufficientPermission(BooklyException):
    """User does not have sufficient permissions to perform the action."""

    pass


class BookNotFound(BooklyException):
    """Book not Found"""

    pass


class TagNotFound(BooklyException):
    """Tag not Found"""

    pass


class TagAlreadyExists(BooklyException):
    """Tag already exists"""

    pass


class UserNotFound(BooklyException):
    """User not Found"""

    pass


class AccountNotVerified(Exception):
    """Account not yet verified"""

    pass


# errors.py - Add these missing exceptions
class ReviewNotFound(BooklyException):
    """Review not found"""

    pass


class ReviewAlreadyExists(BooklyException):
    """User already reviewed this book"""

    pass


class ReviewPermissionDenied(BooklyException):
    """User doesn't have permission to modify this review"""

    pass


class TagInUse(BooklyException):
    """Tag is associated with books and cannot be deleted"""

    pass


class InvalidTagName(BooklyException):
    """Invalid tag name format"""

    pass


def create_exception_handler(
    status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={"detail": initial_detail},
        )

    return exception_handler


def register_all_errors(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "User with email already exists",
                "error_code": "user_exists",
            },
        ),
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User not found",
                "error_code": "user_not_found",
            },
        ),
    )
    app.add_exception_handler(
        BookNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Book not found",
                "error_code": "book_not_found",
            },
        ),
    )
    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Invalid Email Or Password",
                "error_code": "invalid_email_or_password",
            },
        ),
    )
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid Or expired",
                "resolution": "Please get new token",
                "error_code": "invalid_token",
            },
        ),
    )
    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid or has been revoked",
                "resolution": "Please get new token",
                "error_code": "token_revoked",
            },
        ),
    )
    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Please provide a valid access token",
                "resolution": "Please get an access token",
                "error_code": "access_token_required",
            },
        ),
    )
    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Please provide a valid refresh token",
                "resolution": "Please get an refresh token",
                "error_code": "refresh_token_required",
            },
        ),
    )
    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "You do not have enough permissions to perform this action",
                "error_code": "insufficient_permissions",
            },
        ),
    )
    app.add_exception_handler(
        TagNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={"message": "Tag Not Found", "error_code": "tag_not_found"},
        ),
    )

    app.add_exception_handler(
        TagAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Tag Already exists",
                "error_code": "tag_exists",
            },
        ),
    )

    app.add_exception_handler(
        BookNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Book Not Found",
                "error_code": "book_not_found",
            },
        ),
    )

    app.add_exception_handler(
        AccountNotVerified,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Account Not verified",
                "error_code": "account_not_verified",
                "resolution": "Please check your email for verification details",
            },
        ),
    )

    # @app.exception_handler(500)
    # async def internal_server_error(request, exc):
    #     return JSONResponse(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         content={
    #             "message": "An internal server error occurred.",
    #             "resolution": "Please try again later or contact support if the issue persists.",
    #             "error_code": "internal_server_error",
    #         },
    #     )

    # @app.exception_handler(SQLAlchemyError)
    # async def database__error(request, exc):
    #     print(str(exc))
    #     return JSONResponse(
    #         content={
    #             "message": "Oops! Something went wrong",
    #             "error_code": "server_error",
    #         },
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #     )

    app.add_exception_handler(
        ReviewNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Review not found",
                "error_code": "review_not_found",
            },
        ),
    )

    app.add_exception_handler(
        ReviewAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "You have already reviewed this book",
                "error_code": "review_already_exists",
            },
        ),
    )

    app.add_exception_handler(
        ReviewPermissionDenied,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "You don't have permission to modify this review",
                "error_code": "review_permission_denied",
            },
        ),
    )

    app.add_exception_handler(
        TagInUse,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Tag is associated with books and cannot be deleted",
                "error_code": "tag_in_use",
                "resolution": "Remove tag from all books first or merge with another tag",
            },
        ),
    )

    app.add_exception_handler(
        InvalidTagName,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Invalid tag name format",
                "error_code": "invalid_tag_name",
                "resolution": "Tag names can only contain letters, numbers, spaces, hyphens, and underscores",
            },
        ),
    )
