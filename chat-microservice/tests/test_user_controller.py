import pytest
from unittest.mock import AsyncMock, patch # AsyncMock for async service methods
from fastapi.testclient import TestClient

# Import the FastAPI application instance from main.py
# This ensures all dependencies, routes, and configurations are loaded as in production.
from app.main import app 
from app.models.user_model import User # For constructing expected response data
from app.services.user_service import UserService # To assist with mocking

# Sample user data for mocking service responses
sample_users_for_controller = [
    User(id=1, username="controller_john", email="c.john@example.com", first_name="JohnCtrl", last_name="DoeCtrl"),
    User(id=2, username="controller_jane", email="c.jane@example.com", first_name="JaneCtrl", last_name="DoeCtrl"),
]

# Using pytest-asyncio for async tests if any, but TestClient handles async app code.
# No explicit pytestmark needed here as TestClient calls are synchronous.

@pytest.fixture
def client():
    """Fixture to create a TestClient instance for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def mock_user_service():
    """
    Fixture to mock the UserService.
    This allows us to control the behavior of fetch_users_by_name_filter.
    The mock will be injected via FastAPI's dependency override.
    """
    service_mock = AsyncMock(spec=UserService)
    # Configure the default return value for the method we're testing
    service_mock.fetch_users_by_name_filter = AsyncMock(return_value=sample_users_for_controller)
    return service_mock

def test_filter_users_by_name_no_params(client, mock_user_service):
    """Test GET /users/filter_by_name with no query parameters."""
    # Override the get_user_service dependency for this test
    # This replaces the actual UserService with our mock for the duration of this test's app context
    app.dependency_overrides[UserService] = lambda: mock_user_service
    
    response = client.get("/users/filter_by_name")
    
    assert response.status_code == 200
    # Verify the response JSON matches the mocked service output
    response_data = response.json()
    assert len(response_data) == len(sample_users_for_controller)
    # For more detailed check, compare actual fields if User model had orm_mode and Pydantic schemas were used for response
    # For now, checking length and that it's a list.
    # Assuming orm_mode=True on User model, FastAPI will serialize it.
    assert response_data[0]['username'] == sample_users_for_controller[0].username

    # Verify that the service method was called with None for both params
    mock_user_service.fetch_users_by_name_filter.assert_called_once_with(
        first_name_starts_with=None,
        last_name_ends_with=None
    )
    
    # Clean up dependency override after test
    app.dependency_overrides = {}

def test_filter_users_by_name_first_name_only(client, mock_user_service):
    """Test GET /users/filter_by_name with first_name_starts_with only."""
    app.dependency_overrides[UserService] = lambda: mock_user_service
    prefix = "John"
    
    response = client.get(f"/users/filter_by_name?first_name_starts_with={prefix}")
    
    assert response.status_code == 200
    mock_user_service.fetch_users_by_name_filter.assert_called_once_with(
        first_name_starts_with=prefix,
        last_name_ends_with=None
    )
    app.dependency_overrides = {}

def test_filter_users_by_name_last_name_only(client, mock_user_service):
    """Test GET /users/filter_by_name with last_name_ends_with only."""
    app.dependency_overrides[UserService] = lambda: mock_user_service
    suffix = "Ctrl"
    
    response = client.get(f"/users/filter_by_name?last_name_ends_with={suffix}")
    
    assert response.status_code == 200
    mock_user_service.fetch_users_by_name_filter.assert_called_once_with(
        first_name_starts_with=None,
        last_name_ends_with=suffix
    )
    app.dependency_overrides = {}

def test_filter_users_by_name_both_params(client, mock_user_service):
    """Test GET /users/filter_by_name with both query parameters."""
    app.dependency_overrides[UserService] = lambda: mock_user_service
    prefix = "Jane"
    suffix = "Doe"
    
    response = client.get(f"/users/filter_by_name?first_name_starts_with={prefix}&last_name_ends_with={suffix}")
    
    assert response.status_code == 200
    mock_user_service.fetch_users_by_name_filter.assert_called_once_with(
        first_name_starts_with=prefix,
        last_name_ends_with=suffix
    )
    app.dependency_overrides = {}

def test_filter_users_by_name_empty_string_params(client, mock_user_service):
    """
    Test GET /users/filter_by_name with empty string query parameters.
    The controller logic should treat empty strings as if the parameter was not provided (None).
    """
    app.dependency_overrides[UserService] = lambda: mock_user_service
    
    response = client.get("/users/filter_by_name?first_name_starts_with=&last_name_ends_with=")
    
    assert response.status_code == 200
    # Assert that service was called with None for both, due to controller's stripping logic
    mock_user_service.fetch_users_by_name_filter.assert_called_once_with(
        first_name_starts_with=None, # Empty string becomes None in controller
        last_name_ends_with=None    # Empty string becomes None in controller
    )
    app.dependency_overrides = {}

def test_filter_users_by_name_service_returns_empty(client, mock_user_service):
    """Test GET /users/filter_by_name when the service returns an empty list."""
    app.dependency_overrides[UserService] = lambda: mock_user_service
    mock_user_service.fetch_users_by_name_filter.return_value = [] # Override mock for this test
    prefix = "NonExistent"
    
    response = client.get(f"/users/filter_by_name?first_name_starts_with={prefix}")
    
    assert response.status_code == 200
    assert response.json() == []
    mock_user_service.fetch_users_by_name_filter.assert_called_once_with(
        first_name_starts_with=prefix,
        last_name_ends_with=None
    )
    app.dependency_overrides = {}

print("test_user_controller.py created with API endpoint tests.")
