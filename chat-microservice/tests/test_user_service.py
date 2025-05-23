import pytest
import asyncio # For testing async functions
from unittest.mock import AsyncMock, MagicMock # AsyncMock for async methods, MagicMock for sync

from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository # To mock this dependency
from app.models.user_model import User # For type hinting and expected return values

# Sample user data for mocking repository responses
sample_users_data_service = [
    User(id=1, username="johndoe_svc", email="john.doe.svc@example.com", first_name="JohnSvc", last_name="DoeSvc"),
    User(id=2, username="janedoe_svc", email="jane.doe.svc@example.com", first_name="JaneSvc", last_name="DoeSvc"),
]

pytestmark = pytest.mark.asyncio # Mark all tests in this module as asyncio

@pytest.fixture
def mock_user_repository():
    """Fixture for a mock UserRepository."""
    repo = MagicMock(spec=UserRepository) # UserRepository methods are synchronous
    # Mock the method that will be called by the service
    # get_users_by_name_criteria is synchronous in the repository
    repo.get_users_by_name_criteria = MagicMock(return_value=sample_users_data_service)
    return repo

@pytest.fixture
def user_service(mock_user_repository):
    """Fixture for UserService instance with a mocked repository."""
    # The UserService constructor expects a db session, but it only uses it
    # to initialize the repository. Since we're mocking the repository directly,
    # we can pass a MagicMock for the db_session.
    mock_db_session = MagicMock()
    # Patch the UserRepository where UserService instantiates it
    with patch('app.services.user_service.UserRepository', return_value=mock_user_repository) as PatchedRepo:
        service = UserService(db_session=mock_db_session)
        # Ensure the patched repo was used
        PatchedRepo.assert_called_once_with(mock_db_session)
        return service

async def test_fetch_users_by_name_filter_no_params(user_service, mock_user_repository):
    """Test fetch_users_by_name_filter with no parameters."""
    result = await user_service.fetch_users_by_name_filter()
    
    # Verify that the repository method was called correctly via asyncio.to_thread
    # (asyncio.to_thread is an implementation detail of the service,
    # we test that the service calls the repo method with correct args and returns its result)
    mock_user_repository.get_users_by_name_criteria.assert_called_once_with(
        first_name_starts_with=None,
        last_name_ends_with=None
    )
    assert result == sample_users_data_service

async def test_fetch_users_by_name_filter_first_name_only(user_service, mock_user_repository):
    """Test fetch_users_by_name_filter with first_name_starts_with only."""
    prefix = "Jo"
    await user_service.fetch_users_by_name_filter(first_name_starts_with=prefix)
    
    mock_user_repository.get_users_by_name_criteria.assert_called_once_with(
        first_name_starts_with=prefix,
        last_name_ends_with=None
    )

async def test_fetch_users_by_name_filter_last_name_only(user_service, mock_user_repository):
    """Test fetch_users_by_name_filter with last_name_ends_with only."""
    suffix = "Svc"
    await user_service.fetch_users_by_name_filter(last_name_ends_with=suffix)
    
    mock_user_repository.get_users_by_name_criteria.assert_called_once_with(
        first_name_starts_with=None,
        last_name_ends_with=suffix
    )

async def test_fetch_users_by_name_filter_both_params(user_service, mock_user_repository):
    """Test fetch_users_by_name_filter with both parameters."""
    prefix = "Ja"
    suffix = "Doe"
    await user_service.fetch_users_by_name_filter(first_name_starts_with=prefix, last_name_ends_with=suffix)
    
    mock_user_repository.get_users_by_name_criteria.assert_called_once_with(
        first_name_starts_with=prefix,
        last_name_ends_with=suffix
    )

async def test_fetch_users_by_name_filter_empty_results(user_service, mock_user_repository):
    """Test fetch_users_by_name_filter when repository returns an empty list."""
    mock_user_repository.get_users_by_name_criteria.return_value = []
    prefix = "NonExistent"
    
    result = await user_service.fetch_users_by_name_filter(first_name_starts_with=prefix)
    
    mock_user_repository.get_users_by_name_criteria.assert_called_once_with(
        first_name_starts_with=prefix,
        last_name_ends_with=None
    )
    assert result == []

print("test_user_service.py created with tests for UserService.fetch_users_by_name_filter.")
