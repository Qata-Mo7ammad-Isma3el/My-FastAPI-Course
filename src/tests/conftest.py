from src.db.main import get_session
from src.main import app
from unittest.mock import Mock
from fastapi.testclient import TestClient
from src.auth.dependencies import AccessTokenBearer, RefreshTokenBearer, RoleChecker
import pytest

mock_db_session = Mock()
mock_user_service = Mock()
mock_book_service = Mock()

access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()
role_checker = RoleChecker(allowed_roles=["user", "admin"])



def get_mock_session():
    yield mock_db_session


app.dependency_overrides[get_session] = get_mock_session
app.dependency_overrides[role_checker] = Mock()
app.dependency_overrides[access_token_bearer] = Mock()
app.dependency_overrides[refresh_token_bearer] = Mock()


@pytest.fixture(scope="module")
def fake_db_session():
    """Fixture to provide a mock database session."""
    return mock_db_session

@pytest.fixture(scope="module")
def fake_user_service():
    """Fixture to provide a mock user service."""
    return mock_user_service

@pytest.fixture(scope="module")
def test_client():
    """Fixture to provide a TestClient for the FastAPI app."""
    with TestClient(app) as c:
        return c

@pytest.fixture(scope="module")
def fake_book_service():    
    """Fixture to provide a mock book service."""
    return mock_book_service