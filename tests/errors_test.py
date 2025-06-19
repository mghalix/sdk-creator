"""Comprehensive tests for the errors module."""

import pytest

from sdk_creator.errors import (
    ApiError,
    ApiRaisedFromStatusError,
    ApiRequestError,
    ApiResponseError,
    ApiTimeoutError,
)


class TestApiError:
    """Test cases for ApiError base class."""

    def test_api_error_basic(self) -> None:
        """Test basic ApiError functionality."""
        error = ApiError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    def test_api_error_inheritance(self) -> None:
        """Test ApiError inheritance from Exception."""
        error = ApiError("Test error")
        assert isinstance(error, Exception)
        assert issubclass(ApiError, Exception)

    def test_api_error_raising(self) -> None:
        """Test raising ApiError."""
        with pytest.raises(ApiError) as exc_info:
            raise ApiError("Test error")

        assert str(exc_info.value) == "Test error"

    def test_api_error_with_args(self) -> None:
        """Test ApiError with multiple arguments."""
        error = ApiError("Error", "Additional info", 42)
        assert error.args == ("Error", "Additional info", 42)

    def test_api_error_no_args(self) -> None:
        """Test ApiError with no arguments."""
        error = ApiError()
        assert str(error) == ""
        assert error.args == ()

    def test_api_error_custom_inheritance(self) -> None:
        """Test custom ApiError inheritance."""

        class CustomApiError(ApiError):
            pass

        error = CustomApiError("Custom error")
        assert isinstance(error, ApiError)
        assert isinstance(error, Exception)
        assert str(error) == "Custom error"


class TestApiRequestError:
    """Test cases for ApiRequestError class."""

    def test_api_request_error_basic(self) -> None:
        """Test basic ApiRequestError functionality."""
        error = ApiRequestError("Request failed")
        assert str(error) == "Request failed"
        assert isinstance(error, ApiError)
        assert isinstance(error, Exception)

    def test_api_request_error_inheritance(self) -> None:
        """Test ApiRequestError inheritance."""
        assert issubclass(ApiRequestError, ApiError)
        assert issubclass(ApiRequestError, Exception)

    def test_api_request_error_raising(self) -> None:
        """Test raising ApiRequestError."""
        with pytest.raises(ApiRequestError) as exc_info:
            raise ApiRequestError("Connection failed")

        assert str(exc_info.value) == "Connection failed"

    def test_api_request_error_catch_as_api_error(self) -> None:
        """Test that ApiRequestError can be caught as ApiError."""
        with pytest.raises(ApiError):
            raise ApiRequestError("Network error")

    def test_api_request_error_with_multiple_args(self) -> None:
        """Test ApiRequestError with multiple arguments."""
        error = ApiRequestError("DNS resolution failed", "example.com", 404)
        assert error.args == ("DNS resolution failed", "example.com", 404)

    def test_api_request_error_no_args(self) -> None:
        """Test ApiRequestError with no arguments."""
        error = ApiRequestError()
        assert str(error) == ""
        assert isinstance(error, ApiError)

    def test_api_request_error_scenarios(self) -> None:
        """Test ApiRequestError for various network scenarios."""
        # DNS resolution failure
        dns_error = ApiRequestError("DNS resolution failed for api.example.com")
        assert "DNS resolution failed" in str(dns_error)

        # connection timeout
        timeout_error = ApiRequestError("Connection timeout after 30s")
        assert "timeout" in str(timeout_error)

        # network unreachable
        network_error = ApiRequestError("Network unreachable")
        assert "unreachable" in str(network_error)


