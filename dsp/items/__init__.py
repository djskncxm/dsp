from abc import ABCMeta


class Field(dict):
    pass


class ItemMeat(ABCMeta):
    def __new__(mcs, name, bases, attrs):
        field = {}
        for key, value in attrs.items():
            if isinstance(value, Field):
                field[key] = value
        cls_instance = super().__new__(mcs, name, bases, attrs)
        cls_instance.FIELDS = field
        return cls_instance
