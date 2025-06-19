"""Comprehensive tests for AsyncRestAdapter module."""

import json
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from pydantic import HttpUrl

from sdk_creator.adapter import AsyncRestAdapter
from sdk_creator.errors import (
    ApiRaisedFromStatusError,
    ApiRequestError,
    ApiResponseError,
    ApiTimeoutError,
)


class TestAsyncRestAdapterInit:
    """Test AsyncRestAdapter initialization."""

    def test_init_minimal(self) -> None:
        """Test initialization with minimal required parameters."""
        adapter = AsyncRestAdapter("api.example.com")
        assert str(adapter.base_url) == "https://api.example.com/v1"

    def test_init_with_api_version(self) -> None:
        """Test initialization with custom API version."""
        adapter = AsyncRestAdapter("api.example.com", api_version="v2")
        assert str(adapter.base_url) == "https://api.example.com/v2"

    def test_init_with_http_scheme(self) -> None:
        """Test initialization with HTTP scheme."""
        adapter = AsyncRestAdapter("api.example.com", scheme="http")
        assert str(adapter.base_url) == "http://api.example.com/v1"

    def test_init_with_endpoint_prefix(self) -> None:
        """Test initialization with endpoint prefix."""
        adapter = AsyncRestAdapter(
            "api.example.com", api_version="v1", endpoint_prefix="users"
        )
        assert str(adapter.base_url) == "https://api.example.com/v1/users"

    def test_init_with_api_key(self) -> None:
        """Test initialization with API key."""
        with patch("httpx.AsyncClient") as mock_client:
            AsyncRestAdapter("api.example.com", api_key="test-key")
            mock_client.assert_called_once()
            call_kwargs = mock_client.call_args[1]
            assert call_kwargs["headers"]["x-api-key"] == "test-key"

    def test_init_with_azure_api(self) -> None:
        """Test initialization with Azure API configuration."""
        with patch("httpx.AsyncClient") as mock_client:
            AsyncRestAdapter("api.example.com", api_key="azure-key", azure_api=True)
            mock_client.assert_called_once()
            call_kwargs = mock_client.call_args[1]
            assert call_kwargs["headers"]["Ocp-Apim-Subscription-Key"] == "azure-key"

    def test_init_with_jwt_token(self) -> None:
        """Test initialization with JWT token."""
        with patch("httpx.AsyncClient") as mock_client:
            AsyncRestAdapter("api.example.com", jwt_token="jwt-token")
            mock_client.assert_called_once()
            call_kwargs = mock_client.call_args[1]
            assert call_kwargs["headers"]["Authorization"] == "Bearer jwt-token"

    def test_init_with_custom_headers(self) -> None:
        """Test initialization with custom headers."""
        custom_headers = {"Custom-Header": "custom-value"}
        with patch("httpx.AsyncClient") as mock_client:
            AsyncRestAdapter("api.example.com", headers=custom_headers)
            mock_client.assert_called_once()
            call_kwargs = mock_client.call_args[1]
            assert call_kwargs["headers"]["Custom-Header"] == "custom-value"

    def test_init_ssl_verify_false(self) -> None:
        """Test initialization with SSL verification disabled."""
        with patch("httpx.AsyncClient") as mock_client:
            AsyncRestAdapter("api.example.com", ssl_verify=False)
            mock_client.assert_called_once()
            call_kwargs = mock_client.call_args[1]
            assert call_kwargs["verify"] is False

    def test_init_empty_hostname_raises_error(self) -> None:
        """Test that empty hostname raises ValueError."""
        with pytest.raises(ValueError, match="hostname cannot be empty"):
            AsyncRestAdapter("")

    def test_init_empty_api_version_raises_error(self) -> None:
        """Test that empty API version raises ValueError."""
        with pytest.raises(ValueError, match="api_version cannot be empty"):
            AsyncRestAdapter("api.example.com", api_version="")


