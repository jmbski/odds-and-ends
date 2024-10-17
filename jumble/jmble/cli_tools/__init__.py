""" Entrypoint for the CLI tools. """

from . import config_cli, version_manager

print(__package__)
__all__ = ["version_manager", "config_cli"]
