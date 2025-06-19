# SDK Creator

[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/mghalix/sdk-creator)
[![PyPI version](https://badge.fury.io/py/sdk-creator.svg)](https://badge.fury.io/py/sdk-creator)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A foundation for building **strongly-typed Python SDKs** around existing REST
APIs. SDK Creator provides the async HTTP foundation, comprehensive utilities,
and production-grade testing while you focus on building clean, Pydantic-powered
API wrappers with comprehensive error handling and type safety.

## Why SDK Creator?

Instead of manually handling HTTP requests, JSON parsing, and error handling
for every API integration, SDK Creator lets you:

-   **Build clean SDK interfaces** with strong typing and Pydantic models
-   **Focus on business logic** rather than HTTP boilerplate
-   **Leverage async/await** for high-performance API calls
-   **Handle errors gracefully** with comprehensive exception types
-   **Maintain consistency** across multiple API integrations
-   **Use battle-tested utilities** for common SDK development tasks
-   **Benefit from 100% test coverage** and production-ready code quality

## Installation

```bash
pip install sdk-creator
# or using uv
uv add sdk-creator
```

## Quick Start - Building Your First SDK

Here's how to build a clean, typed SDK wrapper around a Users API:

### 1. Define Your Models

```python
# models/responses.py
from sdk_creator.toolkit import SdkModel, CamelCaseAliasMixin
from typing import List, Optional

class User(CamelCaseAliasMixin):
    """User model with automatic camelCase API field mapping."""
    user_id: int        # Maps to "userId" in API
    full_name: str      # Maps to "fullName" in API
    email_address: str  # Maps to "emailAddress" in API
    is_active: bool     # Maps to "isActive" in API

class UserList(SdkModel):
    """User list response with enhanced SDK model features."""
    users: List[User]
    total_count: int    # Maps to "totalCount" in API
    current_page: int   # Maps to "currentPage" in API

class CreateUserResponse(BaseModel):
    user: User
    message: str
```

### 2. Create Your SDK Class

```python
# users_sdk.py
from typing import Optional, Self, Any
from sdk_creator import AsyncRestAdapter
from sdk_creator.errors import ApiRaisedFromStatusError
from sdk_creator.toolkit import SdkModel, CamelCaseAliasMixin, join_endpoints
from .models.responses import User, UserList, CreateUserResponse

class UsersSDK:
    def __init__(self, api_key: str, base_url: str = "api.example.com"):
        """Initialize the Users SDK.

        Args:
            api_key: Your API key for authentication
            base_url: API hostname (default: api.example.com)
        """
        self._adapter = AsyncRestAdapter(
            hostname=base_url,
            api_version="v1",
            endpoint_prefix="users",  # all endpoints will be prefixed with "users"
            api_key=api_key,
            scheme="https"
        )

    async def get_users(self, page: int = 1, limit: int = 10) -> UserList:
        """Get paginated list of users."""
        response = await self._adapter.get("users", page=page, limit=limit)
        return UserList.model_validate(response.data)

    async def get_user(self, user_id: int) -> Optional[User]:
        """Get a specific user by ID."""
        try:
            response = await self._adapter.get(f"users/{user_id}")
            return User.model_validate(response.data)
        except ApiRaisedFromStatusError as e:
            if e.status_code == 404:
                return None
            raise

    async def create_user(self, name: str, email: str) -> CreateUserResponse:
        """Create a new user."""
        data = {"name": name, "email": email}
        response = await self._adapter.post("users", data=data)
        return CreateUserResponse.model_validate(response.data)

    async def update_user(self, user_id: int, **updates) -> User:
        """Update user information."""
        response = await self._adapter.patch(f"users/{user_id}", data=updates)
        return User.model_validate(response.data)

    async def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        try:
            await self._adapter.delete(f"users/{user_id}")
            return True
        except ApiRaisedFromStatusError as e:
            if e.status_code == 404:
                return False
            raise

    async def close(self):
        """Close the HTTP client."""
        await self._adapter.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()
```

### 3. Use Your SDK

```python
import asyncio
from users_sdk import UsersSDK

async def main():
    async with UsersSDK(api_key="your-api-key") as sdk:
        # Get users with strong typing
        users = await sdk.get_users(page=1, limit=5)
        print(f"Found {users.total} users")

        # Get specific user (handles 404 gracefully)
        user = await sdk.get_user(123)
        if user:
            print(f"User: {user.name} ({user.email})")

        # Create new user
        new_user = await sdk.create_user(
            name="John Doe",
            email="john@example.com"
        )
        print(f"Created user: {new_user.user.name}")

asyncio.run(main())
```

## Real-World Example: Azure Face API SDK

Here's how SDK Creator is used to build a production-ready Azure Face API wrapper:

```python
class PersonDirectory:
    def __init__(self, azure_ai_endpoint: str, api_key: str):
        hostname = self._extract_hostname(azure_ai_endpoint) + "/face"
        self._adapter = AsyncRestAdapter(
            hostname=hostname,
            api_version="v1.2-preview.1",
            api_key=api_key,
            scheme="https"
        )

    async def get_persons(self, start: str | None = None, top: int = 10) -> PersonDirectoryPersons:
        """List all persons with strong typing and validation."""
        response = await self._adapter.get("persons", start=start, top=top)
        return PersonDirectoryPersons.model_validate({"persons": response.data})

    async def create_person(self, name: str, user_data: str | dict) -> CreatePersonResult:
        """Create person with automatic JSON serialization."""
        if isinstance(user_data, dict):
            user_data = json.dumps(user_data)

        person_data = PersonDirectoryCreate(name=name, user_data=user_data)
        response = await self._adapter.post("persons", data=person_data.model_dump())
        return CreatePersonResult.model_validate(response.data)

    async def delete_person(self, person_id: str, *, raise_not_found: bool = True) -> bool:
        """Delete person with graceful 404 handling."""
        try:
            await self._adapter.delete(f"persons/{person_id}")
            return True
        except ApiRaisedFromStatusError as err:
            if err.status_code == 404 and not raise_not_found:
                return False
            raise PersonDirectoryNotFoundError(f"Person {person_id} not found") from err
```

## Key Features for SDK Development

### 🏗️ **Composition Over Inheritance**

-   Use `AsyncRestAdapter` as a private component in your SDK classes
-   Build clean, domain-specific interfaces on top of HTTP operations
-   Maintain separation between transport logic and business logic

### 🔐 **Flexible Authentication**

Configure authentication once in your SDK constructor:

```python
class MySDK:
    def __init__(self, api_key: str, environment: str = "production"):
        base_urls = {
            "production": "api.example.com",
            "staging": "staging-api.example.com"
        }

        self._adapter = AsyncRestAdapter(
            hostname=base_urls[environment],
            api_key=api_key,
            headers={"User-Agent": "MySDK/1.0"}
        )
```

### 🛡️ **Comprehensive Error Handling**

Transform HTTP errors into meaningful domain exceptions with a complete error hierarchy:

```python
from sdk_creator.errors import (
    ApiRaisedFromStatusError, ApiTimeoutError,
    ApiRequestError, ApiResponseError
)

class UserNotFoundError(Exception):
    pass

class UserSDK:
    async def get_user(self, user_id: int) -> User:
        try:
            response = await self._adapter.get(f"users/{user_id}")
            return User.model_validate(response.data)
        except ApiRaisedFromStatusError as e:
            if e.status_code == 404:
                raise UserNotFoundError(f"User {user_id} not found") from e
            raise  # Re-raise other HTTP errors
        except ApiTimeoutError:
            raise TimeoutError("User service unavailable")
        except ApiRequestError as e:
            raise ConnectionError(f"Network error: {e}")
        except ApiResponseError as e:
            raise ValueError(f"Invalid response format: {e}")
```

### 📝 **Strong Typing with Pydantic**

Automatic validation and serialization of API responses:

```python
from pydantic import BaseModel, Field
from datetime import datetime

class User(BaseModel):
    id: int
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    created_at: datetime
    is_active: bool = True

    class Config:
        # Automatically convert API snake_case to Python snake_case
        allow_population_by_field_name = True
```

## 🧰 SDK Development Toolkit

SDK Creator includes a comprehensive toolkit of utilities to accelerate your SDK development:

### URL and Endpoint Utilities

```python
from sdk_creator.toolkit import url_to_hostname, join_endpoints

# extract hostname from URLs with validation
hostname = url_to_hostname("https://api.example.com/v1/users")
# returns: "api.example.com"

# intelligently join URL endpoints
endpoint = join_endpoints("api", "v1", "users", "123")
# returns: "api/v1/users/123"

# handles edge cases gracefully
endpoint = join_endpoints("/api/", "//v1//", "/users/")
# returns: "api/v1/users"
```

### Case Conversion Utilities

```python
from sdk_creator.toolkit import to_camelcase

# convert snake_case to camelCase for API compatibility
camel_field = to_camelcase("user_id")  # Returns: "userId"
camel_field = to_camelcase("created_at_timestamp")  # Returns: "createdAtTimestamp"
```

### Pydantic Model Enhancements

```python
from sdk_creator.toolkit import CamelCaseAliasMixin, SdkModel

# automatic camelCase field aliases for APIs
class UserModel(CamelCaseAliasMixin):
    user_id: int      # API field: "userId"
    created_at: str   # API field: "createdAt"
    is_active: bool   # API field: "isActive"

# enhanced base model with SDK-specific configurations
class ApiResponse(SdkModel):
    data: dict
    status: str
    # inherits from_attributes=True and arbitrary_types_allowed=True
```

### Exception Handling

```python
from sdk_creator.errors import (
    ApiError, ApiRequestError, ApiResponseError,
    ApiTimeoutError, ApiRaisedFromStatusError
)

try:
    response = await sdk.get_user(123)
except ApiRaisedFromStatusError as e:
    print(f"HTTP {e.status_code} error: {e}")
except ApiTimeoutError:
    print("Request timed out")
except ApiRequestError:
    print("Network connection failed")
except ApiResponseError:
    print("Invalid response format")
except ApiError:
    print("General API error")
```

## SDK Development Patterns

### Environment Configuration

Support multiple environments in your SDK:

```python
class MySDK:
    ENVIRONMENTS = {
        "production": "api.example.com",
        "staging": "staging-api.example.com",
        "development": "dev-api.example.com"
    }

    def __init__(self, api_key: str, environment: str = "production"):
        if environment not in self.ENVIRONMENTS:
            raise ValueError(f"Invalid environment: {environment}")

        self._adapter = AsyncRestAdapter(
            hostname=self.ENVIRONMENTS[environment],
            api_key=api_key,
            headers={"User-Agent": f"MySDK/1.0 ({environment})"}
        )
```

### Pagination Support

Handle paginated responses cleanly:

```python
from typing import AsyncIterator

class MySDK:
    async def get_all_users(self) -> AsyncIterator[User]:
        """Stream all users across multiple pages."""
        page = 1
        while True:
            response = await self._adapter.get("users", page=page, limit=100)
            user_data = UserPage.model_validate(response.data)

            for user in user_data.users:
                yield user

            if not user_data.has_next:
                break
            page += 1
```

### Custom Exception Hierarchy

Create meaningful exceptions for your domain:

```python
class MySDKError(Exception):
    """Base exception for MySDK operations."""

class ValidationError(MySDKError):
    """Invalid input data."""

class ResourceNotFoundError(MySDKError):
    """Requested resource not found."""

class RateLimitError(MySDKError):
    """Rate limit exceeded."""

    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Rate limited. Retry after {retry_after} seconds")
```

## AsyncRestAdapter API Reference

### Constructor Parameters

-   `hostname` (str): API server hostname or full endpoint URL
-   `api_version` (str): API version path (default: "v1")
-   `endpoint_prefix` (str | None): Additional prefix for all endpoints
-   `api_key` (str): API key for authentication
-   `ssl_verify` (bool): Verify SSL certificates (default: True)
-   `scheme` (Literal["http", "https"]): URL scheme (default: "https")
-   `jwt_token` (str | None): JWT token for Bearer authentication
-   `azure_api` (bool): Enable Azure API Management headers
-   `headers` (dict | None): Additional default headers

### HTTP Methods

All HTTP methods support an `expect_json_response` parameter for flexible response handling:

-   `get(endpoint, expect_json_response=True, **params)` - GET request
-   `post(endpoint, data=None, expect_json_response=True, **params)` - POST request
-   `put(endpoint, data=None, expect_json_response=False, **params)` - PUT request
-   `patch(endpoint, data=None, expect_json_response=False, **params)` - PATCH request
-   `delete(endpoint, data=None, expect_json_response=False, **params)` - DELETE request

### Exception Hierarchy

```
ApiError (base)
├── ApiRequestError        # Network/connection issues
├── ApiResponseError       # Response parsing errors
├── ApiTimeoutError        # Request timeouts
└── ApiRaisedFromStatusError  # HTTP error status codes
```

## 🧪 Quality & Testing

SDK Creator is built with production-grade quality standards:

### Test Coverage

-   **100% source code coverage** across all modules
-   **162 comprehensive tests** covering all functionality
-   **Continuous integration** with GitHub Actions
-   **Multi-Python version support** (3.11, 3.12, 3.13)

### Code Quality

-   **Zero linting errors** with Ruff
-   **Full type annotations** for excellent IDE support
-   **Professional error handling** with detailed exception hierarchy
-   **Comprehensive documentation** with practical examples

### Development Tools

-   **Automated coverage reporting** with badge integration
-   **Pre-commit hooks** for code formatting and linting
-   **Development scripts** for testing and coverage verification
-   **CI/CD workflows** for automated quality checks

### Testing Your SDK

SDK Creator provides excellent testing foundations for your own SDKs:

```python
import pytest
from unittest.mock import Mock
from your_sdk import UserSDK
from sdk_creator.errors import ApiRaisedFromStatusError

@pytest.mark.asyncio
async def test_user_not_found():
    sdk = UserSDK("test-key")

    # mock the adapter to return 404
    mock_response = Mock()
    mock_response.status_code = 404
    sdk._adapter._client.request = Mock(side_effect=ApiRaisedFromStatusError(404, "Not Found"))

    with pytest.raises(UserNotFoundError):
        await sdk.get_user(999)
```

## Best Practices

### 1. **Keep SDKs Focused**

Create separate SDK classes for different API domains:

```python
# ✅ Good - focused SDKs
class UsersSDK: ...
class OrdersSDK: ...
class PaymentsSDK: ...

# ❌ Avoid - monolithic SDK
class MegaSDK:
    def get_user(self): ...
    def create_order(self): ...
    def process_payment(self): ...
```

### 2. **Use Composition**

Keep `AsyncRestAdapter` as a private implementation detail:

```python
# ✅ Good - adapter is private
class MySDK:
    def __init__(self, api_key: str):
        self._adapter = AsyncRestAdapter(...)

# ❌ Avoid - exposing internals
class MySDK(AsyncRestAdapter):
    pass
```

### 3. **Validate Input Early**

Use Pydantic models for request validation:

```python
class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    age: int = Field(..., ge=0, le=150)

async def create_user(self, request: CreateUserRequest) -> User:
    # validation happens automatically
    response = await self._adapter.post("users", data=request.model_dump())
    return User.model_validate(response.data)
```

### ApiResponse

Response object returned by all HTTP methods:

```python
from pydantic import BaseModel

class ApiResponse(BaseModel):
    status_code: int           # HTTP status code
    data: Json                 # Parsed response data
    message: str | None        # Status message
```

## Exception Hierarchy

```text
ApiError (base)
├── ApiRequestError        # Network/connection issues
├── ApiResponseError       # Response parsing errors
├── ApiTimeoutError        # Request timeouts
└── ApiRaisedFromStatusError  # HTTP error status codes
```

## 🚀 Development & Contributing

### Development Setup

```bash
# clone and setup development environment
git clone https://github.com/mghalix/sdk-creator.git
cd sdk-creator

# install with development dependencies
uv sync --dev

# run tests with coverage
python scripts/check_coverage.py

# format and lint code
python -m ruff format .
python -m ruff check .
# or 
./scripts/lint.sh
```

### Quality Standards

-   **100% test coverage** maintained
-   **Zero linting errors** with Ruff
-   **Full type annotations** required
-   **Comprehensive tests** for all functionality

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure 100% coverage is maintained
5. Submit a pull request

## Roadmap

### 🚀 Next Release (v0.0.3)

-   **Built-in Caching** - Response caching with TTL, Redis/memory backends
-   **Rate Limiting** - Automatic rate limiting with exponential backoff
-   **Enhanced Pagination** - Auto-pagination with generators and cursor support

### 🔮 Future Versions

-   **Mock Server** - Built-in testing utilities with mock responses
-   **Circuit Breaker** - Fault tolerance patterns for resilient SDKs
-   **Metrics & Monitoring** - Request/response metrics and health checks
-   **OpenAPI Integration** - Auto-generate SDKs from OpenAPI specs

## License

This project is licensed under the MIT License.
