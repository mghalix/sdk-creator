"""Comprehensive tests for the toolkit module."""

import pytest
from pydantic import ValidationError

from sdk_creator import toolkit


class TestUrlToHostname:
    """Test cases for url_to_hostname function."""

    @pytest.mark.parametrize(
        "url,expected",
        [
            ("https://www.api.example.com/test", "www.api.example.com"),
            ("http://api.github.com", "api.github.com"),
            ("https://localhost:8080/api/v1", "localhost"),
            ("http://127.0.0.1:3000", "127.0.0.1"),
            ("https://sub.domain.example.org/path", "sub.domain.example.org"),
            ("https://api-v2.service.com", "api-v2.service.com"),
            ("http://example.com", "example.com"),
            ("https://a.b.c.d.e.f.g", "a.b.c.d.e.f.g"),
        ],
    )
    def test_url_to_hostname_valid_urls(self, url: str, expected: str) -> None:
        """Test url_to_hostname with valid URLs."""
        assert toolkit.url_to_hostname(url) == expected

    @pytest.mark.parametrize(
        "invalid_url",
        [
            "not-a-url",
            "ftp://example.com",  # unsupported scheme
            "",
            "//example.com",  # missing scheme
            "https://",  # empty host
            "example.com",  # missing scheme
        ],
    )
    def test_url_to_hostname_invalid_urls(self, invalid_url: str) -> None:
        """Test url_to_hostname with invalid URLs raises ValidationError."""
        with pytest.raises(ValidationError):
            toolkit.url_to_hostname(invalid_url)

    def test_url_to_hostname_with_ports(self) -> None:
        """Test url_to_hostname correctly strips ports."""
        assert (
            toolkit.url_to_hostname("https://api.example.com:8443") == "api.example.com"
        )
        assert toolkit.url_to_hostname("http://localhost:3000") == "localhost"

    def test_url_to_hostname_with_auth(self) -> None:
        """Test url_to_hostname with authentication info."""
        assert (
            toolkit.url_to_hostname("https://user:pass@api.example.com")
            == "api.example.com"
        )


class TestJoinEndpoints:
    """Test cases for join_endpoints function."""

    @pytest.mark.parametrize(
        "endpoints,expected",
        [
            # basic cases
            (("test", "ok", "random"), "test/ok/random"),
            (("users", "list"), "users/list"),
            (("api", "v1", "users", "123"), "api/v1/users/123"),
            # single endpoint
            (("single",), "single"),
            # empty endpoint handling
            (("", "test"), "/test"),
            (("test", ""), "test/"),
            (("", "", "test"), "//test"),
            # trailing slash normalization
            (("test/", "ok/", "random/"), "test/ok/random"),
            (("users/", "list"), "users/list"),
            (("api/", "/v1/", "/users/"), "api/v1/users"),
            # mixed trailing slashes
            (("test/", "go", "number/", "one"), "test/go/number/one"),
            # URLs with endpoints
            (("https://api.example.com/", "users"), "https://api.example.com/users"),
            (
                ("https://api.example.com/v1/", "users/", "123"),
                "https://api.example.com/v1/users/123",
            ),
            # Special characters
            (("api", "users-info", "user_123"), "api/users-info/user_123"),
            (("search", "query?param=value"), "search/query?param=value"),
        ],
    )
    def test_join_endpoints_parametrized(
        self, endpoints: tuple[str, ...], expected: str
    ) -> None:
        """Test join_endpoints with various endpoint combinations."""
        assert toolkit.join_endpoints(*endpoints) == expected

    def test_join_endpoints_no_args(self) -> None:
        """Test join_endpoints with no arguments."""
        assert toolkit.join_endpoints() == ""

    def test_join_endpoints_complex_url(self) -> None:
        """Test join_endpoints with complex URL structures."""
        base_url = "https://api.example.com/v2/services"
        endpoint = "users/profile"
        sub_endpoint = "settings"

        result = toolkit.join_endpoints(base_url, endpoint, sub_endpoint)
        assert result == "https://api.example.com/v2/services/users/profile/settings"

    def test_join_endpoints_preserves_query_params(self) -> None:
        """Test that join_endpoints preserves query parameters."""
        result = toolkit.join_endpoints("api", "search?q=test&limit=10")
        assert result == "api/search?q=test&limit=10"

    def test_join_endpoints_unicode(self) -> None:
        """Test join_endpoints with unicode characters."""
        result = toolkit.join_endpoints("api", "ürls", "测试")
        assert result == "api/ürls/测试"


