from flask import Blueprint, request, jsonify
import os
import bcrypt

from validators import Validators
from ace_logger import AceLogger
from db_utils import DBUtils

register_bp = Blueprint("register", __name__)

logger = AceLogger.get_logger("auth_service")


@register_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new application user.

    Flow:
        1. Validate request body.
        2. Check duplicate email.
        3. Hash password.
        4. Insert user.
        5. Return response.
    """

    logger.info("Register request received.")

    connection = None

    try:

        data = request.get_json()

        if not data:
            logger.warning("Request body is empty.")

            return jsonify({
                "status": "error",
                "message": "Request body cannot be empty."
            }), 400

        # ------------------------------------------
        # Validate Request
        # ------------------------------------------

        status, message = Validators.validate_registration(data)

        if not status:

            logger.warning(message)

            return jsonify({
                "status": "error",
                "message": message
            }), 400

        name = data["name"].strip()
        email = data["email"].strip().lower()
        password = data["password"]
        role = data["role"]

        # ------------------------------------------
        # Create Database Connection
        # ------------------------------------------

        connection = DBUtils.get_connection(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            username=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

        logger.info("Database connected successfully.")

        # ------------------------------------------
        # Check Existing Email
        # ------------------------------------------

        logger.info(f"Checking existing user : {email}")

        select_query = """
            SELECT id
            FROM users
            WHERE email = %s
        """

        result = DBUtils.execute(
            connection=connection,
            query=select_query,
            params=(email,)
        )

        if result:

            logger.warning("Email already exists.")

            return jsonify({
                "status": "error",
                "message": "Email already registered."
            }), 409

        # ------------------------------------------
        # Hash Password
        # ------------------------------------------

        logger.info("Hashing password.")

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # ------------------------------------------
        # Insert User
        # ------------------------------------------

        logger.info("Creating new user.")

        insert_query = """
            INSERT INTO users
            (
                name,
                email,
                password_hash,
                role,
                is_active,
                created_at,
                updated_at
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                TRUE,
                NOW(),
                NOW()
            )
        """

        rows = DBUtils.execute(
            connection=connection,
            query=insert_query,
            params=(
                name,
                email,
                password_hash,
                role
            )
        )

        if rows == 0:

            logger.error("User registration failed.")

            return jsonify({
                "status": "error",
                "message": "Unable to register user."
            }), 500

        logger.info(f"User '{email}' registered successfully.")

        return jsonify({
            "status": "success",
            "message": "User registered successfully."
        }), 201

    except Exception as ex:

        logger.exception(f"Register API failed : {ex}")

        return jsonify({
            "status": "error",
            "message": "Internal Server Error"
        }), 500

    finally:

        if connection:

            DBUtils.close(connection)