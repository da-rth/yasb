import os
import sys
import jstyleson
from pathlib import Path
from .alert_dialog import raise_error_alert


CONFIG_DIR_NAME = ".yabar"
STYLES_FILENAME = "styles.css"
CONFIG_FILENAME = "config.json"
HOME_CONFIGURATION_DIR = os.path.join(Path.home(), CONFIG_DIR_NAME)
HOME_STYLES_PATH = os.path.normpath(os.path.join(HOME_CONFIGURATION_DIR, STYLES_FILENAME))
HOME_CONFIG_PATH = os.path.normpath(os.path.join(HOME_CONFIGURATION_DIR, CONFIG_FILENAME))
DEFAULT_STYLES_PATH = os.path.normpath(os.path.join(os.path.dirname(sys.argv[0]), STYLES_FILENAME))
DEFAULT_CONFIG_PATH = os.path.normpath(os.path.join(os.path.dirname(sys.argv[0]), CONFIG_FILENAME))


def load_config(config_path) -> dict:
    with open(config_path) as json_file:
        return jstyleson.load(json_file)


def load_stylesheet(stylesheet_path) -> str:
    with open(stylesheet_path, "r") as css_file:
        return css_file.read()


def get_config():
    try:
        if os.path.isdir(HOME_CONFIGURATION_DIR) and os.path.isfile(HOME_CONFIG_PATH):
            return load_config(HOME_CONFIG_PATH)
        else:
            return load_config(DEFAULT_CONFIG_PATH)
    except Exception:
        title = f"Failed to load {CONFIG_FILENAME}"
        message = (
            f"This application requires a valid {CONFIG_FILENAME} file to be "
            "present in order to configure your  bar(s)."
        )
        informative_message = (
            "\nPlease check that a valid stylesheet file exists in:"
            f"\n - Your home directory ({HOME_CONFIG_PATH})"
            f"\n - Yasb's system directory ({DEFAULT_CONFIG_PATH})"
            "\n\n"
            "Please click 'Show Details' for more information.")
        raise_error_alert(title, message, informative_message)


def get_stylesheet() -> str:
    try:
        if os.path.isdir(HOME_CONFIGURATION_DIR) and os.path.isfile(HOME_STYLES_PATH):
            return load_stylesheet(HOME_STYLES_PATH)
        else:
            return load_stylesheet(DEFAULT_STYLES_PATH)
    except Exception:
        title = f"Failed to load {STYLES_FILENAME}"
        message = (
            f"This application requires a valid {STYLES_FILENAME} file to be "
            "present in order to configure your bar(s)."
        )
        informative_message = (
            "\nPlease check that a valid stylesheet file exists in:"
            f"\n - Your home directory ({HOME_STYLES_PATH})"
            f"\n - Yasb's system directory ({DEFAULT_STYLES_PATH})"
            "\n\n"
            "Please click 'Show Details' for more information.")
        raise_error_alert(title, message, informative_message)
