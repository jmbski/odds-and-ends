""" Base class for dataclasses in order to assign values to the class and generate argparse arguments. """

import argparse

str_to_type_mapping = {"int": int, "float": float, "str": str, "ascii": ascii}
""" Mapping of string types to Python types """

valid_arg_actions = [
    "store",
    "store_const",
    "store_true",
    "append",
    "append_const",
    "count",
    "help",
    "version",
]
""" List of valid argparse actions """


class OptionBase:
    """Base class for dataclasses in order to assign values to the class and generate argparse arguments."""

    def _assign(self, values: any, arg_parser: argparse.ArgumentParser = None) -> None:
        """Assign values to the class"""

        if not isinstance(values, dict):
            return

        arg_parser = arg_parser or argparse.ArgumentParser()

        def get_option_type(option: dict) -> type:
            """Get the type of the option

            Args:
                option (dict): The option dictionary

            Returns:
                type: The type of the option
            """

            return str_to_type_mapping.get(option.get("type"), str)

        def get_arg_options(option: dict) -> tuple:
            """Get the argument options

            Args:
                option (dict): The option dictionary

            Returns:
                tuple: The argument option values
            """

            opt_value = option.get("value")
            opt_alts = option.get("alts", [])
            opt_alts = [
                f"-{alt}" if not alt.startswith("-") else alt for alt in opt_alts
            ]
            opt_help = option.get("help", "")
            opt_action = option.get("action", "store")

            if opt_action not in valid_arg_actions:
                opt_action = "store"

            opt_type = get_option_type(option)

            if opt_type == bool or isinstance(opt_value, bool):
                opt_action = "store_false" if opt_value else "store_true"
                opt_type = None

            return opt_value, opt_alts, opt_help, opt_action, opt_type

        for opt_name, option in values.items():
            if isinstance(option, dict):
                opt_value, opt_alts, opt_help, opt_action, opt_type = get_arg_options(
                    option
                )
                if hasattr(self, opt_name):
                    setattr(self, opt_name, opt_value)

                if isinstance(arg_parser, argparse.ArgumentParser):
                    if opt_type is None:
                        arg_parser.add_argument(
                            f"--{opt_name}",
                            *opt_alts,
                            help=opt_help,
                            action=opt_action,
                        )
                    else:
                        arg_parser.add_argument(
                            f"--{opt_name}",
                            *opt_alts,
                            help=opt_help,
                            action=opt_action,
                            type=opt_type,
                        )

        return arg_parser
