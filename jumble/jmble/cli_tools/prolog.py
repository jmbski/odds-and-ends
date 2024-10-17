""" CLI tool to create and update file prologue headers. """

# import os

from ..config import Configurator
from .._types import AttrDict
from ..general_modules import utils

CONFIG = Configurator()
APP_NAME = "prolog"
ENV_PROPS = CONFIG.get("environment")
APP_PROPS = CONFIG.get(APP_NAME)


def build_template_values() -> AttrDict:
    """Build the template values for the prologue header.

    Returns:
        AttrDict: The template values for the prologue header.
    """

    template = APP_PROPS.template_values or AttrDict()

    if not isinstance(template, AttrDict):
        raise ValueError(
            "Invalid template values, please update the configuration file"
        )


def get_file(file_name: str = None) -> str:
    """Determine the file to create/update the prologue header for.

    Args:
        file_name (str, optional): The name of the file to create/update the prologue
            header for. Defaults to None.

    Returns:
        str: The name of the file to create/update the prologue header for.
    """

    utils.pretty_print(APP_PROPS)

    return file_name

    # supported_exts = APP_PROPS.get("supported_exts", ["py", "sh"])


def main():
    """Main function"""

    args = utils.get_inputs()
    get_file()
    """ if not isinstance(args, dict):
        raise ValueError("Invalid arguments") """

    print("Prolog CLI tool", args)


if __name__ == "__main__":
    main()
