"""
app.py

OCR Consumer Service

Responsibilities
----------------
1. Initialize Logger
2. Initialize PostgreSQL
3. Register Signal Handlers
4. Start Kafka Consumer
5. Graceful Shutdown

No OCR logic is implemented here.
The Kafka consumer handles all processing.
"""

import signal
import sys

from ace_logger import AceLogger
from config import Config
from db_utils import DBUtils
from consumer import OCRConsumer


# ==========================================================
# Logger
# ==========================================================

logger = AceLogger.get_logger(Config.APP_NAME)


# ==========================================================
# Global Variables
# ==========================================================

db_connection = None

consumer = None


# ==========================================================
# Initialize Database
# ==========================================================

def initialize_database():
    """
    Create PostgreSQL connection.
    """

    global db_connection

    logger.info("=" * 70)
    logger.info("Initializing PostgreSQL connection...")

    db_connection = DBUtils.get_connection(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=Config.DB_NAME,
        username=Config.DB_USERNAME,
        password=Config.DB_PASSWORD
    )

    logger.info("PostgreSQL connected successfully.")


# ==========================================================
# Initialize OCR Consumer
# ==========================================================

def initialize_consumer():
    """
    Create Kafka OCR Consumer.
    """

    global consumer

    logger.info("Initializing Kafka Consumer...")

    consumer = OCRConsumer(
        db_connection=db_connection
    )

    logger.info("Kafka Consumer initialized.")


# ==========================================================
# Shutdown Handler
# ==========================================================

def shutdown(signum, frame):
    """
    Gracefully stop application.
    """

    logger.info("=" * 70)
    logger.info(f"Received signal : {signum}")
    logger.info("Stopping OCR Consumer...")

    try:

        if consumer is not None:
            consumer.stop()

    except Exception:

        logger.exception("Error while stopping consumer.")

    try:

        if db_connection is not None:
            DBUtils.close(db_connection)

    except Exception:

        logger.exception("Error while closing database.")

    logger.info("Application stopped successfully.")

    logger.info("=" * 70)

    sys.exit(0)


# ==========================================================
# Register Signals
# ==========================================================

def register_signals():
    """
    Register OS signals.
    """

    signal.signal(signal.SIGINT, shutdown)

    signal.signal(signal.SIGTERM, shutdown)


# ==========================================================
# Main
# ==========================================================

def main():

    logger.info("=" * 70)
    logger.info("Starting OCR Consumer Service")
    logger.info("=" * 70)

    try:

        initialize_database()

        initialize_consumer()

        register_signals()

        logger.info("Listening Kafka Topic...")

        consumer.start()

    except KeyboardInterrupt:

        shutdown(signal.SIGINT, None)

    except Exception as ex:

        logger.exception(f"Application crashed : {ex}")

        shutdown(signal.SIGTERM, None)


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":

    main()