import logging
import os
from logging.handlers import RotatingFileHandler


class AceLogger:
    
    """
    Utility class for creating and configuring application loggers.

    This class provides a reusable logger with:
    - Console logging.
    - Rotating file logging.
    - Configurable log level and log directory through environment variables.
    - A consistent log format across all services.

    Environment Variables:
        LOG_LEVEL (str):
            Logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).
            Defaults to 'INFO' if not specified.

        LOG_DIR (str):
            Directory where log files are stored.
            Defaults to 'logs' if not specified.

    Usage:
        >>> from ace_logger import AceLogger
        >>> logger = AceLogger.get_logger("auth_service")
        >>> logger.info("Application started")

    Log File:
        <LOG_DIR>/<logger_name>.log

    Note:
        Calling get_logger() multiple times with the same logger_name
        returns the existing logger without adding duplicate handlers.
    """

    @staticmethod
    def get_logger(logger_name="ace_logger"):
        
        """
        Create and return a configured logger instance.

        The logger includes:
        - Console handler for terminal output.
        - Rotating file handler for persistent log storage.
        - Custom formatter with timestamp, log level, logger name,
          filename, line number, function name, and message.

        Args:
            logger_name (str, optional):
                Name of the logger and the generated log file.
                Defaults to "ace_logger".

        Returns:
            logging.Logger:
                Configured logger instance.

        Example:
            >>> logger = AceLogger.get_logger("document_api")
            >>> logger.info("Document uploaded successfully")
        """
        
        # Read from environment
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        log_dir = os.getenv("LOG_DIR", "logs")
        
        logger = logging.getLogger(logger_name)

        if logger.handlers:
            return logger

        logger.setLevel(log_level)
        logger.propagate = False

        os.makedirs(log_dir, exist_ok=True)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | "
            "%(filename)s:%(lineno)d | %(funcName)s | %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Rotating File Handler
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, f"{logger_name}.log"),
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger