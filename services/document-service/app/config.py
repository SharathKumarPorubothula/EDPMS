"""
config.py

Application configuration.

Reads all required values from environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Central configuration class.
    """

    # ==========================
    # Input Folder
    # ==========================

    INPUT_FOLDER = os.getenv(
        "INPUT_FOLDER",
        r"C:\Users\User\Desktop\New folder (2)\EDPMS\input"
    )

    WEBFILES_PATH = os.getenv(
        "WEBFILES_PATH",
        r"C:\Users\User\Desktop\New folder (2)\EDPMS\webfiles"
    )

    # ==========================
    # Worker Configuration
    # ==========================

    POLL_INTERVAL = int(
        os.getenv("POLL_INTERVAL", "300")
    )  # seconds (5 minutes)

    MAX_WORKERS = int(
        os.getenv("MAX_WORKERS", "4")
    )

    # ==========================
    # Default User
    # ==========================

    DEFAULT_USER_ID = int(
        os.getenv("DEFAULT_USER_ID", "1")
    )

    # ==========================
    # PostgreSQL
    # ==========================

    DB_HOST = os.getenv("DB_HOST")

    DB_PORT = int(
        os.getenv("DB_PORT", "5432")
    )

    DB_NAME = os.getenv("DB_NAME")

    DB_USERNAME = os.getenv("DB_USERNAME")

    DB_PASSWORD = os.getenv("DB_PASSWORD")

    # ==========================
    # Kafka
    # ==========================

    KAFKA_BOOTSTRAP_SERVERS = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS",
        "localhost:9092"
    )

    KAFKA_TOPIC = os.getenv(
        "KAFKA_TOPIC",
        "document-processing"
    )

    # ==========================
    # Image Configuration
    # ==========================

    IMAGE_FORMAT = os.getenv(
        "IMAGE_FORMAT",
        "JPEG"
    )

    IMAGE_EXTENSION = os.getenv(
        "IMAGE_EXTENSION",
        ".jpg"
    )

    IMAGE_DPI = int(
        os.getenv("IMAGE_DPI", "200")
    )

    # ==========================
    # Logging
    # ==========================

    LOG_LEVEL = os.getenv(
        "LOG_LEVEL",
        "INFO"
    )

    LOG_DIR = os.getenv(
        "LOG_DIR",
        "logs"
    )