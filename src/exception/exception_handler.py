from kivy.base import ExceptionHandler, ExceptionManager

from exception.exception import ConfigError
from view.components.custom_toast.custom_toast import toast


class CustomExceptionHandler(ExceptionHandler):
    def handle_exception(self, inst):
        if isinstance(inst, ConfigError):
            toast(repr(inst), duration=5)
            return ExceptionManager.PASS
        else:
            return ExceptionManager.RAISE
