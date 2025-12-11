from src.auth.schemas import UserCreateModel
auth_prefix = f"/api/v1/auth"


def test_user_creation(fake_db_session, fake_user_service, test_client):
    """Test user creation endpoint."""
    signup_data = {
        "username": "testuser",
        "email": "mohismx10@gmail.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "StrongPass1",
    }
    user_data = UserCreateModel.model_validate(signup_data)
    
    response = test_client.post(url=f"{auth_prefix}/signup", json=signup_data)
    assert fake_user_service.user_exists_called_once()
    assert fake_user_service.user_exists_called_once_with(signup_data["email"], fake_db_session)
    assert fake_user_service.create_user_called_once()
    assert fake_user_service.create_user_called_once_with(user_data, fake_db_session)