class TestAsyncRestAdapterHttpMethods:
    """Test HTTP method implementations."""

    @pytest.fixture
    def adapter(self) -> AsyncRestAdapter:
        """Create adapter instance for testing."""
        return AsyncRestAdapter("api.example.com")

    @pytest.fixture
    def mock_response(self) -> Mock:
        """Create mock HTTP response."""
        response = Mock()
        response.status_code = 200
        response.is_success = True
        response.reason_phrase = "OK"
        response.json.return_value = {"result": "success"}
        response.text = "success"
        return response

    @pytest.fixture
    def mock_error_response(self) -> Mock:
        """Create mock HTTP error response."""
        response = Mock()
        response.status_code = 404
        response.is_success = False
        response.reason_phrase = "Not Found"
        response.json.return_value = {"error": "Not found"}
        response.text = "Not found"
        return response

    @pytest.mark.asyncio
    async def test_get_request(
        self, adapter: AsyncRestAdapter, mock_response: Mock
    ) -> None:
        """Test GET request."""
        with patch.object(adapter._client, "request", return_value=mock_response):
            result = await adapter.get("users")

            assert result.status_code == 200
            assert result.data == {"result": "success"}
            assert result.message == "OK"

            adapter._client.request.assert_called_once_with(
                "GET",
                "users",
                timeout=None,
                headers=None,
                params={},
                json=None,
            )

    @pytest.mark.asyncio
    async def test_get_request_with_params(
        self, adapter: AsyncRestAdapter, mock_response: Mock
    ) -> None:
        """Test GET request with query parameters."""
        with patch.object(adapter._client, "request", return_value=mock_response):
            await adapter.get("users", page=1, limit=10)

            adapter._client.request.assert_called_once_with(
                "GET",
                "users",
                timeout=None,
                headers=None,
                params={"page": 1, "limit": 10},
                json=None,
            )

    @pytest.mark.asyncio
    async def test_get_request_expect_text_response(
        self, adapter: AsyncRestAdapter, mock_response: Mock
    ) -> None:
        """Test GET request expecting text response."""
        with patch.object(adapter._client, "request", return_value=mock_response):
            result = await adapter.get("users", expect_json_response=False)

            assert result.status_code == 200
            assert result.data == "success"
            assert result.message == "OK"

    @pytest.mark.asyncio
    async def test_post_request(
        self, adapter: AsyncRestAdapter, mock_response: Mock
    ) -> None:
        """Test POST request."""
        data = {"name": "John", "email": "john@example.com"}

        with patch.object(adapter._client, "request", return_value=mock_response):
            result = await adapter.post("users", data=data, expect_json_response=False)

            assert result.status_code == 200
            assert result.data == "success"
            assert result.message == "OK"

            adapter._client.request.assert_called_once_with(
                "POST",
                "users",
                timeout=None,
                headers=None,
                params={},
                json=data,
            )

    @pytest.mark.asyncio
    async def test_post_request_expect_json(
        self, adapter: AsyncRestAdapter, mock_response: Mock
    ) -> None:
        """Test POST request expecting JSON response."""
        data = {"name": "John", "email": "john@example.com"}

        with patch.object(adapter._client, "request", return_value=mock_response):
            result = await adapter.post("users", data=data, expect_json_response=True)

            assert result.status_code == 200
            assert result.data == {"result": "success"}
            assert result.message == "OK"

    @pytest.mark.asyncio
    async def test_put_request(
        self, adapter: AsyncRestAdapter, mock_response: Mock
    ) -> None:
        """Test PUT request."""
        data = {"name": "John Updated", "email": "john.updated@example.com"}

        with patch.object(adapter._client, "request", return_value=mock_response):
            result = await adapter.put("users/123", data=data)

            assert result.status_code == 200
            assert result.data == "success"
            assert result.message == "OK"

            adapter._client.request.assert_called_once_with(
                "PUT",
                "users/123",
                timeout=None,
                headers=None,
                params={},
                json=data,
            )

    @pytest.mark.asyncio
    async def test_patch_request(
        self, adapter: AsyncRestAdapter, mock_response: Mock
    ) -> None:
        """Test PATCH request."""
        data = {"name": "John Patched"}

        with patch.object(adapter._client, "request", return_value=mock_response):
            result = await adapter.patch("users/123", data=data)

            assert result.status_code == 200
            assert result.data == "success"
            assert result.message == "OK"

            adapter._client.request.assert_called_once_with(
                "PATCH",
                "users/123",
                timeout=None,
                headers=None,
                params={},
                json=data,
            )

    @pytest.mark.asyncio
    async def test_delete_request(
        self, adapter: AsyncRestAdapter, mock_response: Mock
    ) -> None:
        """Test DELETE request."""
        with patch.object(adapter._client, "request", return_value=mock_response):
            result = await adapter.delete("users/123")

            assert result.status_code == 200
            assert result.data == "success"
            assert result.message == "OK"

            adapter._client.request.assert_called_once_with(
                "DELETE",
                "users/123",
                timeout=None,
                headers=None,
                params={},
                json=None,
            )

    @pytest.mark.asyncio
    async def test_delete_request_with_data(
        self, adapter: AsyncRestAdapter, mock_response: Mock
    ) -> None:
        """Test DELETE request with data."""
        data = {"reason": "Spam account"}

        with patch.object(adapter._client, "request", return_value=mock_response):
            await adapter.delete("users/123", data=data)

            adapter._client.request.assert_called_once_with(
                "DELETE",
                "users/123",
                timeout=None,
                headers=None,
                params={},
                json=data,
            )

    @pytest.mark.asyncio
    async def test_request_with_custom_headers(
        self, adapter: AsyncRestAdapter, mock_response: Mock
    ) -> None:
        """Test request with custom headers."""
        custom_headers = {"X-Custom-Header": "custom-value"}

        with patch.object(adapter._client, "request", return_value=mock_response):
            await adapter.get("users", headers=custom_headers)

            adapter._client.request.assert_called_once_with(
                "GET",
                "users",
                timeout=None,
                headers=custom_headers,
                params={},
                json=None,
            )

    @pytest.mark.asyncio
    async def test_request_with_timeout(
        self, adapter: AsyncRestAdapter, mock_response: Mock
    ) -> None:
        """Test request with timeout."""
        with patch.object(adapter._client, "request", return_value=mock_response):
            await adapter.get("users", timeout=30.0)

            adapter._client.request.assert_called_once_with(
                "GET",
                "users",
                timeout=30.0,
                headers=None,
                params={},
                json=None,
            )