class TestApiResponseError:
    """Test cases for ApiResponseError class."""

    def test_api_response_error_basic(self) -> None:
        """Test basic ApiResponseError functionality."""
        error = ApiResponseError("Invalid JSON response")
        assert str(error) == "Invalid JSON response"
        assert isinstance(error, ApiError)
        assert isinstance(error, Exception)

    def test_api_response_error_inheritance(self) -> None:
        """Test ApiResponseError inheritance."""
        assert issubclass(ApiResponseError, ApiError)
        assert issubclass(ApiResponseError, Exception)

    def test_api_response_error_raising(self) -> None:
        """Test raising ApiResponseError."""
        with pytest.raises(ApiResponseError) as exc_info:
            raise ApiResponseError("Malformed response")

        assert str(exc_info.value) == "Malformed response"

    def test_api_response_error_catch_as_api_error(self) -> None:
        """Test that ApiResponseError can be caught as ApiError."""
        with pytest.raises(ApiError):
            raise ApiResponseError("Parse error")

    def test_api_response_error_with_multiple_args(self) -> None:
        """Test ApiResponseError with multiple arguments."""
        error = ApiResponseError("JSON decode error", "line 15", "invalid character")
        assert error.args == ("JSON decode error", "line 15", "invalid character")

    def test_api_response_error_no_args(self) -> None:
        """Test ApiResponseError with no arguments."""
        error = ApiResponseError()
        assert str(error) == ""
        assert isinstance(error, ApiError)

    def test_api_response_error_scenarios(self) -> None:
        """Test ApiResponseError for various parsing scenarios."""
        # invalid JSON
        json_error = ApiResponseError(
            "Invalid JSON: unexpected character at position 15"
        )
        assert "JSON" in str(json_error) and "position 15" in str(json_error)

        # unexpected format
        format_error = ApiResponseError("Expected JSON object, got array")
        assert "Expected JSON object" in str(format_error)

        # empty response
        empty_error = ApiResponseError("Empty response body")
        assert "Empty response" in str(empty_error)


class TestApiRaisedFromStatusError:
    """Test cases for ApiRaisedFromStatusError class."""

    def test_api_raised_from_status_error_basic(self) -> None:
        """Test basic ApiRaisedFromStatusError functionality."""
        error = ApiRaisedFromStatusError(404, "Not Found")
        assert error.status_code == 404
        assert str(error) == "Not Found"
        assert isinstance(error, ApiError)
        assert isinstance(error, Exception)

    def test_api_raised_from_status_error_inheritance(self) -> None:
        """Test ApiRaisedFromStatusError inheritance."""
        assert issubclass(ApiRaisedFromStatusError, ApiError)
        assert issubclass(ApiRaisedFromStatusError, Exception)

    def test_api_raised_from_status_error_raising(self) -> None:
        """Test raising ApiRaisedFromStatusError."""
        with pytest.raises(ApiRaisedFromStatusError) as exc_info:
            raise ApiRaisedFromStatusError(500, "Internal Server Error")

        error = exc_info.value
        assert error.status_code == 500
        assert str(error) == "Internal Server Error"

    def test_api_raised_from_status_error_catch_as_api_error(self) -> None:
        """Test that ApiRaisedFromStatusError can be caught as ApiError."""
        with pytest.raises(ApiError):
            raise ApiRaisedFromStatusError(401, "Unauthorized")

    @pytest.mark.parametrize(
        "status_code,message",
        [
            (400, "Bad Request"),
            (401, "Unauthorized"),
            (403, "Forbidden"),
            (404, "Not Found"),
            (422, "Unprocessable Entity"),
            (429, "Too Many Requests"),
            (500, "Internal Server Error"),
            (502, "Bad Gateway"),
            (503, "Service Unavailable"),
            (504, "Gateway Timeout"),
        ],
    )
    def test_api_raised_from_status_error_common_codes(
        self, status_code: int, message: str
    ) -> None:
        """Test ApiRaisedFromStatusError with common HTTP status codes."""
        error = ApiRaisedFromStatusError(status_code, message)
        assert error.status_code == status_code
        assert str(error) == message

    def test_api_raised_from_status_error_with_multiple_args(self) -> None:
        """Test ApiRaisedFromStatusError with multiple arguments."""
        error = ApiRaisedFromStatusError(
            422, "Validation failed", "field: name", "error: required"
        )
        assert error.status_code == 422
        assert error.args == ("Validation failed", "field: name", "error: required")

    def test_api_raised_from_status_error_no_message(self) -> None:
        """Test ApiRaisedFromStatusError with only status code."""
        error = ApiRaisedFromStatusError(404)
        assert error.status_code == 404
        assert str(error) == ""

    def test_api_raised_from_status_error_status_code_types(self) -> None:
        """Test ApiRaisedFromStatusError with various status code scenarios."""
        # client errors (4xx)
        client_error = ApiRaisedFromStatusError(400, "Bad Request")
        assert 400 <= client_error.status_code < 500

        # server errors (5xx)
        server_error = ApiRaisedFromStatusError(500, "Internal Server Error")
        assert 500 <= server_error.status_code < 600

        # edge case status codes
        edge_error = ApiRaisedFromStatusError(999, "Custom Error")
        assert edge_error.status_code == 999

    def test_api_raised_from_status_error_attribute_access(self) -> None:
        """Test accessing status_code attribute."""
        error = ApiRaisedFromStatusError(418, "I'm a teapot")

        # direct attribute access
        assert error.status_code == 418
        assert hasattr(error, "status_code")

        # attribute is an integer
        assert isinstance(error.status_code, int)

    def test_api_raised_from_status_error_repr(self) -> None:
        """Test string representation of ApiRaisedFromStatusError."""
        error = ApiRaisedFromStatusError(404, "Resource not found")
        error_str = str(error)
        assert error_str == "Resource not found"

        # test with no message
        error_no_msg = ApiRaisedFromStatusError(500)
        assert str(error_no_msg) == ""