class TestToCamelCase:
    """Test cases for to_camelcase function."""

    @pytest.mark.parametrize(
        "snake_case,expected",
        [
            # basic cases
            ("number_of_people", "numberOfPeople"),
            ("user_id", "userId"),
            ("api_key", "apiKey"),
            # single word (no underscores)
            ("numbers", "numbers"),
            ("test", "test"),
            ("a", "a"),
            # multiple underscores
            ("very_long_variable_name_here", "veryLongVariableNameHere"),
            ("first_middle_last_name", "firstMiddleLastName"),
            # leading/trailing underscores
            ("_private_var", "PrivateVar"),
            ("var_", "var"),
            ("_", ""),
            # multiple consecutive underscores
            ("test__double", "testDouble"),
            ("triple___underscore", "tripleUnderscore"),
            # empty and whitespace
            ("", ""),
            # numbers in variable names
            ("user_id_123", "userId123"),
            ("api_v2_endpoint", "apiV2Endpoint"),
            # all caps parts
            ("API_KEY", "apiKey"),
            ("HTTP_STATUS", "httpStatus"),
            # mixed case
            ("Mixed_Case_Var", "mixedCaseVar"),
        ],
    )
    def test_to_camelcase_parametrized(self, snake_case: str, expected: str) -> None:
        """Test to_camelcase with various snake_case inputs."""
        assert toolkit.to_camelcase(snake_case) == expected

    def test_to_camelcase_special_characters(self) -> None:
        """Test to_camelcase with special characters in variable names."""
        # Note: These might not be valid Python variable names but test edge cases
        assert toolkit.to_camelcase("var_with-dash") == "varWith-dash"
        assert toolkit.to_camelcase("var_with.dot") == "varWith.dot"

    def test_to_camelcase_unicode(self) -> None:
        """Test to_camelcase with unicode characters."""
        assert toolkit.to_camelcase("测试_变量") == "测试变量"
        assert toolkit.to_camelcase("café_münü") == "caféMünü"


class TestCamelCaseAliasMixin:
    """Test cases for CamelCaseAliasMixin."""

    def test_camelcase_mixin_basic(self) -> None:
        """Test basic CamelCaseAliasMixin functionality."""

        class TestModel(toolkit.SdkModel, toolkit.CamelCaseAliasMixin):
            number_of_persons: int
            long_snake_case_attribute: str

        model = TestModel(number_of_persons=10, long_snake_case_attribute="testing")

        expected_dump = {
            "numberOfPersons": 10,
            "longSnakeCaseAttribute": "testing",
        }

        assert model.model_dump() == expected_dump
        assert model == TestModel.model_validate(expected_dump)

    def test_camelcase_mixin_validation_by_alias(self) -> None:
        """Test validation using camelCase aliases."""

        class TestModel(toolkit.SdkModel, toolkit.CamelCaseAliasMixin):
            user_id: int
            full_name: str

        # should work with camelCase
        model = TestModel.model_validate({"userId": 123, "fullName": "John Doe"})
        assert model.user_id == 123
        assert model.full_name == "John Doe"

    def test_camelcase_mixin_validation_by_name(self) -> None:
        """Test validation using original snake_case names."""

        class TestModel(toolkit.SdkModel, toolkit.CamelCaseAliasMixin):
            user_id: int
            full_name: str

        # should also work with snake_case due to validate_by_name=True
        model = TestModel.model_validate({"user_id": 123, "full_name": "John Doe"})
        assert model.user_id == 123
        assert model.full_name == "John Doe"

    def test_camelcase_mixin_mixed_validation(self) -> None:
        """Test validation with mixed camelCase and snake_case."""

        class TestModel(toolkit.SdkModel, toolkit.CamelCaseAliasMixin):
            user_id: int
            full_name: str
            email_address: str

        # mix of camelCase and snake_case
        model = TestModel.model_validate(
            {"userId": 123, "full_name": "John Doe", "emailAddress": "john@example.com"}
        )
        assert model.user_id == 123
        assert model.full_name == "John Doe"
        assert model.email_address == "john@example.com"

    def test_camelcase_mixin_serialization_by_alias(self) -> None:
        """Test that serialization uses camelCase aliases."""

        class TestModel(toolkit.SdkModel, toolkit.CamelCaseAliasMixin):
            user_id: int
            creation_time: str
            is_active: bool

        model = TestModel(user_id=1, creation_time="2023-01-01", is_active=True)
        dumped = model.model_dump()

        # should use camelCase keys
        assert "userId" in dumped
        assert "creationTime" in dumped
        assert "isActive" in dumped

        # should not use snake_case keys
        assert "user_id" not in dumped
        assert "creation_time" not in dumped
        assert "is_active" not in dumped

    def test_camelcase_mixin_complex_model(self) -> None:
        """Test CamelCaseAliasMixin with nested and complex models."""

        class AddressModel(toolkit.SdkModel, toolkit.CamelCaseAliasMixin):
            street_name: str
            zip_code: str

        class UserModel(toolkit.SdkModel, toolkit.CamelCaseAliasMixin):
            user_id: int
            full_name: str
            email_address: str
            home_address: AddressModel

        address_data = {"streetName": "123 Main St", "zipCode": "12345"}
        user_data = {
            "userId": 1,
            "fullName": "John Doe",
            "emailAddress": "john@example.com",
            "homeAddress": address_data,
        }

        user = UserModel.model_validate(user_data)
        assert user.user_id == 1
        assert user.full_name == "John Doe"
        assert user.home_address.street_name == "123 Main St"
        assert user.home_address.zip_code == "12345"

        # test serialization
        serialized = user.model_dump()
        assert serialized == user_data

    def test_camelcase_mixin_optional_fields(self) -> None:
        """Test CamelCaseAliasMixin with optional fields."""

        class TestModel(toolkit.SdkModel, toolkit.CamelCaseAliasMixin):
            required_field: str
            optional_field: str | None = None
            default_value_field: int = 42

        # with all fields
        model1 = TestModel.model_validate(
            {
                "requiredField": "test",
                "optionalField": "optional",
                "defaultValueField": 100,
            }
        )
        assert model1.required_field == "test"
        assert model1.optional_field == "optional"
        assert model1.default_value_field == 100

        # with minimal fields
        model2 = TestModel.model_validate({"requiredField": "test"})
        assert model2.required_field == "test"
        assert model2.optional_field is None
        assert model2.default_value_field == 42

    def test_camelcase_mixin_validation_error(self) -> None:
        """Test that validation errors still work properly."""

        class TestModel(toolkit.SdkModel, toolkit.CamelCaseAliasMixin):
            user_id: int
            email: str

        with pytest.raises(ValidationError):
            TestModel.model_validate(
                {"userId": "not_an_int", "email": "test@example.com"}
            )

        with pytest.raises(ValidationError):
            TestModel.model_validate(
                {"email": "test@example.com"}
            )  # missing required field


