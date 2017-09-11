#!/usr/bin/python3
# -*- coding: utf-8 -*-

from typing import List, Any
from database.table import Table


class Records:

    def __init__(self, records: List[Table.__subclasses__]):
        super().__init__()

        self.__table_class__ = records[0].__class__
        self.__records__: List[Table.__subclasses__] = list(records)

    def __getitem__(self, index: int):
        return self.__records__[index]

    def __len__(self) -> int:
        return len(self.__records__)

    def __add__(self, other: List['Table.__subclasses__']):
        self.__records__ += other

    def __sub__(self, other):
        pass

    def sort(self, attribute_index: int, reverse: bool=False) -> None:

        # attr: str = list(self.__records__[0].get_class_column_names())[attribute_index]
        if self.__records__:
            records = self.__records__
            attr: str = self.__table_class__.get_attribute_name_by_index(attribute_index)
            records.sort(key=lambda x: x[attr], reverse=reverse)

    def append(self, value: Any) -> None:
        self.__records__.append(value)

    def insert(self, index: int, value) -> None:
        self.__records__.insert(index, value)

    def pop(self, index: int=-1) -> Any:
        return self.__records__.pop(index)

    def remove(self, value) -> None:
        self.__records__.remove(value)

    def table_class(self):
        return self.__table_class__

    def index(self, value: Any, start: int=0, stop: int=None) -> int:
        return self.__records__.index(value, start, stop)

    # def raw_data(self, update=True) -> List[List['Table']]:
    #
    #     if update:
    #         self.__raw_data__.clear()
    #         self.__raw_data__ = [list(record.get_values()) for record in self.__records__]
    #
    #     return self.__raw_data__

    def max(self):
        pass

    def min(self):
        pass

    def first(self):
        pass

    def last(self):
        pass