class TestApiTimeoutError:
    """Test cases for ApiTimeoutError class."""

    def test_api_timeout_error_basic(self) -> None:
        """Test basic ApiTimeoutError functionality."""
        error = ApiTimeoutError("Request timed out after 30s")
        assert str(error) == "Request timed out after 30s"
        assert isinstance(error, ApiError)
        assert isinstance(error, Exception)

    def test_api_timeout_error_inheritance(self) -> None:
        """Test ApiTimeoutError inheritance."""
        assert issubclass(ApiTimeoutError, ApiError)
        assert issubclass(ApiTimeoutError, Exception)

    def test_api_timeout_error_raising(self) -> None:
        """Test raising ApiTimeoutError."""
        with pytest.raises(ApiTimeoutError) as exc_info:
            raise ApiTimeoutError("Connection timeout")

        assert str(exc_info.value) == "Connection timeout"

    def test_api_timeout_error_catch_as_api_error(self) -> None:
        """Test that ApiTimeoutError can be caught as ApiError."""
        with pytest.raises(ApiError):
            raise ApiTimeoutError("Timeout occurred")

    def test_api_timeout_error_with_multiple_args(self) -> None:
        """Test ApiTimeoutError with multiple arguments."""
        error = ApiTimeoutError("Timeout after 30s", "GET", "/api/users", 30.0)
        assert error.args == ("Timeout after 30s", "GET", "/api/users", 30.0)

    def test_api_timeout_error_no_args(self) -> None:
        """Test ApiTimeoutError with no arguments."""
        error = ApiTimeoutError()
        assert str(error) == ""
        assert isinstance(error, ApiError)

    def test_api_timeout_error_scenarios(self) -> None:
        """Test ApiTimeoutError for various timeout scenarios."""
        # connection timeout
        conn_timeout = ApiTimeoutError("Connection timeout after 10s")
        assert "Connection timeout" in str(conn_timeout)

        # read timeout
        read_timeout = ApiTimeoutError("Read timeout while waiting for response")
        assert "Read timeout" in str(read_timeout)

        # custom timeout duration
        custom_timeout = ApiTimeoutError("Operation timed out after 60.5 seconds")
        assert "60.5 seconds" in str(custom_timeout)


