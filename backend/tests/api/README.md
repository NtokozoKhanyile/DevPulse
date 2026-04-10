# DevPulse Backend Test Suite

Comprehensive test coverage for the DevPulse backend API.

## Test Structure

```
tests/api/
├── conftest.py              # Pytest fixtures and test setup
├── test_auth.py             # Authentication (registration, login, tokens, logout)
├── test_projects.py         # Project CRUD and ownership validation
├── test_users.py            # User profiles and endpoints
├── test_collaborations.py   # Collaboration requests and comments
├── test_wall.py             # Celebration wall endpoints
├── test_endpoints.py        # Milestones, feed, and health checks
├── test_services.py         # Service layer unit tests
└── test_security.py         # Password hashing and token security
```

## Running Tests

### All Tests
```bash
pytest tests/ -v
```

### Specific Test File
```bash
pytest tests/api/test_auth.py -v
```

### Specific Test Class
```bash
pytest tests/api/test_auth.py::TestRegister -v
```

### Specific Test
```bash
pytest tests/api/test_auth.py::TestRegister::test_register_success -v
```

### With Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

### Async Tests
```bash
pytest tests/ -v --asyncio-mode=auto
```

## Test Coverage

### Authentication (`test_auth.py`)
- ✅ User registration (success, duplicate email/username, validation)
- ✅ User login (success, wrong password, inactive user, rate limiting)
- ✅ Token refresh (success, invalid token, blacklisting)
- ✅ Logout (success, blacklisting refresh token)
- ✅ Full auth flow integration

### Projects (`test_projects.py`)
- ✅ Create project (success, auth required, ownership)
- ✅ List projects (pagination, public/private filtering)
- ✅ Get project (success, 404, view count increment)
- ✅ Update project (success, auth, ownership, partial fields)
- ✅ Delete project (success, auth, ownership)
- ✅ Complete project (success, auth, stage transition)
- ✅ Ownership validation (owner can modify, non-owner forbidden)

### Users (`test_users.py`)
- ✅ Get current user (`/me` endpoint)
- ✅ Update profile (display name, bio, skills, URLs)
- ✅ Get user profile by username (public data)
- ✅ Get user projects (pagination, public only)
- ✅ Edge cases (empty bio, long bio, invalid URLs)

### Collaborations & Comments (`test_collaborations.py`)
- ✅ Collaboration request endpoints
- ✅ Comment posting and retrieval
- ✅ Authentication requirements

### Endpoints (`test_endpoints.py`)
- ✅ Milestones CRUD
- ✅ Feed endpoints with pagination
- ✅ Health check endpoint

### Services (`test_services.py`)
- ✅ AuthService (register, authenticate, token generation)
- ✅ UserService (get user, update profile, avatar)
- ✅ ProjectService (create, update, get, ownership checks)

### Security (`test_security.py`)
- ✅ Password hashing (Bcrypt)
- ✅ Password verification
- ✅ Access token creation and validation
- ✅ Refresh token creation and validation
- ✅ Token expiration
- ✅ Special characters and unicode support
- ✅ Edge cases (empty passwords, very long IDs)

## Test Fixtures

The `conftest.py` provides comprehensive fixtures:

### Database & Client
- `engine` - Test database engine
- `db_session` - Async database session
- `client` - AsyncClient for HTTP requests

### User Fixtures
- `test_user` - Verified, active user
- `test_user_2` - Second user for collaboration tests
- `inactive_user` - Inactive user account
- `unverified_user` - Unverified email user
- `auth_token` - Access token for test_user
- `auth_token_2` - Access token for test_user_2
- `refresh_token` - Refresh token for test_user

### Project Fixtures
- `test_project` - Public project owned by test_user
- `private_project` - Private project
- `completed_project` - Project with COMPLETED stage

### Helper Fixtures
- `authorization_header` - Bearer token header dict
- `test_user_data` - User registration data
- `test_project_data` - Project creation data

## Best Practices

1. **Authentication**: Always use `auth_token` fixture for protected endpoints
2. **Ownership**: Test that non-owners cannot modify resources
3. **Async/Await**: All tests use `@pytest.mark.asyncio` and `async/await`
4. **Fixtures**: Reuse fixtures to keep tests DRY and efficient
5. **Assertions**: Test both success and failure paths
6. **Edge Cases**: Include boundary conditions and error scenarios

## Environment Setup

Ensure `.env` has these variables:
```
TEST_DATABASE_URL=postgresql+asyncpg://user:pass@localhost/devpulse_test
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=<32+ character secret>
```

## CI/CD Integration

Tests should be run before commit:
```bash
# Run tests
pytest tests/api/ -v --asyncio-mode=auto

# With coverage threshold
pytest tests/api/ --cov=app --cov-fail-under=80
```

## Notes

- Tests use a separate `TEST_DATABASE_URL` to avoid polluting production/dev data
- Each test is isolated with automatic rollback
- Redis is used for rate limiting and token blacklisting tests
- Test fixtures are scoped appropriately (session, function, etc.)
