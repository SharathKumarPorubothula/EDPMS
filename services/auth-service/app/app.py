from flask import Flask, request, jsonify
import os
import bcrypt

from .validators import Validators
from .ace_logger import AceLogger
from .db_utils import DBUtils
from .jwt_utils import JWTUtils

app = Flask(__name__)

logger = AceLogger.get_logger("auth_service")
jwt_utils = JWTUtils()


@app.route("/register", methods=["POST"])
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
            

@app.route("/login", methods=["POST"])
def login():
    """
    Authenticate user and generate JWT access token.
    """

    logger.info("Login request received.")

    user_connection = None
    audit_connection = None

    try:

        data = request.get_json()

        if not data:

            logger.warning("Request body is empty.")

            return jsonify({
                "status": "error",
                "message": "Request body cannot be empty."
            }), 400

        # ----------------------------------------
        # Validate Request
        # ----------------------------------------

        status, message = Validators.validate_login(data)

        if not status:

            logger.warning(message)

            return jsonify({
                "status": "error",
                "message": message
            }), 400

        email = data["email"].strip().lower()
        password = data["password"]

        # ----------------------------------------
        # Connect Users Database
        # ----------------------------------------

        user_connection = DBUtils.get_connection(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            username=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

        logger.info("Connected to users database.")

        # ----------------------------------------
        # Get User
        # ----------------------------------------

        select_query = """
            SELECT
                id,
                name,
                email,
                password_hash,
                role,
                is_active
            FROM users
            WHERE email = %s
        """

        users = DBUtils.execute(
            connection=user_connection,
            query=select_query,
            params=(email,)
        )

        if not users:

            logger.warning("Invalid login attempt.")

            return jsonify({
                "status": "error",
                "message": "Invalid email or password."
            }), 401

        user = users[0]

        # ----------------------------------------
        # Check User Active
        # ----------------------------------------

        if not user["is_active"]:

            logger.warning("Inactive user login attempt.")

            return jsonify({
                "status": "error",
                "message": "User account is inactive."
            }), 403

        # ----------------------------------------
        # Verify Password
        # ----------------------------------------

        if not bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        ):

            logger.warning("Invalid password.")

            return jsonify({
                "status": "error",
                "message": "Invalid email or password."
            }), 401

        logger.info("Password verified successfully.")

        # ----------------------------------------
        # Generate JWT Token
        # ----------------------------------------

        access_token = jwt_utils.generate_token(
            user_id=user["id"],
            email=user["email"],
            role=user["role"]
        )

        logger.info("JWT token generated.")

        # ----------------------------------------
        # Update Login Time
        # ----------------------------------------

        update_query = """
            UPDATE users
            SET updated_at = NOW()
            WHERE id = %s
        """

        DBUtils.execute(
            connection=user_connection,
            query=update_query,
            params=(user["id"],)
        )

        logger.info("User login timestamp updated.")

        # ----------------------------------------
        # Audit Log
        # ----------------------------------------

        audit_connection = DBUtils.get_connection(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            username=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

        audit_query = """
            INSERT INTO audit_logs
            (
                user_id,
                action,
                module,
                ip_address,
                created_at
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                NOW()
            )
        """

        DBUtils.execute(
            connection=audit_connection,
            query=audit_query,
            params=(
                user["id"],
                "LOGIN",
                "AUTH_SERVICE",
                request.remote_addr
            )
        )

        logger.info("Audit log created.")

        return jsonify({
            "status": "success",
            "message": "Login successful.",
            "access_token": access_token
        }), 200

    except Exception as ex:

        logger.exception(f"Login failed : {ex}")

        return jsonify({
            "status": "error",
            "message": "Internal Server Error"
        }), 500

    finally:

        if user_connection:
            DBUtils.close(user_connection)

        if audit_connection:
            DBUtils.close(audit_connection)



if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8080,
        debug=True
    )