class TestSdkModel:
    """Test cases for SdkModel base class."""

    def test_sdk_model_basic(self) -> None:
        """Test basic SdkModel functionality."""

        class TestModel(toolkit.SdkModel):
            name: str
            value: int

        model = TestModel(name="test", value=42)
        assert model.name == "test"
        assert model.value == 42

    def test_sdk_model_from_attributes(self) -> None:
        """Test SdkModel with from_attributes=True."""

        class TestModel(toolkit.SdkModel):
            name: str
            value: int

        class SourceObject:
            def __init__(self) -> None:
                self.name = "from_object"
                self.value = 100

        source = SourceObject()
        model = TestModel.model_validate(source)
        assert model.name == "from_object"
        assert model.value == 100

    def test_sdk_model_arbitrary_types(self) -> None:
        """Test SdkModel with arbitrary_types_allowed=True."""
        from datetime import datetime

        class TestModel(toolkit.SdkModel):
            timestamp: datetime
            custom_object: object

        now = datetime.now()
        custom_obj = {"custom": "data"}

        model = TestModel(timestamp=now, custom_object=custom_obj)
        assert model.timestamp == now
        assert model.custom_object == custom_obj

    def test_sdk_model_inheritance(self) -> None:
        """Test SdkModel inheritance."""

        class BaseTestModel(toolkit.SdkModel):
            id: int

        class ExtendedModel(BaseTestModel):
            name: str

        model = ExtendedModel(id=1, name="test")
        assert model.id == 1
        assert model.name == "test"

    def test_sdk_model_with_camelcase_mixin(self) -> None:
        """Test SdkModel combined with CamelCaseAliasMixin."""

        class TestModel(toolkit.SdkModel, toolkit.CamelCaseAliasMixin):
            user_id: int
            created_at: str

        # test from_attributes still works
        class SourceObject:
            def __init__(self) -> None:
                self.user_id = 123
                self.created_at = "2023-01-01"

        source = SourceObject()
        model = TestModel.model_validate(source)
        assert model.user_id == 123
        assert model.created_at == "2023-01-01"

        # test camelCase serialization
        dumped = model.model_dump()
        assert dumped == {"userId": 123, "createdAt": "2023-01-01"}


class TestSdkError:
    """Test cases for SdkError exception."""

    def test_sdk_error_basic(self) -> None:
        """Test basic SdkError functionality."""
        error = toolkit.SdkError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    def test_sdk_error_inheritance(self) -> None:
        """Test SdkError inheritance."""

        class CustomSdkError(toolkit.SdkError):
            pass

        error = CustomSdkError("Custom error")
        assert isinstance(error, toolkit.SdkError)
        assert isinstance(error, Exception)

    def test_sdk_error_raising(self) -> None:
        """Test raising SdkError."""
        with pytest.raises(toolkit.SdkError) as exc_info:
            raise toolkit.SdkError("Test error")

        assert str(exc_info.value) == "Test error"

    def test_sdk_error_with_args(self) -> None:
        """Test SdkError with multiple arguments."""
        error = toolkit.SdkError("Error", "Additional info", 42)
        assert error.args == ("Error", "Additional info", 42)
