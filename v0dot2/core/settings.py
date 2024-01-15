"""Core Module: Global User Settings"""

__status__ = "stable"

from config import DEFAULT_SETTINGS


class Settings:
    """A singleton that provides a dictionary of settings."""

    _data = {}
    _instance = None

    def __new__(cls, initial_data: dict[str, str]):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, initial_data: dict[str, str]) -> None:
        self.register(initial_data)

    def __getitem__(self, key: str) -> str:
        return self._data.get(key, "")

    def __setitem__(self, key: str, value: str) -> None:
        self._data[key] = value

    def register(self, data: dict[str, str]) -> None:
        """Register new settings or update existing ones. Skip None values.

        Args:
            data (dict[str, str]): Dictionary of settings.
        """
        # Only register keys with values that are not None
        self._data.update({key: value for key, value in data.items() if value is not None})


# Import this instance of Settings to access global settings
settings = Settings(DEFAULT_SETTINGS)
