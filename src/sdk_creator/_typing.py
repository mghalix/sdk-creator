"""Type definitions for SDK Creator.

This module provides type aliases for common data structures used throughout
the SDK Creator package, including JSON data types, HTTP methods, and URL schemes.
"""

from typing import Any, Literal, TypeAlias

PrimativeDataType: TypeAlias = int | bool | float | str | None
"""Basic JSON-serializable types."""
QueryParam: TypeAlias = PrimativeDataType | bytes
"""Query parameter values including bytes."""
Json: TypeAlias = dict[str, Any] | list[Any] | str | int | float | bool | None
"""JSON-serializable data structure including nested objects and arrays."""
AllowedSchemes: TypeAlias = Literal["http", "https"]
"""Supported URL schemes for API connections."""
HttpMethods: TypeAlias = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
"""Supported HTTP methods for REST API operations."""
