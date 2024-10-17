""" Combined config reader """

from __future__ import annotations

import configparser
import json
import os

from typing import Any

import toml
import yaml

from .._types import AttrDict
from ..general_modules import utils

COMMON_PROPS_DIR = os.environ.get(
    "COMMON_PROPS_DIR", os.path.expanduser("~/.config/environment")
)

DICT_HANDLERS = {
    "json": {
        "read": json.load,
        "write": json.dump,
    },
    "yaml": {
        "read": yaml.safe_load,
        "write": yaml.dump,
    },
    "yml": {
        "read": yaml.safe_load,
        "write": yaml.dump,
    },
    "toml": {
        "read": toml.load,
        "write": toml.dump,
    },
}
""" Dictionary of handlers for dictionary-based configuration files (json, yaml, toml)"""

PARSER_EXTS = [
    "ini",
    "properties",
    "conf",
]
""" List of parser-based configuration file extensions (ini, properties, conf)"""


def get_cfg_io(path: str) -> tuple[str, SimpleConfigParser | tuple[callable, callable]]:
    """Function to get the IO functions for the configuration file

    Args:
        path (str): The path to the configuration file

    Returns:
        tuple[str, SimpleConfigParser | tuple[callable, callable]]: The extension of the
            file and the IO functions
    """

    ext = utils.get_ext(path).replace(".", "")

    if ext in DICT_HANDLERS:
        handlers = DICT_HANDLERS[ext]
        return ext, (handlers["read"], handlers["write"])

    if ext in PARSER_EXTS:
        return ext, SimpleConfigParser()

    return None, None


class DirNotFoundError(Exception):
    """Exception raised when the directory is not found"""

    def __init__(self, message: str = "Directory not found"):
        """Constructor for the DirNotFoundError class

        Args:
            message (str, optional): The error message. Defaults to 'Directory not found'.
        """

        super().__init__(message)


class SimpleConfigParser(configparser.ConfigParser):
    """SimpleConfigParser class to handle configuration files without sections"""

    def read(self, filenames: list[str], encoding=None):
        """Method to read the configuration file and add a dummy section if one is not present

        Note: Override of configparser.ConfigParser.read

        Args:
            filenames (list[str]): Names of the configuration files to read
            encoding (str, optional): String encoding to use. Defaults to None.
        """

        if isinstance(filenames, str):
            filenames = [filenames]

        for filename in filenames:
            with open(filename, "r", encoding=encoding) as config_file:
                content = config_file.read()
                if not content.startswith("[dummy_section]"):
                    content = "[dummy_section]\n" + content

                self.read_string(content)


class ConfigReader:
    """Class to read configuration files and return the data as an AttrDict"""

    def __init__(self, config_path: str) -> None:
        """Constructor for the ConfigReader class

        Args:
            config_path (str): The path to the configuration file
        Raises:
            FileNotFoundError: Raised if the configuration file is not found
        """

        self.config_data: AttrDict = AttrDict()
        self.path = config_path

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        self.parse_config()

    def parse_config(self):
        """Method to parse the configuration file and store the data in an AttrDict"""

        # Get the values and extension of the file
        config_data = self.read_config()

        if config_data is None:
            raise ValueError("Config data is None")

        # Initialize the config_data attribute
        self.config_data = AttrDict({})

        # Handle configparser and dict types
        if isinstance(config_data, configparser.ConfigParser):
            for section in config_data.sections():
                if section != "dummy_section":
                    # Initialize the section in the config_data attribute
                    # ignoring the dummy_section added by SimpleConfigParser
                    self.config_data[section] = {}

                for key, value in config_data.items(section):
                    # Add the appropriate values from the section to the config_data attribute
                    if utils.not_empty(value):
                        if section == "dummy_section":
                            self.config_data[key] = value
                        else:
                            self.config_data[section][key] = value

        elif isinstance(config_data, dict):
            # Add the values from the dictionary to the config_data attribute
            self.config_data = AttrDict(config_data)

    def read_config(self):
        """Method to read the configuration file and return the data as a dictionary

        Raises:
            ValueError: Raised if the configuration file extension is not supported

        Returns:
            dict | configparser.ConfigParser: The configuration data as a dictionary or
                ConfigParser object
        """

        # Get the extension and IO functions for the file
        ext, cfg_io = get_cfg_io(self.path)

        if isinstance(cfg_io, tuple):
            read = cfg_io[0]
            with open(self.path, "r", encoding="UTF-8") as file:
                return read(file)
        elif isinstance(cfg_io, SimpleConfigParser):
            cfg_io.read(self.path)
            return cfg_io
        else:
            raise ValueError(f"Unsupported config file extension: {ext}")


