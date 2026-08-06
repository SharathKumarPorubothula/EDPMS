"""
validators.py

This module provides reusable validation functions for user input.

Validations:
- Required fields
- Name
- Email
- Password strength
- Role

These validators are intended to be used before processing
registration requests.
"""

import re


class Validators:
    """
    Utility class containing input validation methods.
    """

    EMAIL_REGEX = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

    PASSWORD_REGEX = (
        r'^(?=.*[a-z])'
        r'(?=.*[A-Z])'
        r'(?=.*\d)'
        r'(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    )

    VALID_ROLES = [
        "Admin",
        "Maker",
        "Checker",
        "User"
    ]

    @staticmethod
    def validate_required_fields(data):
        """
        Validate required fields in request body.

        Args:
            data (dict): Incoming request JSON.

        Returns:
            tuple:
                (True, None) if validation succeeds.
                (False, message) otherwise.
        """

        required_fields = [
            "name",
            "email",
            "password",
            "role"
        ]

        for field in required_fields:
            if field not in data:
                return False, f"'{field}' is required."

            if data[field] is None:
                return False, f"'{field}' cannot be null."

            if str(data[field]).strip() == "":
                return False, f"'{field}' cannot be empty."

        return True, None

    @staticmethod
    def validate_name(name):
        """
        Validate user name.

        Rules:
        - Minimum 3 characters
        - Maximum 100 characters
        """

        if len(name.strip()) < 3:
            return False, "Name must contain at least 3 characters."

        if len(name) > 100:
            return False, "Name cannot exceed 100 characters."

        return True, None

    @staticmethod
    def validate_email(email):
        """
        Validate email format.
        """

        if not re.match(Validators.EMAIL_REGEX, email):
            return False, "Invalid email address."

        return True, None

    @staticmethod
    def validate_password(password):
        """
        Validate password strength.

        Rules:
        - Minimum 8 characters
        - One uppercase
        - One lowercase
        - One number
        - One special character
        """

        if not re.match(Validators.PASSWORD_REGEX, password):
            return (
                False,
                (
                    "Password must contain at least 8 characters, "
                    "one uppercase letter, one lowercase letter, "
                    "one number and one special character."
                )
            )

        return True, None

    @staticmethod
    def validate_role(role):
        """
        Validate user role.
        """

        if role not in Validators.VALID_ROLES:
            return (
                False,
                f"Role must be one of {Validators.VALID_ROLES}"
            )

        return True, None

    @staticmethod
    def validate_registration(data):
        """
        Validate complete registration request.

        Args:
            data (dict): Registration request body.

        Returns:
            tuple:
                (True, None) if valid.
                (False, error_message) otherwise.
        """

        status, message = Validators.validate_required_fields(data)
        if not status:
            return status, message

        status, message = Validators.validate_name(data["name"])
        if not status:
            return status, message

        status, message = Validators.validate_email(data["email"])
        if not status:
            return status, message

        status, message = Validators.validate_password(data["password"])
        if not status:
            return status, message

        status, message = Validators.validate_role(data["role"])
        if not status:
            return status, message

        return True, None