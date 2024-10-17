""" Utilities to configure logging using the Configurator """

import json
import logging
import logging.config
import os

from jmble.config import Configurator
from jmble.general_modules import utils
from jmble._types import AttrDict

CONFIG = Configurator()
ENV_PROPS = CONFIG.get_environment()


def configure_logging(
    app_name: str = None, default_logger_name: str | None = None
) -> logging.Logger:
    """Configure logging using the Configurator.

    Args:
        app_name (str, optional): Name of the application. Defaults to None.
        default_logger_name (str, optional): Name of the default logger to return.
            Defaults to None. If None, returns a tuple of the defined loggers.

    Returns:
        logging.Logger | tuple[logging.Logger]: Logger instance or tuple of loggers.
    """

    app_props = CONFIG.get(app_name) if app_name else AttrDict()

    log_config = ENV_PROPS.get("base_python_log_cfg", AttrDict())

    if not isinstance(log_config, AttrDict) and isinstance(log_config, dict):
        log_config = AttrDict(log_config)

    log_settings = app_props.logging
    loggers: tuple | None = None

    if log_settings:
        if "handlers" in log_settings:
            try:
                log_config.handlers.update(log_settings.handlers)
            except Exception as e:
                print(f"Error updating handlers: {e}")
                print(f"handlers: {log_settings.handlers}")
        if "loggers" in log_settings:
            try:
                log_config.loggers.update(log_settings.loggers)
                loggers = tuple(
                    (logging.getLogger(name) for name in log_settings.loggers)
                )
            except Exception as e:
                print(f"Error updating loggers: {e}")
                print(f"loggers: {log_settings.loggers}")

    _check_log_paths(log_config)

    try:
        logging.config.dictConfig(log_config)
    except Exception as e:
        print(f"Error configuring logging: {e}")
        # print(f"log_config: {json.dumps(log_config, indent=4)}")

    if default_logger_name:
        return logging.getLogger(default_logger_name)
    else:
        return loggers


def _check_log_paths(log_config: AttrDict) -> None:
    """Check the log paths and create them if they do not exist.

    Args:
        log_config (AttrDict): Log configuration.
    """

    for handler in log_config.handlers.values():
        if "filename" in handler:
            log_path = os.path.expanduser(handler.filename)
            log_dir = os.path.dirname(log_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