class Configurator:
    """Class that combines all the environment properties into a single dictionary
    for easy retrieval

    The path to the environment properties directory is retrieved from the
    COMMON_PROPS_DIR environment variable (unless a path is provided as an
    argument) and the properties from all .json, .cfg, .ini, .properties,
    .toml, and .yaml files in the directory are combined into a single
    dictionary, unless a specific list of files is provided.
    """

    def __init__(self, env_props_dir: str = None, specific_files: list[str] = None):
        """Constructor for the EnvironmentProps class

        Args:
            env_props_dir (str, optional): The path to the environment properties directory.
                Defaults to None.
            specific_files (list[str], optional): A list of specific files to parse. Defaults to [].
        Raises:
            FileNotFoundError: Raised if the environment properties directory or
                a specific file is not found
            NotADirectoryError: Raised if the path provided is not a directory
        """

        env_props_dir = env_props_dir if env_props_dir else COMMON_PROPS_DIR

        if not os.path.exists(env_props_dir):
            raise DirNotFoundError(
                f"Environment properties directory not found: {env_props_dir}\n \
                Please set the COMMON_PROPS_DIR environment variable to the correct path."
            )
        if not os.path.isdir(env_props_dir):
            raise NotADirectoryError(
                f"Path is not a directory: {env_props_dir}\nPlease set the COMMON_PROPS_DIR \
                environment variable to the correct path that is a directory."
            )

        env_prop_files = specific_files if specific_files else os.listdir(env_props_dir)

        for prop_file in env_prop_files:
            if not os.path.exists(os.path.join(env_props_dir, prop_file)):
                raise FileNotFoundError(
                    f"Environment property file not found: {prop_file}"
                )

        self.config = AttrDict({})

        self._parse_configs(
            [os.path.join(env_props_dir, file) for file in env_prop_files]
        )

    def _parse_configs(self, file_paths: list[str]) -> None:
        """Method to parse the environment properties files and combine them into
        a single dictionary

        Args:
            file_paths (list[str]): A list of file paths to the environment properties files
        """

        for file_path in file_paths:
            config = ConfigReader(file_path).config_data

            if isinstance(config, dict):
                for key, value in config.items():
                    self.config[key] = value

    def get(self, path: str | list[str], default_val: Any = None) -> Any:
        """Method to retrieve a value from the environment properties dictionary

        Args:
            path (str | list[str]): The path to the value in the dictionary
            default_val (Any, optional): The default value to return if the path is not found.
                Defaults to None.

        Returns:
            Any: The value at the specified path in the dictionary, or the default value if
                the path is not found
        """

        value = utils.get_nested(self.config, path, default_val)

        if isinstance(value, dict):
            return AttrDict(value)

        return value

    def set(self, cfg_file: str, key: str | list[str], value: Any):
        """Method to set a value in a configuration file

        Args:
            cfg_file (str): Config file name (with extension) in the environment
                properties directory
            key (str | list[str]): The key path to the value to set
            value (Any): The value to set

        Raises:
            FileNotFoundError: Raised if the config file is not found
        """

        # Check if the config file exists
        path = os.path.join(COMMON_PROPS_DIR, cfg_file)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")

        # Normalize the key path
        if isinstance(key, str):
            key = key.split(".")

        if isinstance(key, list):

            # Get the extension and IO functions for the file
            ext, cfg_io = get_cfg_io(path)

            # Read the file and set the value based on the extension
            if isinstance(cfg_io, SimpleConfigParser):
                cfg_io.read(path)

                if len(key) == 1:
                    cfg_io[key[0]] = value
                else:
                    cfg_io[key[0]][key[1]] = value

                with open(path, "w", encoding="UTF-8") as file:
                    cfg_io.write(file)

            elif isinstance(cfg_io, tuple):
                read, write = cfg_io

                with open(path, "r", encoding="UTF-8") as file:
                    data = read(file)

                utils.set_nested(data, key, value)

                with open(path, "w", encoding="UTF-8") as file:
                    if ext == "json":
                        write(data, file, indent=4)
                    else:
                        write(data, file)

    def delete(self, cfg_file: str, key: str | list[str]) -> None:
        """Method to delete a value from a configuration file

        Args:
            cfg_file (str): Config file name (with extension) in the environment
                properties directory
            key (str | list[str]): The key path to the value to delete

        Raises:
            FileNotFoundError: Raised if the config file is not found
        """

        # Check if the config file exists
        path = os.path.join(COMMON_PROPS_DIR, cfg_file)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")

        # Normalize the key path
        if isinstance(key, str):
            key = key.split(".")

        if isinstance(key, list):

            # Get the extension and IO functions for the file
            ext, cfg_io = get_cfg_io(path)

            if isinstance(cfg_io, SimpleConfigParser):
                cfg_io.read(path)

                if len(key) == 1:
                    cfg_io.remove_option("dummy_section", key[0])
                else:
                    cfg_io.remove_option(key[0], key[1])

                with open(path, "w", encoding="UTF-8") as file:
                    cfg_io.write(file)

            elif isinstance(cfg_io, tuple):
                read, write = cfg_io

                with open(path, "r", encoding="UTF-8") as file:
                    data = read(file)

                utils.delete_nested(data, key)

                with open(path, "w", encoding="UTF-8") as file:
                    if ext == "json":
                        write(data, file, indent=4)
                    else:
                        write(data, file)

    def create_file(self, file_name: str, initial_values: dict = None):
        """Method to create a new configuration file with the specified initial values

        Args:
            file_name (str): The name of the configuration file to create
            initial_values (dict, optional): Initial values to set in the new file. Defaults to {}.
        """

        path = os.path.join(COMMON_PROPS_DIR, file_name)

        ext, cfg_io = get_cfg_io(path)

        if isinstance(cfg_io, configparser.ConfigParser):
            cfg_io.read_dict(initial_values)
            with open(path, "w", encoding="UTF-8") as file:
                cfg_io.write(file)
        elif isinstance(cfg_io, tuple):
            write = cfg_io[1]

            with open(path, "w", encoding="UTF-8") as file:
                if ext == ".json":
                    write(initial_values, file, indent=4)
                else:
                    write(initial_values, file)

    def get_environment(self) -> dict:
        """Method to get the environment properties as a dictionary

        Returns:
            dict: The environment properties as a dictionary
        """

        return self.get("environment")
