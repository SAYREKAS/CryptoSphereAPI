import hashlib

import pytest
from pydantic import ValidationError

from api.schemas.users_crud_schemas import UsernameFieldValidator, EmailFieldValidator, PasswordFieldValidator


class TestUsernameFieldValidator:
    def test_valid_username(self):
        schema = UsernameFieldValidator(username="validUser123")
        assert schema.username == "validuser123"

    def test_invalid_username_format(self):
        with pytest.raises(ValidationError):
            UsernameFieldValidator(username="invalid@user")

        with pytest.raises(ValidationError):
            UsernameFieldValidator(username="invalid user")

    def test_username_start_or_end_invalid(self):
        with pytest.raises(ValidationError):
            UsernameFieldValidator(username=".username")

        with pytest.raises(ValidationError):
            UsernameFieldValidator(username="username.")

        with pytest.raises(ValidationError):
            UsernameFieldValidator(username="_username")

        with pytest.raises(ValidationError):
            UsernameFieldValidator(username="username_")

    def test_reserved_username(self):
        with pytest.raises(ValidationError, match="This username is reserved."):
            UsernameFieldValidator(username="admin")

    def test_username_length(self):
        with pytest.raises(ValidationError, match="Username can only contain letters, numbers, dots, or underscores."):
            UsernameFieldValidator(username="a")

        with pytest.raises(ValidationError, match="Username can only contain letters, numbers, dots, or underscores."):
            UsernameFieldValidator(username="a" * 31)

    def test_username_strip_and_lower(self):
        schema = UsernameFieldValidator(username="  User_Name  ")
        assert schema.username == "user_name"


class TestEmailFieldValidator:
    def test_valid_email(self):
        schema = EmailFieldValidator(email="user@example.com")
        assert schema.email == "user@example.com"

    def test_invalid_email_format(self):
        with pytest.raises(ValidationError):
            EmailFieldValidator(email="invalid-email.com")

    def test_missing_email(self):
        with pytest.raises(ValidationError):
            EmailFieldValidator()

    def test_email_strip(self):
        schema = EmailFieldValidator(email="  user@example.com  ")
        assert schema.email == "user@example.com"

    def test_email_lower(self):
        schema = EmailFieldValidator(email="USER@examPLE.COM")
        assert schema.email == "user@example.com"


class TestPasswordFieldValidator:
    def test_valid_password(self):
        schema = PasswordFieldValidator(password="Valid1Password!")
        assert len(schema.password) == 64
        assert schema.password != "Valid1Password!"
        assert schema.password == hashlib.sha256("Valid1Password!".encode()).hexdigest()

    def test_invalid_password_length(self):
        with pytest.raises(ValidationError):
            PasswordFieldValidator(password="Short1!")

    def test_invalid_password_no_uppercase(self):
        with pytest.raises(ValidationError):
            PasswordFieldValidator(password="password1!")

    def test_invalid_password_no_lowercase(self):
        with pytest.raises(ValidationError):
            PasswordFieldValidator(password="PASSWORD1!")

    def test_invalid_password_no_digit(self):
        with pytest.raises(ValidationError):
            PasswordFieldValidator(password="Password!")

    def test_invalid_password_no_special_char(self):
        with pytest.raises(ValidationError):
            PasswordFieldValidator(password="Password1")

    def test_empty_password(self):
        with pytest.raises(ValidationError):
            PasswordFieldValidator(password=" ")

    def test_password_hashing(self):
        schema = PasswordFieldValidator(password="Valid1Password!")
        assert len(schema.password) == 64
        assert schema.password != "Valid1Password!"

    def test_password_strip(self):
        schema = PasswordFieldValidator(password="  Valid1Password!  ")
        assert schema.password != "  Valid1Password!  "
