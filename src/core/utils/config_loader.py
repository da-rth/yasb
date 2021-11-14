import os
import sys
import yaml
from pathlib import Path
from core import settings
from core.utils.alert_dialog import raise_error_alert, raise_info_alert
from core.validation.config import CONFIG_SCHEMA
from cssutils import css, CSSParser, parseFile
from cerberus import Validator, schema
from pprint import pprint

HOME_CONFIGURATION_DIR = os.path.join(Path.home(), settings.DEFAULT_CONFIG_DIRECTORY)
HOME_STYLES_PATH = os.path.normpath(os.path.join(HOME_CONFIGURATION_DIR, settings.DEFAULT_STYLES_FILENAME))
HOME_CONFIG_PATH = os.path.normpath(os.path.join(HOME_CONFIGURATION_DIR, settings.DEFAULT_CONFIG_FILENAME))
DEFAULT_STYLES_PATH = os.path.normpath(os.path.join(os.path.dirname(sys.argv[0]), settings.DEFAULT_STYLES_FILENAME))
DEFAULT_CONFIG_PATH = os.path.normpath(os.path.join(os.path.dirname(sys.argv[0]), settings.DEFAULT_CONFIG_FILENAME))
GITHUB_ISSUES_URL = f"{settings.GITHUB_URL}/issues"

try:
    yaml_validator = Validator(CONFIG_SCHEMA)
except schema.SchemaError as e:
    pprint(e)
    raise Exception


def load_config(config_path) -> dict:
    with open(config_path) as yaml_stream:
        return yaml.safe_load(yaml_stream)


def load_stylesheet(stylesheet_path) -> css.CSSStyleSheet:
    parser = CSSParser(raiseExceptions=True)
    try:
        return parser.parseFile(stylesheet_path)
    except Exception as e:
        raise_info_alert(
            title=f"Invalid CSS detected in {settings.DEFAULT_STYLES_FILENAME}",
            msg=(
                f"The some of the changes made in {settings.DEFAULT_STYLES_FILENAME} are invalid"
                " and may result in your styles being incorrectly applied. "
            ),
            informative_msg="Please click 'Show Details' for more information.",
            additional_details=e.__str__()
        )
    finally:
        return parseFile(stylesheet_path)


def get_config() -> dict:
    try:
        if os.path.isdir(HOME_CONFIGURATION_DIR) and os.path.isfile(HOME_CONFIG_PATH):
            config_path = HOME_CONFIG_PATH
            config = load_config(HOME_CONFIG_PATH)
        else:
            config_path = DEFAULT_CONFIG_PATH
            config = load_config(DEFAULT_CONFIG_PATH)

        if not yaml_validator.validate(config, CONFIG_SCHEMA):
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
            return load_stylesheet(HOME_STYLES_PATH)
        else:
            return load_stylesheet(DEFAULT_STYLES_PATH)
    except Exception:
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


def get_config_and_stylesheet(debug_mode: bool = False) -> tuple[dict, css.CSSStyleSheet]:
    try:
        config = get_config()
        stylesheet = get_stylesheet()
        return config, stylesheet
    except Exception:
        if not debug_mode:
            raise_error_alert(
                title="Program Error",
                msg="This application has encountered a critical error. Sorry about that.",
                informative_msg=(
                    f"You can <strong>submit a bug report</strong> at:"
                    f"<br/><br/><a href='{GITHUB_ISSUES_URL}'>{GITHUB_ISSUES_URL}</a><br/><br/>"
                    "Please click 'Show Details' for more information."
                ),
                rich_text=True
            )
        else:
            raise Exception
