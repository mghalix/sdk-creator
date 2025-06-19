"""Utilities to use as your toolkit when building your SDK."""

from pydantic import BaseModel, ConfigDict, HttpUrl


def url_to_hostname(url: str) -> str:
    """Extract hostname from a URL string.

    Args:
        url: The URL string to extract hostname from.

    Returns:
        The hostname component of the URL.

    Raises:
        ValidationError: If the URL is invalid or malformed.
    """
    return str(HttpUrl(url).host)


def join_endpoints(*endpoints: str) -> str:
    """Join multiple endpoint strings with forward slashes.

    Strips trailing slashes from each endpoint before joining to avoid double slashes,
    except when endpoints explicitly contain multiple slashes.

    Args:
        *endpoints: Variable number of endpoint strings to join.

    Returns:
        The joined endpoint path as a single string.

    Examples:
        ```python
        join_endpoints("api", "v1", "users")  # 'api/v1/users'
        join_endpoints("users/", "profile", "settings/")  # 'users/profile/settings'
        ```
    """
    return "/".join(endpoint.strip("/") for endpoint in endpoints)


def to_camelcase(snakecase_str: str) -> str:
    """Convert a variable name to camelcase representation."""
    return "".join(
        v.lower() if i == 0 else v.capitalize()
        for i, v in enumerate(snakecase_str.split("_"))
    )


class CamelCaseAliasMixin:
    """Mixin class that provides camelCase field aliases for Pydantic models.

    This mixin configures a Pydantic model to automatically generate camelCase aliases
    for snake_case field names, allowing the model to serialize and deserialize using
    camelCase field names while maintaining snake_case field names in Python code.

    The mixin enables:
    - Automatic camelCase alias generation from snake_case field names
    - Serialization using camelCase aliases
    - Validation using both original field names and camelCase aliases

    Example:
        ```python
        class UserModel(SdkModel, CamelCaseAliasMixin):
            user_id: int
            full_name: str

        user = UserModel(user_id=1, full_name="John Doe")
        user.model_dump()  # {'userId': 1, 'fullName': 'John Doe'}
        ```
    """

    model_config = ConfigDict(
        alias_generator=to_camelcase,
        serialize_by_alias=True,
        validate_by_alias=True,
        validate_by_name=True,
    )


class SdkModel(BaseModel):
    """Base Pydantic model class with SDK-specific configurations.

    This base model provides common configurations suitable for SDK development:
    - from_attributes=True: Allows model creation from objects with attributes
    - arbitrary_types_allowed=True: Permits the use of arbitrary types in model fields

    This makes it easier to work with various data sources and complex types
    commonly encountered when building SDK wrappers around APIs.

    Example:
        ```python
        class UserModel(SdkModel):
            id: int
            name: str

        # Can create from dict
        user = UserModel(id=1, name="John")
        ```

        Can also create from object with attributes
        ```python
        class DataObject:
            def __init__(self):
                self.id = 2
                self.name = "Jane"

        user2 = UserModel.model_validate(DataObject())
        ```
    """

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class SdkError(Exception):
    """Base exception class for SDK-related errors.

    This exception class serves as the base for all custom exceptions
    that may be raised by the SDK. It provides a consistent way to
    handle and identify SDK-specific errors.

    Example:
        ```python
        try:
            raise SdkError("Something went wrong with the SDK")
        except SdkError as e:
            print(f"SDK Error: {e}") # SDK Error: Something went wrong with the SDK
        ```
    """
