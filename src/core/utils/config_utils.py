import os
import sys
import yaml
import logging
import settings
from pathlib import Path
from PyQt6.QtCore import QCoreApplication
from core.utils.alert_dialog import raise_error_alert, raise_info_alert
from core.validation.config import CONFIG_SCHEMA
from cssutils import css, CSSParser
from cerberus import Validator, schema

MAIN_CONFIGURATION_DIR = os.path.dirname(sys.argv[0])
HOME_CONFIGURATION_DIR = os.path.join(Path.home(), settings.DEFAULT_CONFIG_DIRECTORY)
HOME_STYLES_PATH = os.path.normpath(os.path.join(HOME_CONFIGURATION_DIR, settings.DEFAULT_STYLES_FILENAME))
HOME_CONFIG_PATH = os.path.normpath(os.path.join(HOME_CONFIGURATION_DIR, settings.DEFAULT_CONFIG_FILENAME))
DEFAULT_STYLES_PATH = os.path.normpath(os.path.join(MAIN_CONFIGURATION_DIR, settings.DEFAULT_STYLES_FILENAME))
DEFAULT_CONFIG_PATH = os.path.normpath(os.path.join(MAIN_CONFIGURATION_DIR, settings.DEFAULT_CONFIG_FILENAME))
GITHUB_ISSUES_URL = f"{settings.GITHUB_URL}/issues"

try:
    yaml_validator = Validator(CONFIG_SCHEMA)
except schema.SchemaError:
    logging.exception("Failed to load schema for config schema")
    raise Exception


def get_config_dir() -> str:
    if os.path.isdir(HOME_CONFIGURATION_DIR):
        return HOME_CONFIGURATION_DIR
    else:
        return MAIN_CONFIGURATION_DIR


def load_config(config_path) -> dict:
    with open(config_path) as yaml_stream:
        return yaml.safe_load(yaml_stream)


def load_stylesheet(stylesheet_path) -> css.CSSStyleSheet:
    parser = CSSParser(raiseExceptions=True)
    try:
        return parser.parseFile(stylesheet_path)
    except Exception as e:
        logging.exception(f"Failed to validate CSS in stylesheet {stylesheet_path}")
        raise_info_alert(
            title=f"Invalid CSS detected in {settings.DEFAULT_STYLES_FILENAME}",
            msg=(
                f"The some of the changes made in {settings.DEFAULT_STYLES_FILENAME} are invalid"
                " and may result in your styles being incorrectly applied. "
            ),
            informative_msg="Please click 'Show Details' for more information.",
            additional_details=e.__str__()
        )


def get_config() -> dict:
    if os.path.isdir(HOME_CONFIGURATION_DIR) and os.path.isfile(HOME_CONFIG_PATH):
        config_path = HOME_CONFIG_PATH
    else:
        config_path = DEFAULT_CONFIG_PATH

    try:
        config = load_config(config_path)

        if not yaml_validator.validate(config, CONFIG_SCHEMA):
            logging.exception(f"Failed to validate {settings.DEFAULT_CONFIG_FILENAME} at path {config_path}")
            pretty_errors = yaml.dump(yaml_validator.errors)
            raise_error_alert(
                title=f"Failed to validate {settings.DEFAULT_CONFIG_FILENAME}",
                msg=f"There are validation errors present in your {settings.DEFAULT_CONFIG_FILENAME} "
                    f"which need to be fixed."
                    f"\n\n{config_path}",
                informative_msg="Please click 'Show Details' to view the config fields which failed validation.",
                additional_details=pretty_errors
            )
        else:
            return yaml_validator.normalized(config)
    except Exception:
        logging.exception(f"Failed to load {settings.DEFAULT_CONFIG_FILENAME} at path {config_path}")
        title = f"Failed to load {settings.DEFAULT_CONFIG_FILENAME}"
        message = (
            f"This application requires a valid {settings.DEFAULT_CONFIG_FILENAME} file to be "
            "present in order to configure your  bar(s)."
        )
        informative_message = (
            "\nPlease check that a valid stylesheet file exists in:"
            f"\n - Your home directory ({HOME_CONFIG_PATH})"
            f"\n - Yasb's system directory ({DEFAULT_CONFIG_PATH})"
            "\n\n"
            "Please click 'Show Details' for more information.")
        raise_error_alert(title, message, informative_message)


def get_stylesheet() -> css.CSSStyleSheet:
    try:
        if os.path.isdir(HOME_CONFIGURATION_DIR) and os.path.isfile(HOME_STYLES_PATH):
            stylesheet_path = HOME_STYLES_PATH
        else:
            stylesheet_path = DEFAULT_STYLES_PATH

        return load_stylesheet(stylesheet_path)
    except Exception:
        logging.error(f"Failed to stylesheet {settings.DEFAULT_STYLES_FILENAME} at path {stylesheet_path}")
        title = f"Failed to load {settings.DEFAULT_STYLES_FILENAME}"
        message = (
            f"This application requires a valid {settings.DEFAULT_STYLES_FILENAME} file to be "
            "present in order to configure your bar(s)."
        )
        informative_message = (
            "\nPlease check that a valid stylesheet file exists in:"
            f"\n - Your home directory ({HOME_STYLES_PATH})"
            f"\n - Yasb's system directory ({DEFAULT_STYLES_PATH})"
            "\n\n"
            "Please click 'Show Details' for more information.")
        raise_error_alert(title, message, informative_message)


def get_config_and_stylesheet() -> tuple[dict, css.CSSStyleSheet]:
    try:
        config = get_config()
        stylesheet = get_stylesheet()
        logging.info("Successfully loaded config file and stylesheet")
        return config, stylesheet
    except Exception:
        logging.exception("Failed to load config and stylesheet")
        if not settings.DEBUG:
            raise_error_alert(
                title=f"{settings.APP_NAME} - Program Error",
                msg="Failed to load config and stylesheet files.",
                informative_msg=(
                    f"You can <strong>submit a bug report</strong> at:"
                    f"<br/><br/><a href='{GITHUB_ISSUES_URL}'>{GITHUB_ISSUES_URL}</a><br/><br/>"
                    "Please click 'Show Details' for more information."
                ),
                rich_text=True
            )
        QCoreApplication.exit(1)
