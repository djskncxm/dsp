import os
import sys

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
