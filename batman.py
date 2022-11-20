"""

Tool for exception handling and logging

"""

import re
from sys import exc_info
import traceback
import datetime
import functools
from types import SimpleNamespace
from collections.abc import Callable, Iterable
from typing import Any, Optional


class _EmptyExceptionClass(BaseException):
    """ Dummy exception class represents 'None' or emptyness. It's never occurred exception """
    pass


class ExitBatmanArea(BaseException):
    """
    Custom exception raised for instant exit batman_area context
    Useful when use Batman behavior as a part of logic

    This exception consistently handled in  batman_area  implementation,
    or raised by default under decorator

    """
    pass


def _str2exc(exception_class_name: str, *, _rgc_classname=[re.compile(r"^[A-Z][a-zA-Z0-9]+$")]):
    """ returns Exception-class-object from its name
    """
    if not exception_class_name:
        # Any argument represented as False or None must return _EmptyExceptionClass
        return _EmptyExceptionClass
    # some assertions to validate class name before  eval()
    assert 2 <= len(exception_class_name) <= 79, "Length of a class name assertion (2..79) fail"
    # pattern of pythonic style exception class name  (kinda getting from cache once compiled)
    assert _rgc_classname[0].match(exception_class_name), "Classname looks pythonic assertion fail"

    try:
        exc_type = eval(exception_class_name)  # 'exception class object from class name' magic
    except:
        raise NameError(f"There is no exception with name {exception_class_name}")
    else:
        if not issubclass(exc_type, BaseException):
            raise TypeError(f"Exceptions must be derived from 'BaseException' class")
        else:
            return exc_type


class _Singleton:
    # got from
    # https://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    """
    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)


def _default_bat_writer(**kwargs) -> str:
    fail_value = kwargs.get("fail_value", "")     # fail_value to be returned by decorator
    text = kwargs.get("text", "")
    exc = kwargs.get("exc", None)                 # exception object (in some cases)
    exc_traceback = kwargs.get("exc_traceback", None)                      # traceback object
    exc_traceback_formatted = kwargs.get("exc_traceback_formatted", None)  # str repr of traceback
    exc_time = kwargs.get("exc_time", "")
    exc_type = kwargs.get("exc_type", "")
    exc_value = kwargs.get("exc_value", "")

    # message format to send to batman
    message = f"\n" \
              f"[{exc_time}] {text} -> {exc_type}\n" \
              f"{exc_traceback_formatted}"
    return message


def _default_bat_messenger(message: str) -> None:
    print(message)


# =======================================
# by default built-in BaseException's special first-level descendants will be raised
default_to_raise_set = frozenset({'GeneratorExit',
                                  'KeyboardInterrupt',
                                  'SystemExit',
                                  'ExitBatmanArea'})
# ========


@_Singleton
class _BatmanRecord(SimpleNamespace):
    # by default built-in BaseException's first-level descendants will be raised
    to_raise: Optional[Iterable[str]] = default_to_raise_set
    # by default only Exception descendants will be sent
    to_send: Optional[Iterable[str]] = frozenset({'Exception'})

    bat_messenger: Callable[[str], Optional[Any]] = staticmethod(_default_bat_messenger)
    bat_writer: Callable[[dict], str] = staticmethod(_default_bat_writer)


# =======================================
""" Create once instance of setup singleton """
bat_setup: _BatmanRecord = _BatmanRecord.instance()
# ========


# send user message to batman
def send_to_batman(message: str) -> Optional[Any]:
    try:
        return bat_setup.bat_messenger(message)
    except:
        print("*ALARM!*")
        print("Batman's messenger is broken")
        print("Trying to send message thru default messenger")
        _default_bat_messenger(message)


# =======================================
""" Alias name for send_to_batman(). Just for three-letter use instead of log() """
bat = send_to_batman
# ========


