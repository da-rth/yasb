import yaml
import logging
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject
from typing import Optional
from cerberus import Validator
from importlib import import_module
from .alert_dialog import raise_info_alert
from ...settings import DEFAULT_CONFIG_FILENAME


class WidgetBuilder(QObject):
    def __init__(self, widget_configs: dict):
        super().__init__()
        self._widget_event_listeners = set()
        self._widget_configurations = widget_configs
        self._missing_widget_types = set()
        self._invalid_widget_names = set()
        self._invalid_widget_types = {}
        self._invalid_widget_options = {}

    def build_widgets(self, widget_map: dict[str, list[str]]) -> tuple[dict[str, list[QWidget]], set]:
        bar_widgets = {}

        for column, widget_names in widget_map.items():
            built_widgets = [self._build_widget(widget_name) for widget_name in widget_names]
            bar_widgets[column] = [widget for widget in built_widgets if widget is not None]

        return bar_widgets, self._widget_event_listeners

    def _build_widget(self, widget_name: str) -> Optional[QWidget]:
        widget_config = self._widget_configurations.get(widget_name, None)

        if (widget_name in self._invalid_widget_names) or (widget_name in self._invalid_widget_options):
            logging.warning(f"Ignoring construction of invalid widget '{widget_name}'")
        elif not widget_config:
            self._invalid_widget_names.add(widget_name)
            logging.warning(f"No widget config could be found for widget '{widget_name}")
        else:
            try:
                widget_module_str, widget_class_str = widget_config['type'].rsplit('.', 1)
                widget_module = import_module(f"core.widgets.{widget_module_str}")
                widget_cls = getattr(widget_module, widget_class_str)
                widget_schema = getattr(widget_cls, 'validation_schema')
                widget_event_listener = getattr(widget_cls, 'event_listener')

                if type(widget_schema) != dict and not widget_schema:
                    raise Exception(f"The widget {widget_cls.__name__} has no validation_schema")

                if widget_event_listener:
                    self._widget_event_listeners.add(widget_event_listener)

                widget_options_validator = Validator(widget_schema)
                widget_options = widget_config.get('options', {})

                if not widget_options_validator.validate(widget_options, widget_schema):
                    validation_errors = yaml.dump(widget_options_validator.errors)
                    indented_validation_errors = f"\n{validation_errors}".replace("\n", "\n      ")
                    self._invalid_widget_options[widget_name] = indented_validation_errors
                else:
                    normalized_options = widget_options_validator.normalized(widget_options)
                    return widget_cls(**normalized_options)
            except (AttributeError, ValueError, ModuleNotFoundError):
                logging.exception(f"Failed to import widget with type {widget_config['type']}")
                self._invalid_widget_types[widget_name] = widget_config['type']
            except KeyError:
                logging.exception(f"No type specified for widget '{widget_name}'")
                self._missing_widget_types.add(widget_name)
            except Exception:
                logging.exception(f"Failed to import widget '{widget_name}'")

    def raise_alerts_if_errors_present(self):
        if self._invalid_widget_names:
            undefined_widgets = "\n".join([
                f" - The widget \"{widget_name}\" is undefined." for widget_name in self._invalid_widget_names
            ])
            raise_info_alert(
                title=f"Failed to add undefined widget(s) in {DEFAULT_CONFIG_FILENAME}",
                msg="Failed to add undefined widget(s) to bar.",
                informative_msg="Please click 'Show Details' to find out more.",
                additional_details=undefined_widgets
            )
        if self._invalid_widget_options:
            additional_details = "\n".join([(
                f" - {widget_name}{validation_errors}"
            ) for widget_name, validation_errors in self._invalid_widget_options.items()])
            raise_info_alert(
                title=f"Failed to validate widget(s) in {DEFAULT_CONFIG_FILENAME}",
                msg="Failed to validate widget(s) due to invalid options",
                informative_msg="Please click 'Show Details' to find out more.",
                additional_details=additional_details
            )
        if self._invalid_widget_types:
            widget_names_and_types = "\n".join([
                f" - {widget_name} has unknown type \"{widget_type}\""
                for widget_name, widget_type in self._invalid_widget_types.items()
            ])
            raise_info_alert(
                title=f"Failed to build widget(s) in {DEFAULT_CONFIG_FILENAME}",
                msg="Failed to build widget(s) of unknown widget type(s)",
                informative_msg="Click 'Show Details' to find out more.",
                additional_details=widget_names_and_types
            )
        if self._missing_widget_types:
            widget_names = "\n".join([f" - {widget_name}" for widget_name in self._missing_widget_types])
            raise_info_alert(
                title=f"Failed to import widget(s) in {DEFAULT_CONFIG_FILENAME}",
                msg="Failed to import widget(s) with missing widget type(s)",
                informative_msg="Please click 'Show Details' to find out more.",
                additional_details=f"The following widget(s) have no widget type defined:\n{widget_names}"
            )
