import yaml
import traceback
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject
from typing import Optional
from cerberus import Validator
from importlib import import_module
from core.utils.alert_dialog import raise_info_alert
from core.utils.config_loader import CONFIG_FILENAME


class WidgetBuilder(QObject):
    def __init__(self, widget_configs: dict):
        super().__init__()
        self._widget_configs = widget_configs
        self._missing_widget_types = set()
        self._invalid_widget_names = set()
        self._invalid_widget_types = {}
        self._invalid_widget_options = {}

    def build_widgets(self, widget_map: dict[str, list[str]]) -> dict[str, list[QWidget]]:
        bar_widgets = {}
        for column, widget_names in widget_map.items():
            built_widgets = [self._build_widget(widget_name) for widget_name in widget_names]
            bar_widgets[column] = [widget for widget in built_widgets if widget is not None]
        return bar_widgets

    def _build_widget(self, widget_name: str) -> Optional[QWidget]:
        widget_config = self._widget_configs.get(widget_name, None)

        if (widget_name in self._invalid_widget_names) or (widget_name in self._invalid_widget_options):
            print("Ignoring construction of invalid widget", widget_name)
        elif not widget_config:
            self._invalid_widget_names.add(widget_name)
            print("No widget config could be found for widget", widget_name)
        else:
            try:
                widget_module_str, widget_class_str = widget_config['type'].rsplit('.', 1)
                widget_module = import_module(f"core.widgets.{widget_module_str}")
                widget_cls = getattr(widget_module, widget_class_str)

                if not hasattr(widget_cls, 'validation_schema'):
                    raise Exception(f"The widget {widget_cls.__name__} has no validation_schema")

                widget_schema = getattr(widget_cls, 'validation_schema')
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
                print("Failed to import widget with type", widget_config['type'], traceback.format_exc())
                self._invalid_widget_types[widget_name] = widget_config['type']
            except KeyError:
                print("No type specified for widget", widget_name, traceback.format_exc())
                self._missing_widget_types.add(widget_name)
            except Exception:
                print(f"Failed to import widget '{widget_name}':", traceback.format_exc())

    def raise_alerts_if_errors_present(self):
        if self._invalid_widget_names:
            undefined_widgets = "\n".join([
                f" - The widget \"{widget_name}\" is undefined." for widget_name in self._invalid_widget_names
            ])
            raise_info_alert(
                title=f"Failed to add undefined widget(s) in {CONFIG_FILENAME}",
                msg="Failed to add undefined widget(s) to bar.",
                informative_msg="Please click 'Show Details' to find out more.",
                additional_details=undefined_widgets
            )
        if self._invalid_widget_options:
            additional_details = "\n".join([(
                f" - {widget_name}{validation_errors}"
            ) for widget_name, validation_errors in self._invalid_widget_options.items()])
            raise_info_alert(
                title=f"Failed to validate widget(s) in {CONFIG_FILENAME}",
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
                title=f"Failed to build widget(s) in {CONFIG_FILENAME}",
                msg="Failed to build widget(s) of unknown widget type(s)",
                informative_msg="Click 'Show Details' to find out more.",
                additional_details=widget_names_and_types
            )
        if self._missing_widget_types:
            widget_names = "\n".join([f" - {widget_name}" for widget_name in self._missing_widget_types])
            raise_info_alert(
                title=f"Failed to import widget(s) in {CONFIG_FILENAME}",
                msg="Failed to import widget(s) with missing widget type(s)",
                informative_msg="Please click 'Show Details' to find out more.",
                additional_details=f"The following widget(s) have no widget type defined:\n{widget_names}"
            )
