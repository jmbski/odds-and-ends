""" Module to handle file utilities """

import json
import os
from datetime import datetime


def escape_path(path_str, preserve_init_slash=False):
    """Escapes a URI string so that it can be passed as a command line argument

    Args:
        path_str (str): The URI string

    Returns:
        str: The escaped URI string
    """

    special_chars = [
        " ",
        "(",
        ")",
        "[",
        "]",
        "{",
        "}",
        "<",
        ">",
        "|",
        ";",
        "&",
        "$",
        "`",
        "\\",
        '"',
        "'",
    ]

    parts = path_str.split("/")

    escaped_parts = []

    for part in parts:
        if not part:
            continue
        if any(char in part for char in special_chars):
            if not part.startswith("'") and not part.endswith("'"):
                part = "'" + part + "'"
        escaped_parts.append(part)

    escaped_path_str = "/".join(escaped_parts)
    escaped_path_str = (
        "/" + escaped_path_str
        if preserve_init_slash and path_str.startswith("/")
        else escaped_path_str
    )
    return escaped_path_str


def get_ext(path):
    """Get the file extension of a path.

    Args:
        path (str): The path to the file.

    Returns:
        str: The file extension.
    """

    ext_split = os.path.splitext(path)
    if len(ext_split) == 1:
        return "N/A"
    return ext_split[1].lower()


def check_path(path):
    """Check if a path exists"""

    if not isinstance(path, str):
        raise ValueError("path must be a string")

    if not os.path.exists(path) and not os.path.islink(path):
        raise FileNotFoundError("Path not found: " + path)


def get_paths(path=None):
    """If path exists, return that, otherwise, return the path from /media/ that has contents

    Args:
        path (str, optional): Path to a specific directory to copy. Defaults to None.

    Raises:
        ValueError: No path(s) can be found.

    Returns:
        list[str]: List of paths, either the specified path or the paths from /media/ that have contents.
    """

    if isinstance(path, str):
        check_path(path)
        return [path]

    media_path = "/media/"
    media_dirs = os.listdir(media_path)
    paths = []
    for path in media_dirs:
        if path.startswith("."):
            continue
        if path.startswith("_"):
            continue

        dir_path = os.path.join(media_path, path)
        if os.path.isdir(dir_path) and os.listdir(dir_path):
            paths.append(dir_path)

    if not paths:
        raise ValueError("No paths found")

    return paths


def get_timestamp(path, timestamp_type="modified"):
    """Get the timestamp of a file.

    Args:
        path (str): Path to the file.
        timestamp_type (str, optional): Type of timestamp to retrieve. Valid values are
            "created", "modified", and "accessed". Defaults to "modified".

    Returns:
        tuple (int, str): Tuple containing the timestamp in seconds and human-readable format.
    """

    timestamp_functs = {
        "created": os.path.getctime,
        "modified": os.path.getmtime,
        "accessed": os.path.getatime,
    }

    if timestamp_type not in timestamp_functs:
        raise ValueError("Invalid timestamp type: " + timestamp_type)

    try:
        timestamp_raw = timestamp_functs[timestamp_type](path)
        timestamp_str = datetime.fromtimestamp(timestamp_raw).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        return timestamp_raw, timestamp_str
    except FileNotFoundError:
        return None, "N/A"


def load_json(path):
    """Load a JSON file.

    Args:
        path (str): Path to the JSON file.

    Returns:
        dict | list: The JSON data.
    """

    check_path(path)

    with open(path, "r", encoding="UTF-8") as file:
        data = json.load(file)

    return data
