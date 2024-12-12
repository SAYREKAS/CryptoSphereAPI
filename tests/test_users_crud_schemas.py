import hashlib

import pytest
from pydantic import ValidationError

from api.schemas.users_crud_schemas import CommonFieldsValidator, UserInfoSchema, AllUsersSchema, reserved_names


# Test username validation
def test_valid_username():
    valid_usernames = [
        "user_name123",
        "user.name",
        "valid_user_1",
        "username123",
    ]
    for username in valid_usernames:
        user = CommonFieldsValidator(username=username, email="test@example.com", password="Valid123!")
        assert user.username == username.lower()


def test_invalid_username_special_chars():
    invalid_usernames = [
        "invalid@name",  # contains special character '@'
        "user name",  # contains space
        ".startdot",  # starts with dot
        "enddot.",  # ends with dot
        "_startunderscore",  # starts with underscore
    ]
    for username in invalid_usernames:
        print(username)
        with pytest.raises(ValidationError):
            CommonFieldsValidator(username=username, email="test@example.com", password="Valid123!")


def test_reserved_username():
    for username in reserved_names:
        with pytest.raises(ValidationError):
            CommonFieldsValidator(username=username, email="test@example.com", password="Valid123!")


# Test password validation
def test_valid_password():
    valid_passwords = [
        "Valid123!",
        "StrongPassword1$",
        "Pa$$w0rd!",
        "Val1dP@ssw0rd",
    ]
    for password in valid_passwords:
        user = CommonFieldsValidator(username="valid_user", email="test@example.com", password=password)
        assert user.password == hashlib.sha256(password.encode()).hexdigest()


def test_invalid_password_length():
    invalid_passwords = ["s" * 5, "l" * 100]
    for password in invalid_passwords:
        with pytest.raises(ValidationError):
            CommonFieldsValidator(username="valid_user", email="test@example.com", password=password)


def test_invalid_password_missing_uppercase():
    invalid_passwords = [
        "nouppercase1!",
        "lowercaseonly123!",
    ]
    for password in invalid_passwords:
        with pytest.raises(ValidationError):
            CommonFieldsValidator(username="valid_user", email="test@example.com", password=password)


def test_invalid_password_missing_lowercase():
    invalid_passwords = [
        "NOLOWERCASE123!",
        "UPPERCASEONLY123!",
    ]
    for password in invalid_passwords:
        with pytest.raises(ValidationError):
            CommonFieldsValidator(username="valid_user", email="test@example.com", password=password)


def test_invalid_password_missing_digit():
    invalid_passwords = [
        "NoDigitInPassword!",
        "PasswordWithoutDigits!",
    ]
    for password in invalid_passwords:
        with pytest.raises(ValidationError):
            CommonFieldsValidator(username="valid_user", email="test@example.com", password=password)


def test_invalid_password_missing_special_char():
    invalid_passwords = [
        "NoSpecialChar123",
        "Password123",
    ]
    for password in invalid_passwords:
        with pytest.raises(ValidationError):
            CommonFieldsValidator(username="valid_user", email="test@example.com", password=password)


# Test AllUsersSchema validation
def test_all_users_schema():
    valid_users = AllUsersSchema(users=["user1", "user2", "user3"])
    assert len(valid_users.users) == 3
    assert valid_users.users == ["user1", "user2", "user3"]

    invalid_users = ["user1", 123, "user3"]
    with pytest.raises(ValidationError):
        AllUsersSchema(users=invalid_users)


# Test UserInfoSchema (inherits CommonFieldsValidator)
def test_user_info_schema():
    valid_user = UserInfoSchema(username="validuser", email="test@example.com", password="Valid123!")
    assert valid_user.username == "validuser"
    assert valid_user.email == "test@example.com"
    assert valid_user.password == hashlib.sha256("Valid123!".encode()).hexdigest()

    with pytest.raises(ValidationError):
        UserInfoSchema(username="inv@lid", email="test@example.com", password="Valid123!")

    with pytest.raises(ValidationError):
        UserInfoSchema(username="validuser", email="invalid-email", password="Valid123!")

    with pytest.raises(ValidationError):
        UserInfoSchema(username="validuser", email="test@example.com", password="short")
