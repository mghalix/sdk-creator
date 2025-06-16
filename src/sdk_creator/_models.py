"""Data models for SDK Creator.

This module defines Pydantic models used to represent any data structures throughout the
SDK Creator package including API responses.
"""

from pydantic import BaseModel

from ._typing import Json


class ApiResponse(BaseModel):
    """API response data structure.

    Represents the result of an HTTP API request with status information,
    response data, and optional message.

    Attributes:
        status_code: HTTP status code (200, 404, 500, etc.).
        data: Response data parsed from JSON or raw text.
        message: Optional status message or error description.

    """

    status_code: int
    data: Json = None
    message: str | None = None
