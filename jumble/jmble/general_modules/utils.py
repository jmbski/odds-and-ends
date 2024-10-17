""" Common Python code for jmble projects."""

import json
import os
import re
import shlex
import subprocess
import sys

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from time import time
from typing import Any, Callable, Literal, Optional, TypedDict

from tqdm import tqdm
from .._types import AttrDict

LIST_STR_PATTERN = r"^\[(.*)\]$"
SINGLE_QUOTE_PATTERN = r"^'(.*)'$"
DOUBLE_QUOTE_PATTERN = r'^"(.*)"$'

p_join = os.path.join
""" Shortcut for os.path.join """

p_exists = os.path.exists
""" Shortcut for os.path.exists """

SubReturn = Literal["out", "err", "both"]
""" String literal type representing the output choices for cmdx """


class GetInputsOptions(TypedDict, total=False):
    """Options for the get_inputs function"""

    parse_types: Optional[bool]
    save_initial_text: Optional[bool]
    initial_text_key: Optional[str] = "initial_text"


def e_open(file_path: str, mode: str = "r", encoding: str = "UTF-8"):
    """Open a file with a specified encoding

    Args:
        file_path (str): The path to the file
        mode (str, optional): The mode to open the file. Defaults to "r".
        encoding (str, optional): The encoding to use. Defaults to "UTF-8".

    Returns:
        file: The file object
    """

    return open(file_path, mode, encoding=encoding)


def json_or_raw(value: str) -> Any:
    """Load a JSON string or return the raw string

    Args:
        value (str): The string to load

    Returns:
        Any: The loaded JSON object or the raw string
    """

    try:
        return json.loads(value)
    except Exception as err:
        if isinstance(err, json.JSONDecodeError):
            return value
        raise err


def get_ext(path: str) -> str:
    """Get the extension of a file path

    Args:
        path (str): The file path

    Returns:
        str: The file extension
    """

    return os.path.splitext(path)[1]


def add_to_bashrc(value: str) -> None:
    """Add a value to the bashrc file

    Args:
        value (str): The value to add

    Raises:
        FileNotFoundError: If the bashrc file is not found
    """

    bashrc_path = os.path.expanduser("~/.bashrc")
    if not os.path.exists(bashrc_path):
        raise FileNotFoundError("No bashrc file found")
    with open(bashrc_path, "a", encoding="UTF-8") as f:
        f.write("\n" + value + "\n")


def is_numeric(value) -> bool:
    """Checks if a value is numeric"""

    try:
        if isinstance(value, str):
            value = value.replace(",", "")
        float(value)
        return True
    except ValueError:
        return False


def list_str_to_list(list_str: str) -> list:
    """Converts a string representation of a list to a list

    Args:
        list_str (str): The string representation of a list

    Returns:
        list: The list
    """

    search = re.search(LIST_STR_PATTERN, list_str)

    if search:
        parsed_list = []
        list_str = search.group(1)

        list_split = list_str.split(",")

        for item in list_split:
            parsed_list.append(parse_str_type(item))

        return parsed_list
    return list_str


def parse_str_type(value: str, empty_value: Any = 0) -> Any:
    """Parse a string to a type

    Args:
        value (str): The value to parse
        empty_value (Any, optional): The value to return if the string is empty. Defaults to 0.

    Returns:
        Any: The parsed value
    """

    if isinstance(value, str):
        if re.search(DOUBLE_QUOTE_PATTERN, value):
            value = value.strip().strip('"')

        elif re.search(SINGLE_QUOTE_PATTERN, value):
            value = value.strip().strip("'")

        elif re.search(LIST_STR_PATTERN, value):
            value = list_str_to_list(value)

        if not isinstance(value, str):
            return value

        value = value.strip().replace(",", "")

        if is_numeric(value):
            if "." in value:
                value = float(value)
            value = int(value)

        elif value.lower() == "true":
            value = True

        elif value.lower() == "false":
            value = False

        if not isinstance(value, str):
            return value

        if value.strip() == "":
            return empty_value

    return value


def check_prefixes(prefixes: list[str], arg: str) -> str:
    """Checks if the argument starts with any of the prefixes and returns the best match

    Args:
        prefixes (list[str]): - A list of prefixes to check for
        arg (str): - The argument to check

    Returns:
        str: The prefix that best matches the argument or None
            i.e. if the argument is '--name' and the prefixes are ['--', '-'], it will return '--'
    """

    matches = []

    for prefix in prefixes:
        if arg.startswith(prefix):
            matches.append(prefix)

    return max(matches, key=len) if matches else None