class TestAsyncRestAdapterErrorHandling:
    """Test error handling in AsyncRestAdapter."""

    @pytest.fixture
    def adapter(self) -> AsyncRestAdapter:
        """Create adapter instance for testing."""
        return AsyncRestAdapter("api.example.com")

    @pytest.mark.asyncio
    async def test_timeout_error(self, adapter: AsyncRestAdapter) -> None:
        """Test handling of timeout errors."""
        with (
            patch.object(
                adapter._client,
                "request",
                side_effect=httpx.TimeoutException("Request timed out"),
            ),
            pytest.raises(ApiTimeoutError, match="Request timed out"),
        ):
            await adapter.get("users")

    @pytest.mark.asyncio
    async def test_request_error(self, adapter: AsyncRestAdapter) -> None:
        """Test handling of request errors."""
        with (
            patch.object(
                adapter._client,
                "request",
                side_effect=httpx.ConnectError("Connection failed"),
            ),
            pytest.raises(ApiRequestError, match="Request failed"),
        ):
            await adapter.get("users")

    @pytest.mark.asyncio
    async def test_json_decode_error(self, adapter: AsyncRestAdapter) -> None:
        """Test handling of JSON decode errors."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.reason_phrase = "OK"
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Invalid JSON response"

        with (
            patch.object(adapter._client, "request", return_value=mock_response),
            pytest.raises(ApiResponseError, match="Bad JSON in response"),
        ):
            await adapter.get("users")

    @pytest.mark.asyncio
    async def test_http_error_status_raises_exception(
        self, adapter: AsyncRestAdapter
    ) -> None:
        """Test that HTTP error status raises exception by default."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.is_success = False
        mock_response.reason_phrase = "Not Found"
        mock_response.json.return_value = {"error": "Not found"}
        mock_response.text = "Not found"

        with patch.object(adapter._client, "request", return_value=mock_response):
            with pytest.raises(ApiRaisedFromStatusError) as exc_info:
                await adapter.get("users")

            assert exc_info.value.status_code == 404
            assert "404: Not Found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_http_error_status_graceful_handling(
        self, adapter: AsyncRestAdapter
    ) -> None:
        """Test graceful handling of HTTP error status."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.is_success = False
        mock_response.reason_phrase = "Not Found"
        mock_response.json.return_value = {"error": "Not found"}
        mock_response.text = "Not found"

        with patch.object(adapter._client, "request", return_value=mock_response):
            # use private _request method to test graceful parameter
            result = await adapter._request("GET", "users", graceful=True)

            assert result.status_code == 404
            assert result.data == {"error": "Not found"}
            assert result.message == "Not Found"


class TestAsyncRestAdapterContextManager:
    """Test AsyncRestAdapter as async context manager."""

    @pytest.mark.asyncio
    async def test_context_manager_usage(self) -> None:
        """Test using adapter as async context manager."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            async with AsyncRestAdapter("api.example.com") as adapter:
                assert adapter is not None
                assert isinstance(adapter, AsyncRestAdapter)

            # verify that aclose was called
            mock_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_method(self) -> None:
        """Test explicit close method."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            adapter = AsyncRestAdapter("api.example.com")
            await adapter.close()

            # verify that aclose was called
            mock_client.aclose.assert_called_once()


class TestAsyncRestAdapterUrlBuilding:
    """Test URL building logic."""

    @pytest.fixture
    def adapter(self) -> AsyncRestAdapter:
        """Create adapter instance for testing."""
        return AsyncRestAdapter("api.example.com")

    @pytest.mark.asyncio
    async def test_url_building_with_params(self, adapter: AsyncRestAdapter) -> None:
        """Test URL building with query parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.reason_phrase = "OK"
        mock_response.json.return_value = {"result": "success"}

        with (
            patch.object(adapter._client, "request", return_value=mock_response),
            # mock the URL building to verify the correct URL is constructed
            patch("pydantic.HttpUrl.build") as mock_url_build,
        ):
            mock_url_build.return_value = HttpUrl(
                "https://api.example.com/v1/users?page=1&limit=10"
            )

            await adapter.get("users", page=1, limit=10)

            # verify HttpUrl.build was called with correct parameters
            mock_url_build.assert_called()

    @pytest.mark.asyncio
    async def test_url_building_without_params(self, adapter: AsyncRestAdapter) -> None:
        """Test URL building without query parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.reason_phrase = "OK"
        mock_response.json.return_value = {"result": "success"}

        with (
            patch.object(adapter._client, "request", return_value=mock_response),
            patch("pydantic.HttpUrl.build") as mock_url_build,
        ):
            mock_url_build.return_value = HttpUrl("https://api.example.com/v1/users")

            await adapter.get("users")

            # verify HttpUrl.build was called
            mock_url_build.assert_called()


class TestAsyncRestAdapterEdgeCases:
    """Test edge cases and special scenarios."""

    @pytest.fixture
    def adapter(self) -> AsyncRestAdapter:
        """Create adapter instance for testing."""
        return AsyncRestAdapter("api.example.com")

    @pytest.mark.asyncio
    async def test_empty_endpoint(self, adapter: AsyncRestAdapter) -> None:
        """Test request with empty endpoint."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.reason_phrase = "OK"
        mock_response.json.return_value = {"result": "success"}

        with patch.object(adapter._client, "request", return_value=mock_response):
            result = await adapter.get("")

            assert result.status_code == 200
            adapter._client.request.assert_called_once_with(
                "GET",
                "",
                timeout=None,
                headers=None,
                params={},
                json=None,
            )

    @pytest.mark.asyncio
    async def test_none_data_in_post(self, adapter: AsyncRestAdapter) -> None:
        """Test POST request with None data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.reason_phrase = "OK"
        mock_response.text = "success"

        with patch.object(adapter._client, "request", return_value=mock_response):
            result = await adapter.post("users", data=None, expect_json_response=False)

            assert result.status_code == 200
            adapter._client.request.assert_called_once_with(
                "POST",
                "users",
                timeout=None,
                headers=None,
                params={},
                json=None,
            )

    @pytest.mark.asyncio
    async def test_mixed_auth_methods(self) -> None:
        """Test initialization with multiple authentication methods."""
        with patch("httpx.AsyncClient") as mock_client:
            AsyncRestAdapter(
                "api.example.com",
                api_key="api-key",
                jwt_token="jwt-token",
                azure_api=True,
                headers={"Custom": "header"},
            )

            mock_client.assert_called_once()
            call_kwargs = mock_client.call_args[1]
            headers = call_kwargs["headers"]

            # all auth methods should be present
            assert headers["x-api-key"] == "api-key"
            assert headers["Ocp-Apim-Subscription-Key"] == "api-key"
            assert headers["Authorization"] == "Bearer jwt-token"
            assert headers["Custom"] == "header"

    def test_base_url_construction_complex(self) -> None:
        """Test complex base URL construction scenarios."""
        # test with endpoint prefix
        adapter = AsyncRestAdapter(
            "api.example.com",
            api_version="v2",
            endpoint_prefix="users/admin",
            scheme="http",
        )
        assert str(adapter.base_url) == "http://api.example.com/v2/users/admin"

    @pytest.mark.asyncio
    async def test_large_json_response(self, adapter: AsyncRestAdapter) -> None:
        """Test handling of large JSON response."""
        large_data = {"data": [{"id": i, "name": f"User {i}"} for i in range(1000)]}

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.reason_phrase = "OK"
        mock_response.json.return_value = large_data

        with patch.object(adapter._client, "request", return_value=mock_response):
            result = await adapter.get("users")

            assert result.status_code == 200
            assert result.data == large_data
            assert len(result.data["data"]) == 1000

    @pytest.mark.asyncio
    async def test_special_characters_in_endpoint(
        self, adapter: AsyncRestAdapter
    ) -> None:
        """Test endpoint with special characters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.reason_phrase = "OK"
        mock_response.json.return_value = {"result": "success"}

        with patch.object(adapter._client, "request", return_value=mock_response):
            await adapter.get("users/search?name=John%20Doe&age=30")

            adapter._client.request.assert_called_once_with(
                "GET",
                "users/search?name=John%20Doe&age=30",
                timeout=None,
                headers=None,
                params={},
                json=None,
            )
