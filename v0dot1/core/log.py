"""Core Module: Log"""

import logging
from enum import Enum
from typing import List

from core.settings import settings


class Log:
    """Provides logging functionality."""

    class Level(Enum):
        """All available logging levels."""

        ERROR = logging.getLevelName("ERROR")
        WARNING = logging.getLevelName("WARNING")
        INFO = logging.getLevelName("INFO")
        DEBUG = logging.getLevelName("DEBUG")

        @classmethod
        def get_level_from_name(cls, level_name: str):
            """Return log level from given level name."""
            return cls[level_name.upper()]

    class _LevelnamePaddingFilter(logging.Filter):
        """Logging filter to add padding to level name."""

        def filter(self, record: logging.LogRecord) -> bool:
            """Add padding to levelname to align log messages."""
            # [NOTE] "WARNING" is the longest level name used in this project
            record.levelname_padding = " " * (len("WARNING") - len(record.levelname))
            return True

    def __init__(
        self,
        name: str,
        log_file: str = "",
        level: Level | None = None,
    ) -> None:
        """Initialize new logging provider.

        Args:
            name (str): Name of the logger that will be created.
            log_file (str, optional): File name of log file. Defaults to config.DEFAULT_LOG_FILE.
            level (Level, optional): Log level. Defaults to config.DEFAULT_LOG_LEVEL.
        """
        log_file = log_file or settings["log_file"]
        level = level or self.Level.get_level_from_name(settings["log_level"])
        self._logger = logging.getLogger(name)
        self._logger.addFilter(self._LevelnamePaddingFilter())
        self._logger.handlers.clear()
        self._logger.setLevel(level.value)
        logging.raiseExceptions = True
        formatter = logging.Formatter(
            "%(asctime)s.%(msecs)03d [%(levelname)s]%(levelname_padding)s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handlers: List[logging.Handler] = [
            logging.StreamHandler(),
            logging.FileHandler(log_file),
        ]
        for handler in handlers:
            handler.setLevel(level.value)
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def __getattr__(self, level_name: str):
        """Return a logging function for the given level name.

        Args:
            level_name (str): Name of the logging level, e.g. "info" or "warning".

        Raises:
            AttributeError: If the given level name is not a valid logging level.

        Returns:
            lambda: Logging function for the given level name, e.g. self.info() or self.warning().
        """
        level_name = level_name.upper()
        if level_name in self.Level.__members__:
            level = logging.getLevelName(level_name)
            return lambda message: self._logger.log(level, message)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{level_name}'.")

    def entry(self, level: Level, message: str) -> None:
        """Log a message with the given log level."""
        self._logger.log(level.value, message)

    def get_logger(self) -> logging.Logger:
        """Return the current logger."""
        return self._logger

    def shutdown(self) -> None:
        """Shut down logging. Log file will be closed."""
        logging.shutdown()
