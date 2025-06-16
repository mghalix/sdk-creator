"""Async REST API client with authentication and error handling."""

from collections.abc import Mapping
from json import JSONDecodeError
from typing import Any, Self

import httpx
from loguru import logger
from pydantic import HttpUrl

from ._models import ApiResponse
from ._typing import AllowedSchemes, HttpMethods, Json, QueryParam
from .errors import (
    ApiRaisedFromStatusError,
    ApiRequestError,
    ApiResponseError,
    ApiTimeoutError,
)


class AsyncRestAdapter:
    """Async REST API client with authentication and error handling.

    Supports GET, POST, PUT, PATCH, DELETE with automatic JSON handling,
    API key/JWT authentication, and comprehensive error handling.

    Example:
        ```python
        async with AsyncRestAdapter("api.example.com", api_key="key") as client:
            response = await client.get("users/123")
        ```

    """

    def __init__(
        self,
        hostname: str,
        api_version: str = "v1",
        api_key: str = "",
        ssl_verify: bool = True,
        *,
        scheme: AllowedSchemes = "https",
        jwt_token: str | None = None,
        azure_api: bool = False,
        headers: dict | None = None,
    ) -> None:
        """Initialize the AsyncRestAdapter.

        Args:
            hostname: API server hostname (e.g., "api.example.com").
            api_version: API version path. Defaults to "v1".
            api_key: Optional API key for authentication.
            ssl_verify: Whether to verify SSL certificates. Defaults to True.
            scheme: URL scheme ("http" or "https"). Defaults to "https".
            jwt_token: Optional JWT token for Bearer authentication.
            azure_api: Add required header with assiociated api key.
            headers: Additional default headers to include with all requests.

        Raises:
            ValueError: If hostname or api_version is empty.

        """
        if not hostname:
            raise ValueError("hostname cannot be empty")
        if not api_version:
            raise ValueError("api_version cannot be empty")

        self.base_url = HttpUrl.build(
            scheme=scheme,
            host=hostname,
            path=api_version,
        )
        headers = headers or {}

        if api_key:
            headers["x-api-key"] = api_key
        if azure_api:
            headers["Ocp-Apim-Subscription-Key"] = api_key
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"

        self._client = httpx.AsyncClient(
            base_url=str(self.base_url),
            headers=headers,
            verify=ssl_verify,
        )

    async def _request(
        self,
        method: HttpMethods,
        endpoint: str,
        timeout: float | None = None,
        headers: Mapping | None = None,
        graceful: bool = False,
        params: Mapping | None = None,
        data: Json = None,
        expect_json_response: bool = True,
    ) -> ApiResponse:
        """Execute HTTP request with error handling and logging.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE).
            endpoint: API endpoint path relative to base URL.
            timeout: Request timeout in seconds.
            headers: Additional headers.
            graceful: If True, don't raise exceptions for HTTP error status codes.
            params: Query parameters.
            data: JSON data for request body.
            expect_json_response: Parse response as JSON vs text.

        Returns:
            ApiResponse with status code, data, and message.

        Raises:
            ApiTimeoutError: Request timeout.
            ApiRequestError: Network/connection error.
            ApiResponseError: JSON parsing error.
            ApiRaisedFromStatusError: HTTP error status (when graceful=False).

        """
        logger.debug(self._client.base_url)

        logs_ph = {
            "pre": lambda method, url: f"{method} {url}",
            "post": lambda request_desc, success, status_code, message: ", ".join(
                (
                    request_desc,
                    f"{success=}",
                    f"{status_code}",
                    f"{message}",
                )
            ),
        }

        b = self.base_url
        url = HttpUrl.build(
            scheme=b.scheme,
            host=str(b.host),
            path=str(b.path).lstrip("/").rstrip("/") + f"/{endpoint}",
            query="&".join(f"{k}={v}" for k, v in params.items()) if params else None,
        )
        request_desc = logs_ph["pre"](method=method, url=url)
        logger.debug(request_desc)

        try:
            response = await self._client.request(
                method,
                endpoint,
                timeout=timeout,
                headers=headers,
                params=params,
                json=data,
            )
        except httpx.TimeoutException as err:
            logger.error(str(err))
            raise ApiTimeoutError("Request timed out") from err
        except httpx.RequestError as err:
            logger.error(str(err))
            raise ApiRequestError("Request failed") from err

        data_out: Json

        if expect_json_response:
            try:
                data_out = response.json()
            except (ValueError, JSONDecodeError) as err:
                raise ApiResponseError(
                    f"Bad JSON in response: {response.text}"
                ) from err
        else:
            data_out = response.text

        message = response.reason_phrase
        status_code = response.status_code
        is_success = response.is_success

        log = logger.debug if is_success else logger.error
        log(
            logs_ph["post"](
                request_desc=request_desc,
                success=is_success,
                status_code=status_code,
                message=message,
            ),
        )

        if not graceful and not is_success:
            raise ApiRaisedFromStatusError(status_code, f"{status_code}: {message}")

        return ApiResponse(
            status_code=status_code,
            data=data_out,
            message=message,
        )

    async def get(
        self,
        endpoint: str,
        headers: Mapping | None = None,
        timeout: float | None = None,
        **params: QueryParam,
    ) -> ApiResponse:
        """Send GET request to endpoint.

        Args:
            endpoint: API endpoint path.
            headers: Additional headers.
            timeout: Request timeout.
            **params: Query parameters.

        Returns:
            ApiResponse with parsed JSON data.

        """
        return await self._request(
            "GET", endpoint, headers=headers, timeout=timeout, params=params
        )

    async def post(
        self,
        endpoint: str,
        data: Json = None,
        headers: Mapping | None = None,
        timeout: float | None = None,
        **params: QueryParam,
    ) -> ApiResponse:
        """Send POST request to create/submit data.

        Args:
            endpoint: API endpoint path.
            data: JSON data for request body.
            headers: Additional headers.
            timeout: Request timeout.
            **params: Query parameters.

        Returns:
            ApiResponse with parsed JSON data.

        """
        return await self._request(
            "POST", endpoint, data=data, headers=headers, timeout=timeout, params=params
        )

    async def put(
        self,
        endpoint: str,
        data: Json = None,
        headers: Mapping | None = None,
        timeout: float | None = None,
        **params: QueryParam,
    ) -> ApiResponse:
        """Send PUT request to update/replace resource.

        Args:
            endpoint: API endpoint path.
            data: JSON data for request body.
            headers: Additional headers.
            timeout: Request timeout.
            **params: Query parameters.

        Returns:
            ApiResponse with parsed JSON data.

        """
        return await self._request(
            "PUT", endpoint, data=data, headers=headers, timeout=timeout, params=params
        )

    async def patch(
        self,
        endpoint: str,
        data: Json = None,
        headers: Mapping | None = None,
        timeout: float | None = None,
        **params: QueryParam,
    ) -> ApiResponse:
        """Send PATCH request for partial updates.

        Args:
            endpoint: API endpoint path.
            data: JSON data for request body.
            headers: Additional headers.
            timeout: Request timeout.
            **params: Query parameters.

        Returns:
            ApiResponse with parsed JSON data.

        """
        return await self._request(
            "PATCH",
            endpoint,
            data=data,
            headers=headers,
            timeout=timeout,
            params=params,
        )

    async def delete(
        self,
        endpoint: str,
        data: Json = None,
        headers: Mapping | None = None,
        timeout: float | None = None,
        expect_json_response: bool = False,
        **params: QueryParam,
    ) -> ApiResponse:
        """Send DELETE request to remove resource.

        Args:
            endpoint: API endpoint path.
            data: Optional JSON data for request body.
            headers: Additional headers.
            timeout: Request timeout.
            expect_json_response: Parse response as JSON (default: False).
            **params: Query parameters.

        Returns:
            ApiResponse with text or JSON data.

        """
        return await self._request(
            "DELETE",
            endpoint,
            data=data,
            headers=headers,
            timeout=timeout,
            expect_json_response=expect_json_response,
            params=params,
        )

    async def close(self) -> None:
        """Close HTTP client and release resources."""
        await self._client.aclose()

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit. Automatically closes client."""
        await self.close()
