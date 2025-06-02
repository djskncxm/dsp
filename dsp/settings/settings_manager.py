import importlib

from collections.abc import MutableMapping
from copy import deepcopy

from dsp.settings import default_settings


class SettingManager(MutableMapping):
    def __init__(self, value=None):
        self.attributes = {}
        self.set_settings(default_settings)
        self.update_values(value)
        # "PROJECT_NAME":"",
        # "CONCURRENCY" : 16,

    def __getitem__(self, item):
        if item not in self:
            return None
        return self.attributes[item]

    def get(self, name, defaults):
        return self[name] if self[name] is not None else defaults

    def getint(self, name, defaults=0):
        return int(self.get(name, defaults=defaults))

    def getfloat(self, name, defaults=0):
        return float(self.get(name, defaults))


    def getbool(self, name, defaults=0):
        got = self.get(name, defaults)
        try:
            return bool(int(got))
        except ValueError:
            if got in ("True", "true", "TRUE"):
                return True
            if got in ("False", "false", "FALSE"):
                return False
            raise ValueError("请传递一个bool值或者数字")

    def getlist(self, name, defaults=None):
        value = self.get(name, defaults or [])
        if isinstance(value, str):
            value.split(",")
        return list(value)

    def __contains__(self, item):
        return item in self.attributes

    def __setitem__(self, key, value):
        self.set(key, value)

    def set(self, key, value):
        self.attributes[key] = value

    def __delitem__(self, key):
        del self.attributes[key]

    def delete(self, key):
        del self.attributes[key]

    def set_settings(self, module):
        if isinstance(module, str):
            module = importlib.import_module(module)
        for key in dir(module):
            if key.isupper():
                self.set(key, getattr(module, key))

    def __str__(self):
        return f"<Settings values => {self.attributes}>"

    def __iter__(self):
        return iter(self.attributes)

    def __len__(self):
        return len(self.attributes)

    def update_values(self, values):
        if values is not None:
            for key, value in values.items():
                self.set(key, value)

    def copy(self):
        return deepcopy(self)

    __repr = __str__
