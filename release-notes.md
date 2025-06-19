## Release Notes

### 0.0.2 (Current)

**Major Testing & Quality Improvements**

#### 🧪 Comprehensive Test Suite

-   **162 comprehensive tests** with 100% source code coverage
-   **Complete error handling testing** with 52 dedicated error tests
-   **Robust adapter testing** with 37 HTTP method and edge case tests
-   **Toolkit utility testing** with 73 comprehensive utility tests
-   **Production-ready test quality** with type annotations and best practices

#### 🛠️ New Toolkit Utilities

-   **`url_to_hostname()`** - Extract hostname from URL strings with validation
-   **`join_endpoints()`** - Intelligently join URL endpoints with proper slash handling
-   **`to_camelcase()`** - Convert snake_case to camelCase for API compatibility
-   **`CamelCaseAliasMixin`** - Pydantic mixin for automatic camelCase field aliases
-   **`SdkModel`** - Enhanced base Pydantic model with SDK-specific configurations
-   **`SdkError`** - Base exception class for SDK-related errors

#### 🔧 Enhanced Error Handling

-   **Comprehensive error hierarchy** with specific exception types:
    -   `ApiError` - Base class for all API-related errors
    -   `ApiRequestError` - Network and connection failures
    -   `ApiResponseError` - Response parsing and format errors
    -   `ApiTimeoutError` - Request timeout handling
    -   `ApiRaisedFromStatusError` - HTTP status code errors with status tracking
-   **Detailed error context** and exception chaining support

#### 🚀 Development & CI/CD Improvements

-   **100% test coverage** with automated verification
-   **Coverage badge** integration in README
-   **GitHub Actions workflow** for continuous testing
-   **Multi-Python version support** (3.11, 3.12, 3.13)
-   **Automated coverage scripts** for development workflow
-   **Professional linting** and code formatting standards

#### 📦 Core Adapter Enhancements

-   **`endpoint_prefix` parameter** for cleaner URL construction
-   **`expect_json_response` parameter** in all HTTP methods for flexible response handling
-   **Enhanced hostname handling** supporting both hostnames and full endpoint URLs
-   **Improved authentication** with Azure API support and JWT token handling
-   **Better SSL configuration** and custom header support

#### 📚 Documentation & Examples

-   **Comprehensive README** with practical SDK building examples
-   **Type hints throughout** for better IDE support and development experience
-   **Detailed API documentation** with usage examples
-   **Coverage reporting** and development workflow documentation

### 0.0.1

-   Initial release
-   Async REST client with authentication support
-   Basic error handling
-   Type hints and documentation
