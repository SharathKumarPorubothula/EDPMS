"""
jwt_utils.py

Utility class for generating and validating JSON Web Tokens (JWT).

Features:
    - Generate JWT access token.
    - Verify JWT token.
    - Decode JWT payload.

Environment Variables:
    JWT_SECRET_KEY
    JWT_ALGORITHM
    JWT_EXPIRY_MINUTES
"""

import os
import jwt
from datetime import datetime, timedelta

from ace_logger import AceLogger


logger = AceLogger.get_logger("jwt_utils")


class JWTUtils:
    """
    Utility class for JWT token operations.
    """

    @staticmethod
    def generate_token(user_id, email, role):
        """
        Generate JWT access token.

        Args:
            user_id (int):
                User ID.

            email (str):
                User email.

            role (str):
                User role.

        Returns:
            str:
                JWT access token.
        """

        try:

            payload = {
                "user_id": user_id,
                "email": email,
                "role": role,
                "exp": datetime.utcnow() + timedelta(
                    minutes=int(os.getenv("JWT_EXPIRY_MINUTES", 60))
                )
            }

            token = jwt.encode(
                payload,
                os.getenv("JWT_SECRET_KEY"),
                algorithm=os.getenv("JWT_ALGORITHM", "HS256")
            )

            logger.info("JWT token generated successfully.")

            return token

        except Exception as ex:

            logger.exception(f"Failed to generate JWT token: {ex}")

            raise

    @staticmethod
    def verify_token(token):
        """
        Verify JWT token.

        Args:
            token (str):
                JWT token.

        Returns:
            dict:
                Decoded JWT payload.

        Raises:
            jwt.ExpiredSignatureError:
                Token expired.

            jwt.InvalidTokenError:
                Invalid token.
        """

        try:

            payload = jwt.decode(
                token,
                os.getenv("JWT_SECRET_KEY"),
                algorithms=[
                    os.getenv("JWT_ALGORITHM", "HS256")
                ]
            )

            logger.info("JWT token verified successfully.")

            return payload

        except jwt.ExpiredSignatureError:

            logger.warning("JWT token expired.")

            raise

        except jwt.InvalidTokenError:

            logger.warning("Invalid JWT token.")

            raise

    @staticmethod
    def decode_token(token):
        """
        Decode JWT token.

        Args:
            token (str):
                JWT token.

        Returns:
            dict:
                Decoded JWT payload.
        """

        return JWTUtils.verify_token(token)