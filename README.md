# SDK Creator

[![PyPI version](https://badge.fury.io/py/sdk-creator.svg)](https://badge.fury.io/py/sdk-creator)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A foundation for building **strongly-typed Python SDKs** around existing REST
APIs. SDK Creator provides the async HTTP foundation while you focus on
building clean, Pydantic-powered API wrappers with comprehensive error handling
and type safety.

## Why SDK Creator?

Instead of manually handling HTTP requests, JSON parsing, and error handling
for every API integration, SDK Creator lets you:

- **Build clean SDK interfaces** with strong typing and Pydantic models
- **Focus on business logic** rather than HTTP boilerplate
- **Leverage async/await** for high-performance API calls
- **Handle errors gracefully** with specific exception types
- **Maintain consistency** across multiple API integrations

## Installation

```bash
pip install sdk-creator
```

## Quick Start - Building Your First SDK

Here's how to build a clean, typed SDK wrapper around a Users API:

### 1. Define Your Models

```python
# models/responses.py
from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    id: int
    name: str
    email: str
    active: bool

class UserList(BaseModel):
    users: List[User]
    total: int
    page: int

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
- Use `AsyncRestAdapter` as a private component in your SDK classes
- Build clean, domain-specific interfaces on top of HTTP operations
- Maintain separation between transport logic and business logic

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
Transform HTTP errors into meaningful domain exceptions:

```python
from sdk_creator.errors import ApiRaisedFromStatusError

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
- `hostname` (str): API server hostname
- `api_version` (str): API version path (default: "v1")
- `api_key` (str): API key for authentication
- `ssl_verify` (bool): Verify SSL certificates (default: True)
- `scheme` (Literal["http", "https"]): URL scheme (default: "https")
- `jwt_token` (str | None): JWT token for Bearer authentication
- `azure_api` (bool): Enable Azure API Management headers
- `headers` (dict | None): Additional default headers

### HTTP Methods
- `get(endpoint, **params)` - GET request
- `post(endpoint, data=None, **params)` - POST request
- `put(endpoint, data=None, **params)` - PUT request
- `patch(endpoint, data=None, **params)` - PATCH request
- `delete(endpoint, data=None, **params)` - DELETE request


### Exception Hierarchy
```
ApiError (base)
├── ApiRequestError        # Network/connection issues
├── ApiResponseError       # Response parsing errors
├── ApiTimeoutError        # Request timeouts
└── ApiRaisedFromStatusError  # HTTP error status codes
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
    # Validation happens automatically
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

## Roadmap

### 🚀 Next Release
- **Built-in Caching** - Response caching with TTL, Redis/memory backends
- **Rate Limiting** - Automatic rate limiting with exponential backoff
- **Enhanced Pagination** - Auto-pagination with generators and cursor support
- **Test Coverage** - Comprehensive test suite with 100% coverage

### 🔮 Future Versions
- **Mock Server** - Built-in testing utilities with mock responses
- **Circuit Breaker** - Fault tolerance patterns for resilient SDKs
- **Metrics & Monitoring** - Request/response metrics and health checks
- **OpenAPI Integration** - Auto-generate SDKs from OpenAPI specs

## License
This project is licensed under the MIT License.