def get_prefix_args(
    prefixes: list[str] = None, options: Optional[GetInputsOptions] = None
) -> AttrDict[str, str] | str:
    """Parses command line arguments that start with a prefix and returns them as a dictionary

    Args:
        prefixes (list[str], optional): Prefixes to check for. Defaults to ['--', '-'].

    Returns:
        AttrDict[str, str] | str: A dictionary of arguments or a single string
    """

    prefixes = prefixes or ["--", "-"]
    options = options or {}

    parsed_args = AttrDict()
    args = sys.argv[1:]
    save_initial = options.get("save_initial_text", False)
    initial_text_key = options.get("initial_text_key")
    parse_types = options.get("parse_types", False)

    if isinstance(prefixes, list):
        key: str = None
        value: str = None
        for arg in args:
            prefix_match = check_prefixes(prefixes, arg)
            if prefix_match:
                if key is not None:
                    arg_value = value.strip() if value is not None else True
                    parsed_args[key] = (
                        arg_value if not parse_types else parse_str_type(arg_value)
                    )
                    value = None
                elif save_initial and initial_text_key:
                    parsed_args[initial_text_key] = arg
                    value = None

                key = arg[len(prefix_match) :]
            else:
                value = f"{value} {arg}" if value is not None else arg

        if key is not None and key not in parsed_args:
            parsed_args[key] = value.strip() if value is not None else True
        elif key is None and value is not None:
            return value.strip()

    return parsed_args


def get_ordered_args(
    ordered_arg_names: list[str], options: Optional[GetInputsOptions] = None
) -> AttrDict[str, str]:
    """Parses command line arguments based on a list of ordered argument names

    Args:
        ordered_arg_names (list[str]): A list of argument names in the order they should be parsed.
        options (Optional[GetInputsOptions], optional): Options for parsing the arguments.
            Defaults to {}.

    Returns:
        AttrDict[str, str]: A dictionary of arguments
    """

    options = options or {}

    args = sys.argv[1:]
    parsed_args = zip(ordered_arg_names, args)
    if options.get("parse_types", False):
        parsed_args = [(key, parse_str_type(value)) for key, value in parsed_args]
    return AttrDict(parsed_args)


def get_inputs(
    prefixes: list[str] | None = None,
    ordered_arg_names: list[str] | None = None,
    options: Optional[GetInputsOptions] = None,
) -> AttrDict[str, str] | str:
    """Parses command line arguments based on the prefix, argument names, and/or options

    Args:
        prefix (list[str], optional): Prefix(es) to check. Defaults to ['--', '-'].
        ordered_arg_names (list[str], optional): A list of argument names in the order
            they should be parsed. Defaults to None.
        options (dict, optional): A dictionary of various option values. Defaults to None.
            *Not implemented yet*

    Returns:
        AttrDict[str, str] | str: A dictionary of arguments or a single string
    """

    if isinstance(ordered_arg_names, list):
        return get_ordered_args(ordered_arg_names, options)

    return get_prefix_args(prefixes, options)


def not_empty(value: Any) -> bool:
    """Checks if a value is empty (nullish) or not

    Args:
        value (Any): The value to check

    Returns:
        bool: True if the value is not empty
    """

    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value)
    if isinstance(value, dict):
        return bool(value)
    return True


def get_nested(obj: dict | list, path: list[str] | str, default_val: Any = None) -> Any:
    """Get a nested value from a dictionary or list

    Args:
        obj (dict | list): The object to get the value from
        path (list[str] | str): The path to the value
        default_val (Any, optional): The default value to return if the path is not found.
            Defaults to None.

    Returns:
        Any: The value at the path or the default value
    """

    if isinstance(path, str):
        path = path.split(".")

    if len(path) == 1:
        result = None
        if isinstance(obj, dict):
            result = obj.get(path[0], default_val)

        elif isinstance(obj, list) and path[0].isdigit():
            idx = int(path[0])
            item = None
            if idx < len(obj):
                item = obj[idx]
            if item is None:
                item = default_val

            result = item
        return result

    key = path.pop(0)
    if isinstance(obj, list) and key.isdigit():
        if int(key) < len(obj):
            return get_nested(obj[int(key)], path, default_val)
        return default_val
    if key not in obj:
        return default_val
    return get_nested(obj[key], path, default_val)


def delete_nested(obj: dict | list, path: list[str] | str) -> None:
    """Delete a nested value from a dictionary or list

    Args:
        obj (dict | list): The object to delete the value from
        path (list[str] | str): The path to the value
    """

    if isinstance(path, str):
        path = path.split(".")

    if len(path) == 1:
        if isinstance(obj, dict):
            obj.pop(path[0], None)
        elif isinstance(obj, list) and path[0].isdigit():
            idx = int(path[0])
            if idx < len(obj):
                obj.pop(idx)
    else:
        key = path.pop(0)
        if isinstance(obj, list) and key.isdigit():
            if int(key) < len(obj):
                delete_nested(obj[int(key)], path)
        elif key in obj:
            delete_nested(obj[key], path)


