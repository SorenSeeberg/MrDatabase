#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Base class for mr_database tables

class members describe the schema
instance members describe the record 
static members are utility

"""

import json
import copy
import sqlite3 as sqlite
import hashlib
from typing import Dict, Generator, List, Tuple
from mr_database.data_formatting import DataFormatting
from mr_database.column import Column


class Table:
    __join_table_definitions__: Dict = dict()
    __join_tables__: Dict = dict()

    @classmethod
    def __get_named_col_pairs__(cls):

        return zip(cls.get_columns(), cls.get_col_names())

    @classmethod
    def __create_table__(cls) -> str:
        """ Constructs the needed sql statements to create a mr_database table from a Table class """

        sql = list()
        sql.append(f'CREATE TABLE IF NOT EXISTS {cls.get_table_name()}(')

        sql_properties = list()
        sql_foreign_keys = list()

        for column, prop_name in cls.__get_named_col_pairs__():
            property_components = list()

            property_components.append(prop_name)
            property_components.append(column.data_type)

            if column.pk:
                if column.data_type == column.data_types.integer:
                    property_components.append('PRIMARY KEY AUTOINCREMENT')
                else:
                    property_components.append('PRIMARY KEY')

            if column.default is not None:
                property_components.append(f'DEFAULT {DataFormatting.value_to_string(column, column.default, default=True)}')

            if column.unique:
                property_components.append('UNIQUE')

            if column.not_null:
                property_components.append('NOT NULL')

            if column.pk:
                sql_properties.insert(0, ' '.join(property_components))
            else:
                sql_properties.append(' '.join(property_components))

            if column.fk:
                if hasattr(column, 'fk_table'):
                    sql_foreign_keys.append(f'FOREIGN KEY ({prop_name}) '
                                            f'REFERENCES {column.fk_table.get_table_name()}({column.fk_property})')
                elif hasattr(column, 'fk_table_name'):
                    sql_foreign_keys.append(f'FOREIGN KEY ({prop_name}) '
                                            f'REFERENCES {column.fk_table_name}({column.fk_property})')

        sql.append(', \n'.join(sql_properties + sql_foreign_keys))
        sql.append(');')

        return ' \n'.join(sql)

    @classmethod
    def __drop_table__(cls) -> str:
        """Constructs the needed sql statements to drop a mr_database table from a Table class"""

        return f'DROP TABLE IF EXISTS {cls.get_table_name()};'

    @classmethod
    def has_int_pk(cls) -> Tuple[str]:
        return tuple(col_pair[1] for col_pair in cls.__get_named_col_pairs__() if col_pair[0].pk and col_pair[0].data_type == Column.data_types.integer)

    @classmethod
    def get_table_name(cls) -> str:
        if issubclass(cls, Table):
            return cls.__name__
        else:
            return cls.__class__.__name__

    @classmethod
    def get_columns(cls) -> Generator[Column, None, None]:
        """ Returns the Column objects of a table. Using self.get_table_property_names to guarantee property order """

        if issubclass(cls, Table):
            return (value for attr, value in cls.__dict__.items() if isinstance(value, Column))
        else:
            return (value for attr, value in cls.__class__.__dict__.items() if isinstance(value, Column))

    @classmethod
    def get_col_names(cls) -> Generator[str, None, None]:
        """ Returns class level attribute names (excluding privates and callables) """

        if issubclass(cls, Table):
            return (attr for attr, value in cls.__dict__.items() if isinstance(value, Column))
        else:
            return (attr for attr, value in cls.__class__.__dict__.items() if isinstance(value, Column))

    @classmethod
    def get_col_display_names(cls) -> Tuple[str]:
        """ Returns the display names of each column if they exist. Fallback is attribute name """

        display_names: Generator[str, None, None] \
            = (getattr(cls, col_name).display_name if getattr(cls, col_name).display_name is not None else col_name
               for col_name in cls.get_col_names())

        return tuple(display_names)

    @classmethod
    def get_attr_name_by_index(cls, index) -> str:
        return list(cls.get_col_names())[index]

    @staticmethod
    def read_blob_file(data):
        return sqlite.Binary(data.read())

    @staticmethod
    def md5_file_object(file_object) -> str:
        md5 = hashlib.md5(file_object.read()).hexdigest()
        file_object.seek(0)
        return md5

    def __init__(self):
        self.__setup_default_value__()
        self.__init_join_tables__()

    def __setup_default_value__(self):
        [setattr(self, prop_name, column.default) for column, prop_name in self.__get_named_col_pairs__()]

    def __init_join_tables__(self):

        for column, prop_name in self.__get_named_col_pairs__():

            if not column.fk:
                continue

            if hasattr(column, 'fk_table'):
                join_table_class = column.fk_table
                fk_table_name = column.fk_table.__name__
            else:
                join_table_class = self.__class__
                fk_table_name = column.fk_table_name

            # todo : simplify the dict . . just the column is needed
            self.__join_table_definitions__[fk_table_name] = {'table_class': join_table_class,
                                                              'fk': column.fk_property,
                                                              'property': prop_name,
                                                              'column': column}

    def __getitem__(self, item):
        return getattr(self, item)

    def __repr__(self) -> str:
        x = (f'{a} : {b}' for a, b in zip(list(self.get_col_names()), list(self.get_values())))

        repr_string = f'{self.get_table_name()} ({", ".join(x)})'

        return repr_string

    def __get_value_by_index__(self, index: int):
        """ Gets the value of the nth attribute """

        try:
            return getattr(self, list(self.get_col_names())[index])
        except:
            return False

    def __set_value_by_index__(self, index: int, value) -> bool:
        """ Sets the value of the nth attribute """

        try:
            attrib = list(self.get_col_names())[index]
            setattr(self, attrib, value)
            return True
        except:
            return False

    def get_attributes(self) -> Generator[str, None, None]:
        """ returns instance level attribute names (excluding privates and callables) """

        return (attr for attr, value in self.__dict__.items() if not callable(getattr(self, attr)) and not attr.startswith("__"))

    def get_values(self) -> Generator:
        """ Returns a generator for all the values """

        return (getattr(self, column_name) for column_name in self.get_col_names())

    def add_table_to_join_table_dict(self, key, value) -> None:

        self.__join_tables__[key] = value

    def fetch_join_tables(self, db_object: 'MrDatabase') -> None:

        [self.add_table_to_join_table_dict(join_table_name, self.select_join_record(db_object, join_table_name)) for join_table_name in self.__join_table_definitions__.keys()]

    def select_join_record_all(self, db_object: 'MrDatabase') -> Tuple['Table']:
        """ returning row objects for all join tables """

        return tuple((self.select_join_record(db_object, join_table_name) for join_table_name in self.__join_table_definitions__.keys()))

    def select_join_record(self, db_object: 'MrDatabase', join_table_name: str) -> 'Table':
        """ returning row object for a specific join table """

        fk_table_info = self.__join_table_definitions__.get(join_table_name)

        if fk_table_info is None:
            return

        value = getattr(self, fk_table_info.get('property'))
        column = fk_table_info.get('column')

        if value is None:
            return

        condition = f'{fk_table_info.get("fk")}={DataFormatting.value_to_string(column, value)}'

        return db_object.select_record(fk_table_info.get('table_class'), condition)

    def default_update_condition(self) -> str:
        """ Returning sql definition of default update condition """

        return f'id = {self.id}'

    def from_sql_record(self, sql_row: List) -> None:
        """ Sets the record values from a sql record of type list """

        for column_name, value in zip(self.get_col_names(), sql_row):
            setattr(self, column_name, value)

    def reset_to_default(self) -> None:
        """ Resets the values of the instance to the defined default values of each Column """

        for column, column_name in self.__get_named_col_pairs__():
            setattr(self, column_name, column.default)

    def from_json(self, json_string: str) -> None:
        """ Sets the record values from a json string """

        json_object = json.loads(json_string)

        for column, column_name in self.__get_named_col_pairs__():
            setattr(self, column_name, json_object.get(column_name, column.default))

    def to_json(self) -> str:
        """ Returns a json string containing the table name, column names and values """

        json_data = dict()

        json_data["table_name"] = self.get_table_name()
        json_data["headers"] = list(self.get_col_names())

        for prop_name in self.get_col_names():
            json_data[prop_name] = getattr(self, prop_name)

        return json.dumps(json_data)

    def clone(self) -> 'self':
        """ Returns a deep copy of self """
        return copy.deepcopy(self)




