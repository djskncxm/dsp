import copy
from pprint import pformat
from collections.abc import MutableMapping

from dsp.items import ItemMeat
from dsp.exceptions import ItemInitError


class Item(MutableMapping, metaclass=ItemMeat):
    FIELDS: dict = dict()

    def __init__(self, *args, **kwargs):
        self._values = {}
        if args:
            raise ItemInitError(
                f"{self.__class__.__name__}: position args is not supported, use keyword args."
            )
        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __setitem__(self, key, value):
        if key in self.FIELDS:
            self._values[key] = value
        else:
            raise KeyError(f"{self.__class__.__name__} 不支持 {key}")

    def __getitem__(self, item):
        return self._values[item]

    def __setattr__(self, key, value):
        if not key.startswith("_"):
            raise AttributeError("不能用.的方式来进行操作值，请使用[]进行操作")
        super().__setattr__(key, value)

    def __repr__(self):
        return pformat(dict(self))

    def __getattr__(self, item):
        raise AttributeError(
            f"{self.__class__.__name__}没找到{item}，请你加入{self.__class__.__name__}和使用item[{item!r}] 获取值"
        )

    def __getattribute__(self, item):
        field = super().__getattribute__("FIELDS")
        if item in field:
            raise ItemInitError(f"请使用[{item!r}]可以获取value")
        else:
            return super().__getattribute__(item)

    def __delitem__(self, key):
        del self._values[key]

    def __iter__(self):
        return iter(self._values)

    def __len__(self):
        return len(self._values)

    def to_dict(self):
        return dict(self)

    def copy(self):
        return copy.deepcopy(self)

    __str__ = __repr__
