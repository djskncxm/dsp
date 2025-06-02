import importlib
import os
import sys
from inspect import iscoroutinefunction
from typing import Callable

from dsp.settings.settings_manager import SettingManager


def _get_cloest(path="."):
    return os.path.abspath(path)


def _init_env():
    cloest = _get_cloest()
    if cloest:
        project_dir = os.path.dirname(cloest)
        sys.path.append(project_dir)


def get_settings(settings="settings"):
    _settings = SettingManager()
    _init_env()
    _settings.set_settings(settings)
    return _settings


def merge_settings(spider, settings):
    if hasattr(spider, "custom_settings"):
        custom_settings = getattr(spider)
        settings.update_values(custom_settings)


def load_class(_path: str):
    if not isinstance(_path, str):
        if callable(_path):
            return _path
        else:
            raise TypeError(f"args expected string or object got => {type(_path)}")
    module, name = _path.rsplit(".", 1)
    mod = importlib.import_module(module)
    try:
        cls = getattr(mod, name)
    except AttributeError:
        raise NameError(f"module{module!r} doesn't define any object named {name!r}")
    return cls


async def common_call(func: Callable, *args, **kwargs):
    if iscoroutinefunction(func):
        return await func(*args, **kwargs)
    else:
        return func(*args, **kwargs)