def debug_print(*args):
    """Print debug statements with a newline before and after"""

    strings = list(args)
    strings.insert(0, "\n")
    strings.append("\n")
    print(*strings)


def pretty_print(obj: any) -> None:
    """Prints a JSON serializable object with indentation"""

    print(json.dumps(obj, indent=4))


@dataclass
class SetNestedOptions:
    """Options for the set_nested function"""

    def __init__(self, debug: bool = False, create_lists: bool = False) -> None:

        self.debug: bool = debug
        self.create_lists: bool = create_lists


def _set_next_append(
    obj: list,
    path: list[str],
    key: str | int,
    value: Any,
    debug: bool = False,
    create_lists: bool = True,
) -> None:
    """Set a value in a nested object when the index is out of bounds

    Args:
        obj (list): Object to set the value in
        path (list[str]): Path to the value
        key (str | int): Key to set the value at
        value (Any): Value to set
        debug (bool, optional): Flag to enable debug statements. Defaults to False.
        create_lists (bool, optional): Flag to set whether to create a list or. Defaults to True.
    """
    if debug:
        debug_print("out of bounds", "inserting new value", f"path[0] = {path[0]}")

    if path[0].isdigit() and create_lists:
        obj.insert(int(key), [])
    else:
        obj.insert(int(key), {})

    if debug:
        debug_print("blank inserted", obj)

    set_nested(obj[-1], path, value, debug, create_lists)


def _set_next_list_item(
    obj: list,
    path: list[str],
    key: str | int,
    value: Any,
    debug: bool = False,
    create_lists: bool = True,
) -> None:
    """Iterate through the next item in a list or dictionary

    Args:
        obj (list): Object to set the value in
        path (list[str]): Path to the value
        key (str | int): Key to set the value at
        value (Any): Value to set
        debug (bool, optional): Flag to enable debug statements. Defaults to False.
        create_lists (bool, optional): Flag to set whether to create a list or. Defaults to True.
    """

    sub = obj[int(key)]
    if not sub or not isinstance(sub, (dict, list)):
        if debug:
            debug_print("sub is None or not an object", "creating new sub")

        if path[0].isdigit() and create_lists:
            obj[int(key)] = []
        else:
            obj[int(key)] = {}

    set_nested(obj[int(key)], path, value, debug, create_lists)


def _set_final_prop(obj: dict | list, path: list[str], value: Any) -> None:
    """Set a value in a nested object at the final path

    Args:
        obj (dict | list): Object to set the value in
        path (list[str]): Path to the value
        value (Any): Value to set
    """

    if isinstance(obj, dict):
        obj[path[0]] = value
    elif isinstance(obj, list) and path[0].isdigit():
        if int(path[0]) < len(obj):
            obj[int(path[0])] = value
        else:
            obj.append(value)


def _set_next_nested(
    obj: dict | list,
    path: list[str],
    value: Any,
    key: str | int,
    debug: bool = False,
    create_lists: bool = True,
) -> None:
    """Set a value in a nested object

    Args:
        obj (dict | list): Object to set the value in
        path (list[str]): Path to the value
        value (Any): Value to set
        key (str | int): Key to set the value at
        debug (bool, optional): Flag to enable debug statements. Defaults to False.
        create_lists (bool, optional): Flag to set whether to create a list or. Defaults to True.
    """

    sub = obj.get(key)

    if debug:
        debug_print("obj is dict", "sub:", sub)

    if not sub or not isinstance(sub, (dict, list)):
        if debug:
            debug_print("sub is None or not an object", "creating new sub")

        if path[0].isdigit() and create_lists:
            obj[key] = []
        else:
            obj[key] = {}

        if debug:
            debug_print("new sub created", obj)

    set_nested(obj.get(key), path, value, debug, create_lists)


def set_nested(
    obj: dict | list,
    path: list[str] | str,
    value: Any,
    debug: bool = False,
    create_lists: bool = True,
) -> None:
    """Set a nested value in a dictionary or list

    Args:
        obj (dict | list): The object to set the value in
        path (list[str] | str): The path to the value
        value (Any): The value to set
        debug (bool, optional): Flag to enable debug statements. Defaults to False.
        create_lists (bool, optional): Flag to set whether to create a list or
            a dict when the path fragment is a number. Defaults to True.
    """

    if isinstance(path, str):
        path = path.split(".")

    if debug:
        debug_print("starting function")
        pretty_print({"obj": obj, "path": path, "value": value})

    if len(path) == 1:
        _set_final_prop(obj, path, value)
    else:
        key = path.pop(0)

        if debug:
            debug_print("key", key)

        if isinstance(obj, list) and key.isdigit():  # true
            if debug:
                debug_print("obj is list", "key < len", int(key) < len(obj))

            if int(key) < len(obj):
                _set_next_list_item(
                    obj,
                    path,
                    key,
                    value,
                    create_lists,
                )
            else:
                _set_next_append(
                    obj,
                    path,
                    key,
                    value,
                    create_lists,
                )
        elif isinstance(obj, dict):
            _set_next_nested(obj, path, value, key, debug, create_lists)


