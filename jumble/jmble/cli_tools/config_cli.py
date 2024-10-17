""" CLI Config tool. """

import os
import re
import sys

from typing import Any

from ..general_modules import utils

from ..config.configurator import Configurator, DirNotFoundError
from .._types import AttrDict

CONFIG: Configurator = None
APP_PROPS: AttrDict = AttrDict()
DEFAULT_FILE = "properties.yaml"

# pylint: disable=line-too-long
CMD_PATTERNS = {
    "set-file-key-value": r"^(?P<action>set)\s(?P<file>\S+)\s(?P<key>\S+)\s*=\s*(?P<value>.*)$",
    "set-key-value": r"^(?P<action>set)\s(?P<key>\S+)\s*=\s*(?P<value>.*)$",
    "get-key": r"^(?P<action>get)\s(?P<key>\S+)$",
    "del-file-key": r"^(?P<action>del)\s(?P<file>\S+)\s(?P<key>\S+)$",
    "del-key": r"^(?P<action>del)\s(?P<key>\S+)$",
    "append-file-key-value": r"^(?P<action>append)\s(?P<file>\S+)\s(?P<key>\S+)\s*=\s*(?P<value>.*)$",
    "append-key-value": r"^(?P<action>append)\s(?P<key>\S+)\s*=\s*(?P<value>.*)$",
}
# pylint: enable=line-too-long


def create_env_props_dir(path: str) -> None:
    """Create environment properties directory.

    Args:
        path (str): Path to environment properties directory.

    Raises:
        EnvironmentError: Error creating environment properties directory.
    """

    try:
        os.makedirs(path, exist_ok=True)
    except Exception as err:
        raise EnvironmentError(
            f"Error creating environment properties directory: {err}"
        ) from err


def check_env_props():
    """Check for environment properties directory and create one if not found."""

    def check_dir(msg: str):
        create_dir = input(f"{msg} (y/n): ")
        path = None
        if create_dir.lower() == "y":
            path = input("Enter path to environment properties directory: ")
            create_env_props_dir(path)
        else:
            print("Exiting...")
            sys.exit(1)
        return path

    try:
        globals()["PROPS"] = Configurator()
    except DirNotFoundError:
        path = check_dir("No environment properties directory found. Create one?")

        env_prop = os.environ.get("COMMON_ENV_PROPS_DIR")
        if not env_prop or env_prop != path:
            os.environ["COMMON_ENV_PROPS_DIR"] = path
            if sys.platform == "linux":
                utils.add_to_bashrc("export COMMON_ENV_PROPS_DIR=" + path)
                # pylint: disable=line-too-long
                print(
                    "Added COMMON_ENV_PROPS_DIR to bashrc.\nRun 'source ~/.bashrc' to update environment variables."
                )
                # pylint: enable=line-too-long


def set_prop(file_name: str, key: str, value: Any) -> None:
    """Set property in environment properties file.

    Args:
        file_name (str): Name of environment properties file to update.
        key (str): Key to update.
        value (Any): Value to set.
    """

    if isinstance(value, str):
        value = utils.json_or_raw(value)

    print(f"Setting {key} to {value} in {file_name}.")
    try:
        CONFIG.set(file_name, key, value)
    except FileNotFoundError:
        print(f"File not found: {file_name}")
        create_file = input(f"Create file {file_name}? (y/n): ")
        if create_file.lower() == "y":
            CONFIG.create_file(file_name)
            CONFIG.set(file_name, key, value)


def handle_set(cmd_name: str, cmd_match: re.Match):
    """Handle set command.

    Args:
        cmd_name (str): Key from CMD_PATTERNS.
        cmd_match (re.Match): Match object from re.match.

    Raises:
        EnvironmentError: Environment properties not found.
    """

    if CONFIG is None:
        raise EnvironmentError("Environment properties not found.")

    if cmd_name == "set-file-key-value":
        file_name = cmd_match.group("file")
    else:
        file_name = DEFAULT_FILE

    key = cmd_match.group("key")
    value = cmd_match.group("value")

    set_prop(file_name, key, value)


def handle_get(cmd_name: str, cmd_match: re.Match):
    """Handle get command.

    Args:
        cmd_name (str): Key from CMD_PATTERNS.
        cmd_match (re.Match): Match object from re.match.

    Raises:
        EnvironmentError: Environment properties not found.

    Returns:
        str: Value of key.
    """

    if CONFIG is None:
        raise EnvironmentError("Environment properties not found.")

    if cmd_name == "get-file-key":
        file_name = cmd_match.group("file")
    else:
        file_name = DEFAULT_FILE

    key = cmd_match.group("key")
    value = CONFIG.get(file_name, key)
    print(f"{file_name}.{key}: {value}")

    return value


def handle_del(cmd_name: str, cmd_match: re.Match):
    """Handle delete command.

    Args:
        cmd_name (str): Key from CMD_PATTERNS.
        cmd_match (re.Match): Match object from re.match.

    Raises:
        EnvironmentError: Environment properties not found.
    """

    if CONFIG is None:
        raise EnvironmentError("Environment properties not found.")

    if cmd_name == "del-file-key":
        file_name = cmd_match.group("file")
    else:
        file_name = DEFAULT_FILE

    key = cmd_match.group("key")
    CONFIG.delete(file_name, key)


def handle_append(cmd_name: str, cmd_match: re.Match):
    """Handle append command. Used to append values to a list.

    Args:
        cmd_name (str): Key from CMD_PATTERNS.
        cmd_match (re.Match): Match object from re.match.

    Raises:
        EnvironmentError: Environment properties not found.
    """

    if CONFIG is None:
        raise EnvironmentError("Environment properties not found.")

    if cmd_name == "append-file-key-value":
        file_name = cmd_match.group("file")
    else:
        file_name = DEFAULT_FILE

    key = cmd_match.group("key")
    value = cmd_match.group("value")

    if isinstance(value, str):
        value = utils.json_or_raw(value)

    current_value = CONFIG.get(key, [])

    if not isinstance(current_value, list):
        print("Target key is not a list.")
        return

    if isinstance(value, list):
        current_value.extend(value)
    else:
        current_value.append(value)

    set_prop(file_name, key, current_value)


def parse_cmd(cmd_str: str):
    """Parse command string.

    Args:
        cmd_str (str): Command string.

    Raises:
        ValueError: Invalid command.
    """

    cmd_match = None
    cmd = None
    for cmd, pattern in CMD_PATTERNS.items():
        cmd_match = re.match(pattern, cmd_str, re.A)
        if cmd_match:
            break

    if not cmd_match:
        raise ValueError("Invalid command.")

    action = cmd_match.group("action")

    if not cmd:
        raise ValueError("Invalid command.")

    if action == "set":
        handle_set(cmd, cmd_match)
    elif action == "get":
        handle_get(cmd, cmd_match)
    elif action == "del":
        handle_del(cmd, cmd_match)
    elif action == "append":
        handle_append(cmd, cmd_match)


def main():
    """Main function."""

    check_env_props()
    globals()["ENV_PROPS"] = Configurator()
    globals()["APP_PROPS"] = CONFIG.get(__name__)

    args = utils.get_inputs(options={"parse_types": False})

    if isinstance(args, str):
        parse_cmd(args)


if __name__ == "__main__":
    main()
