import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

# LOAD ENVIRONMENT VARIABLES
load_dotenv()

CONFIG_DIR = Path("config")


def _deep_merge(base: dict, override: dict):
    """
    Recursively merges two dictionaries.
    For each key in the `override` dictionary, if the key exists in `base` and both values are dictionaries,
    the function merges them recursively. Otherwise, the value from `override` replaces the value in `base`.
    Args:
        base (dict): The base dictionary to merge into.
        override (dict): The dictionary whose values will override those in `base`.
    Returns:
        dict: A new dictionary containing the merged keys and values.
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class Config:
    """
    Configuration loader and accessor for Atlas projects.
    This class loads configuration settings from YAML files based on the current environment,
    merging a base configuration with environment-specific overrides. It provides methods to
    retrieve configuration values using dot-separated paths, access environment variables, and
    construct a database connection URL.
    Attributes:
        env (str): The current environment (e.g., "dev", "prod"), determined by the ATLAS_ENV environment variable.
        data (dict): The merged configuration dictionary.
    Methods:
        get(path: str, default=None):
            Retrieve a value from the configuration using a dot-separated path.
        env_var(name: str, default=None):
        database_url():
            Construct and return the PostgreSQL database connection URL using configuration and environment variables.
    """

    def __init__(self):

        self.env = os.getenv("ATLAS_ENV", "dev")

        base_file = CONFIG_DIR / "base.yaml"
        env_file = CONFIG_DIR / f"{self.env}.yaml"

        with open(base_file) as f:
            base_config = yaml.safe_load(f) or {}

        if env_file.exists():
            with open(env_file) as f:
                env_config = yaml.safe_load(f) or {}
        else:
            env_config = {}

        self.data = _deep_merge(base_config, env_config)

    # -----------------------------------------------
    def get(self, path: str, default=None):
        """
        Retrieve a value from a nested dictionary using a dot-separated path.
        Parameters:
            path (str): A dot-separated string representing the path to the desired value
                (e.g., "section.key.subkey").
            default (Any, optional): The value to return if the specified path does not exist.
                Defaults to None.
        Example:
            >>> config = Config({"database": {"host": "localhost"}})
            >>> config.get("database.host")
            'localhost'
            >>> config.get("database.port", default=5432)
            5432
        """
        keys = path.split(".")
        value = self.data

        for key in keys:
            if not isinstance(value, dict):
                return default
            if key not in value:
                return default
            value = value[key]

        return value

    # -----------------------------------------------
    def env_var(self, name: str, default=None):
        """
        Retrieve the value of an environment variable.

        Args:
            name (str): The name of the environment variable to retrieve.
            default (Any, optional): The value to return if the environment variable is not set. Defaults to None.

        Returns:
            Any: The value of the environment variable if it exists, otherwise the default value.
        """
        return os.getenv(name, default)

    # -----------------------------------------------
    def database_url(self):
        """
        Constructs the PostgreSQL database URL from environment variables.
        Retrieves the database user, password, host, port, and name from environment
        variables and formats them into a SQLAlchemy-compatible PostgreSQL URL.
        Returns:
            str: The formatted PostgreSQL database URL.
        Raises:
            KeyError: If any of the required environment variables are not set.
        """
        user = self.env_var("DATABASE_USER")
        password = self.env_var("DATABASE_PASSWORD")
        host = self.env_var("DATABASE_HOST")
        port = self.env_var("DATABASE_PORT")
        name = self.env_var("DATABASE_NAME")

        return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"


# GLOBAL CONFIG INSTANCE
config = Config()


# EXAMPLE USAGE
# from atlas.infrastructure.config import config

# print(config.env)
# print(config.get("database.host"))
# print(config.database_url())