# pylint: disable=C0103
@dataclass
class SubReturns:
    """Enum class for SubReturn values"""

    OUT: SubReturn = "out"
    ERR: SubReturn = "err"
    BOTH: SubReturn = "both"


# pylint: enable=C0103


def cmdx(
    cmd: list[str] | str, rtrn: SubReturn = "out", print_out: bool = True
) -> str | tuple[str, str]:
    """Executes a command and returns the output or error

    Args:
        cmd (list[str] | str): - A list of strings that make up the command or a string
            that will be split by spaces
        rtrn (SubReturn, optional): What outputs to return. If both, it will return a
            tuple of (stdout, stderr)Defaults to 'out'.

    Returns:
        str | tuple[str, str]: The output of the command or a tuple of (stdout, stderr)
    """

    if isinstance(cmd, str):
        cmd = shlex.split(cmd)

    try:
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            check=True,
        )
    except subprocess.CalledProcessError as e:
        # Print and handle the errors here if needed
        process = e

    stdout = process.stdout
    stderr = process.stderr
    if print_out:
        if stdout:
            print(stdout)
        if stderr:
            print("\nERROR:\n", stderr)

    if rtrn == "out":
        return process.stdout
    if rtrn == "err":
        return process.stderr

    return process.stdout, process.stderr


def cmd_grep(
    cmd: str | list, search_expr: str, rtrn: SubReturn = "out", print_out: bool = True
):
    """Executes a command and pipes the result through a grep search

    Args:
        cmd (str | list): - A list of strings that make up the command or a string that
            will be split by spaces
        search_cmd (str): - The command to pass to grep
        rtrn (SubReturn, optional): What outputs to return. If both, it will return a
            tuple of (stdout, stderr) . Defaults to 'out'.

    """

    if isinstance(cmd, str):
        cmd = cmd.split()

    search_cmd = f'grep "{search_expr}"'
    with subprocess.Popen(cmd, stdout=subprocess.PIPE) as initial_cmd:

        process = subprocess.run(
            search_cmd,
            stdin=initial_cmd.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            check=True,
        )
        stdout = process.stdout
        stderr = process.stderr
        if print_out:
            if stdout:
                print(stdout)
            if stderr:
                print("\nERROR:\n", stderr)

        if rtrn == "out":
            return process.stdout
        if rtrn == "err":
            return process.stderr
        return process.stdout, process.stderr


def escape_path(path_str: str, preserve_init_slash: bool = False) -> str:
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
                part = f"'{part}'"
        escaped_parts.append(part)

    escaped_path_str = "/".join(escaped_parts)
    escaped_path_str = (
        "/" + escaped_path_str
        if preserve_init_slash and path_str.startswith("/")
        else escaped_path_str
    )
    return escaped_path_str


def to_snake_case(value: str) -> str:
    """Convert a string to snake_case

    Args:
        value (str): The string to convert

    Returns:
        str: The converted string
    """

    # Convert camelCase to snake_case
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    # Convert spaces and hyphens to underscores
    value = re.sub(r"[-\s]+", "_", value)
    # Convert to lower case
    return value.lower()


def generate_sample_file(file_path: str, size: int, append=False) -> None:
    """Generate a sample file.

    Args:
        file_path (str): Path to the file.
        size (int): Size of the file in bytes.
    """

    thread_count = os.cpu_count()
    chunk_size = size // thread_count

    mode = "wb" if not append else "ab"

    def write_chunk(start, end):
        with open(file_path, mode) as file:
            file.seek(start)
            file.write(os.urandom(end - start))

    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        offsets = [(i * chunk_size, (i + 1) * chunk_size) for i in range(thread_count)]
        if offsets[-1][1] < size:
            offsets[-1] = (offsets[-1][0], size)

        # rewrite the next line but using TQDM
        # executor.map(lambda args: write_chunk(*args), offsets)

        for _ in tqdm(
            executor.map(lambda args: write_chunk(*args), offsets), total=thread_count
        ):
            pass


def stopwatch(funct: Callable, *args, **kwargs) -> tuple[float, Any]:
    """Time the execution of a function.

    Args:
        funct (Callable): The function to time.

    Returns:
        tuple[float, Any]: The time taken to execute the function and the result of the function.
    """

    start = time()
    result = funct(*args, **kwargs)
    total_time = round(time() - start, 2)

    return total_time, result
