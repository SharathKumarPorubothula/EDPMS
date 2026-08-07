"""
config.py

Application configuration.

Loads configuration from environment variables and
provides default values where appropriate.

This configuration is used by:

- Kafka Consumer
- OCR Engine
- PostgreSQL
- PDF Processing
- Image Processing
- Output Generation
"""

import os


class Config:
    """
    Application Configuration
    """

    # ==========================================================
    # Application
    # ==========================================================

    APP_NAME = os.getenv("APP_NAME", "ocr_consumer")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    LOG_DIR = os.getenv("LOG_DIR", "logs")

    # ==========================================================
    # Kafka Configuration
    # ==========================================================

    KAFKA_BOOTSTRAP_SERVERS = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS",
        "localhost:9092"
    )

    KAFKA_TOPIC = os.getenv(
        "KAFKA_TOPIC",
        "document_processing"
    )

    KAFKA_GROUP_ID = os.getenv(
        "KAFKA_GROUP_ID",
        "ocr_consumer_group"
    )

    KAFKA_AUTO_OFFSET_RESET = os.getenv(
        "KAFKA_AUTO_OFFSET_RESET",
        "earliest"
    )

    ENABLE_AUTO_COMMIT = (
        os.getenv("ENABLE_AUTO_COMMIT", "True").lower()
        == "true"
    )

    # ==========================================================
    # PostgreSQL Configuration
    # ==========================================================

    DB_HOST = os.getenv("DB_HOST", "localhost")

    DB_PORT = int(os.getenv("DB_PORT", "5432"))

    DB_NAME = os.getenv(
        "DB_NAME",
        "edpms_extracted_data"
    )

    DB_USERNAME = os.getenv(
        "DB_USERNAME",
        "postgres"
    )

    DB_PASSWORD = os.getenv(
        "DB_PASSWORD",
        "postgres"
    )

    # ==========================================================
    # OCR Configuration
    # ==========================================================

    OCR_ENGINE = os.getenv(
        "OCR_ENGINE",
        "tesseract"
    )
    # Supported:
    # tesseract
    # paddleocr
    # abbyy

    OCR_LANGUAGE = os.getenv(
        "OCR_LANGUAGE",
        "eng"
    )

    OCR_DPI = int(
        os.getenv("OCR_DPI", "300")
    )

    # ==========================================================
    # ABBYY Configuration
    # ==========================================================

    ABBYY_LICENSE_PATH = os.getenv(
        "ABBYY_LICENSE_PATH",
        ""
    )

    ABBYY_PROJECT_PATH = os.getenv(
        "ABBYY_PROJECT_PATH",
        ""
    )

    # ==========================================================
    # Tesseract Configuration
    # ==========================================================

    TESSERACT_CMD = os.getenv(
        "TESSERACT_CMD",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    # ==========================================================
    # PaddleOCR Configuration
    # ==========================================================

    USE_GPU = (
        os.getenv("USE_GPU", "False").lower()
        == "true"
    )

    # ==========================================================
    # Folder Paths
    # ==========================================================

    WEBFILES_PATH = os.getenv(
        "WEBFILES_PATH",
        r"C:\Users\User\Desktop\New folder (2)\EDPMS\webfiles"
    )

    OUTPUT_FOLDER = os.getenv(
        "OUTPUT_FOLDER",
        "output"
    )

    TEMP_FOLDER = os.getenv(
        "TEMP_FOLDER",
        "temp"
    )

    # ==========================================================
    # Image Processing
    # ==========================================================

    IMAGE_FORMAT = os.getenv(
        "IMAGE_FORMAT",
        "PNG"
    )

    IMAGE_EXTENSION = os.getenv(
        "IMAGE_EXTENSION",
        ".png"
    )

    IMAGE_DPI = int(
        os.getenv("IMAGE_DPI", "300")
    )

    IMAGE_QUALITY = int(
        os.getenv("IMAGE_QUALITY", "95")
    )

    # ==========================================================
    # OCR Validation
    # ==========================================================

    MIN_CONFIDENCE = float(
        os.getenv("MIN_CONFIDENCE", "70")
    )

    REMOVE_EMPTY_LINES = (
        os.getenv("REMOVE_EMPTY_LINES", "True").lower()
        == "true"
    )

    REMOVE_SPECIAL_CHARACTERS = (
        os.getenv(
            "REMOVE_SPECIAL_CHARACTERS",
            "False"
        ).lower() == "true"
    )

    # ==========================================================
    # Thread Configuration
    # ==========================================================

    MAX_WORKERS = int(
        os.getenv("MAX_WORKERS", "4")
    )

    # ==========================================================
    # Output Files
    # ==========================================================

    GENERATE_JSON = (
        os.getenv("GENERATE_JSON", "True").lower()
        == "true"
    )

    GENERATE_XML = (
        os.getenv("GENERATE_XML", "True").lower()
        == "true"
    )

    GENERATE_TXT = (
        os.getenv("GENERATE_TXT", "True").lower()
        == "true"
    )

    GENERATE_SEARCHABLE_PDF = (
        os.getenv(
            "GENERATE_SEARCHABLE_PDF",
            "False"
        ).lower() == "true"
    )

    # ==========================================================
    # Supported File Types
    # ==========================================================

    SUPPORTED_FILE_TYPES = [
        ".pdf"
    ]