class TestErrorInteraction:
    """Test cases for error class interactions and polymorphism."""

    def test_all_errors_inherit_from_api_error(self) -> None:
        """Test that all specific errors inherit from ApiError."""
        errors = [
            ApiRequestError("test"),
            ApiResponseError("test"),
            ApiRaisedFromStatusError(500, "test"),
            ApiTimeoutError("test"),
        ]

        for error in errors:
            assert isinstance(error, ApiError)
            assert isinstance(error, Exception)

    def test_catch_all_api_errors(self) -> None:
        """Test catching all API errors with base ApiError."""
        errors_to_test = [
            ApiRequestError("Network error"),
            ApiResponseError("Parse error"),
            ApiRaisedFromStatusError(404, "Not found"),
            ApiTimeoutError("Timeout"),
        ]

        for error in errors_to_test:
            with pytest.raises(ApiError):
                raise error

    def test_error_type_identification(self) -> None:
        """Test identifying specific error types."""
        request_error = ApiRequestError("Connection failed")
        response_error = ApiResponseError("Invalid JSON")
        status_error = ApiRaisedFromStatusError(500, "Server error")
        timeout_error = ApiTimeoutError("Request timeout")

        assert isinstance(request_error, ApiRequestError)
        assert isinstance(response_error, ApiResponseError)
        assert isinstance(status_error, ApiRaisedFromStatusError)
        assert isinstance(timeout_error, ApiTimeoutError)

        # ensure they're not instances of each other
        assert not isinstance(request_error, ApiResponseError)
        assert not isinstance(response_error, ApiTimeoutError)
        assert not isinstance(status_error, ApiRequestError)
        assert not isinstance(timeout_error, ApiRaisedFromStatusError)

    def test_error_handling_patterns(self) -> None:
        """Test common error handling patterns."""

        def handle_api_error(error: Exception) -> str:
            """Example error handler function."""
            if isinstance(error, ApiRaisedFromStatusError):
                return f"HTTP {error.status_code}: {error}"
            if isinstance(error, ApiTimeoutError):
                return f"Timeout: {error}"
            if isinstance(error, ApiRequestError):
                return f"Request failed: {error}"
            if isinstance(error, ApiResponseError):
                return f"Response error: {error}"
            if isinstance(error, ApiError):
                return f"API error: {error}"
            return f"Unknown error: {error}"

        # test each error type
        assert (
            handle_api_error(ApiRaisedFromStatusError(404, "Not found"))
            == "HTTP 404: Not found"
        )
        assert handle_api_error(ApiTimeoutError("Timeout")) == "Timeout: Timeout"
        assert (
            handle_api_error(ApiRequestError("Connection failed"))
            == "Request failed: Connection failed"
        )
        assert (
            handle_api_error(ApiResponseError("Parse error"))
            == "Response error: Parse error"
        )
        assert handle_api_error(ApiError("Generic error")) == "API error: Generic error"

    def test_error_chaining(self) -> None:
        """Test error chaining and cause tracking."""
        original_exception = ValueError("Invalid input")

        try:
            raise original_exception
        except ValueError as e:
            chained_error = ApiRequestError("Request failed due to invalid input")
            chained_error.__cause__ = e

            assert chained_error.__cause__ is original_exception
            assert isinstance(chained_error.__cause__, ValueError)

    def test_error_with_context_manager(self) -> None:
        """Test error handling in context managers."""
        from types import TracebackType

        class MockApiClient:
            def __enter__(self) -> "MockApiClient":
                return self

            def __exit__(
                self,
                exc_type: type[BaseException] | None,
                exc_val: BaseException | None,
                exc_tb: TracebackType | None,
            ) -> bool:
                if exc_type is not None and not isinstance(exc_val, ApiError):
                    # convert any exception to ApiError
                    raise ApiError(f"Wrapped error: {exc_val}") from exc_val
                return False

        # test successful operation
        with MockApiClient():
            pass  # no exception

        # test exception conversion
        with pytest.raises(ApiError) as exc_info, MockApiClient():
            raise ValueError("Test error")

        assert "Wrapped error: Test error" in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, ValueError)
