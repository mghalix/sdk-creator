"""Custom exceptions for API operations.

Provides specific exception types for different API failure scenarios
to enable proper error handling and debugging.
"""


class ApiError(Exception):
    """Base exception for all API-related errors."""


class ApiRequestError(ApiError):
    """Raised when HTTP request fails due to network/connection issues.

    Examples: DNS resolution failure, connection timeout, network unreachable.
    """


class ApiResponseError(ApiError):
    """Raised when API response cannot be parsed or is malformed.

    Examples: Invalid JSON response, unexpected response format.
    """


class ApiRaisedFromStatusError(ApiError):
    """Raised when API returns HTTP error status codes.

    Examples: 400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Internal Server Error.
    """

    def __init__(self, status_code: int, *args: object) -> None:
        """Initialize the exception with HTTP status code.

        Args:
            status_code: The HTTP status code that caused the error.
            *args: Additional arguments passed to the base Exception class.

        """
        super().__init__(*args)
        self.status_code = status_code


class ApiTimeoutError(ApiError):
    """Raised when API request times out.

    Occurs when the request takes longer than the specified timeout duration.
    """