# decorator
def batman(text: str = "",
           *,
           fail_value: Optional[Any] = None,
           to_raise: Optional[Iterable[str]] = bat_setup.to_raise,
           to_send:  Optional[Iterable[str]] = bat_setup.to_send) -> Callable:
    def batpower(f: Callable) -> Callable:

        @functools.wraps(f)
        def wrapper(*args, **kwargs) -> Any:
            result = fail_value
            try:
                result = f(*args, **kwargs)
            except BaseException as e:
                # refine situation
                exc_time = datetime.datetime.now()
                exc_type, exc_value, exc_traceback = exc_info()
                exc_traceback_formatted = traceback.format_exc()

                # compose message to batman
                msg = bat_setup.bat_writer(text=text,
                                           exc=e,
                                           fail_value=fail_value,
                                           exc_time=exc_time,
                                           exc_type=exc_type,
                                           exc_value=exc_value,
                                           exc_traceback=exc_traceback,
                                           exc_traceback_formatted=exc_traceback_formatted)
                # send to batman if nesessary
                if to_send:
                    flag_to_send = issubclass(e.__class__,
                                              (*[_str2exc(exc_name) for exc_name in to_send],))
                    if flag_to_send:
                        send_to_batman(msg)

                # raise if nesessary
                if to_raise:
                    flag_to_raise = issubclass(e.__class__,
                                               (*[_str2exc(exc_name) for exc_name in to_raise],))
                    if flag_to_raise:
                        raise e
            else:
                pass

            return result

        # ---
        return wrapper
    # ---
    return batpower


# context manager
class batman_area:
    def __init__(self,
                 text: str = "",
                 *,
                 to_raise: Optional[Iterable[str]] = bat_setup.to_raise,
                 to_send:  Optional[Iterable[str]] = bat_setup.to_send):
        self._text = text
        self._to_raise = to_raise
        self._to_send = to_send

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is not None:
            # refine situation
            exc_time = datetime.datetime.now()
            exc_type, exc_value, exc_traceback = exc_info()
            exc_traceback_formatted = traceback.format_exc()

            # send to batman if nesessary
            if self._to_send:
                flag_to_send = issubclass(exc_type,
                                          (*[_str2exc(exc_name) for exc_name in self._to_send],))
                if flag_to_send:
                    # compose message
                    msg = bat_setup.bat_writer(text=self._text,
                                               exc=None,  # currently not implemented
                                               fail_value=None,  # useless in context manager
                                               exc_time=exc_time,
                                               exc_type=exc_type,
                                               exc_value=exc_value,
                                               exc_traceback=exc_traceback,
                                               exc_traceback_formatted=exc_traceback_formatted)
                    send_to_batman(msg)

            # raise if nesessary
            if self._to_raise:
                flag_to_raise = issubclass(exc_type,
                                           (*[_str2exc(exc_name) for exc_name in self._to_raise],))
                if flag_to_raise:
                    if exc_type == ExitBatmanArea:
                        # Exit batman_area code
                        pass
                    else:
                        raise

        # for __exit__ method  return True  means 'Exception has not to be rased'
        return True


# =================

def assertion_friendly_bat_message_format(**kwargs) -> str:
    fail_value = kwargs.get("fail_value", "")     # fail_value to be returned by decorator
    text = kwargs.get("text", "")
    exc = kwargs.get("exc", None)                 # exception object (in some cases)
    exc_traceback = kwargs.get("exc_traceback", None)                      # traceback object
    exc_traceback_formatted = kwargs.get("exc_traceback_formatted", None)  # str repr of traceback
    exc_time = kwargs.get("exc_time", "")
    exc_type = kwargs.get("exc_type", "")
    exc_value = kwargs.get("exc_value", "")

    # format message to send
    if exc_type == AssertionError:
        message = f"\n" \
                  f"[{exc_time}] {text} -> {exc_type}\n" \
                  f"{exc_traceback_formatted}"
    else:
        message = f"\n" \
                  f"[{exc_time}] {text} -> {exc_type}\n" \
                  f"{exc_traceback_formatted}"
    return message
