#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Base class for database tables

class members describe the schema
instance members describe the record 
static members are utility

"""

import json
import logging
import sqlite3 as sqlite
import hashlib
from typing import Dict, Generator, List, Tuple
from database.data_formatting import DataFormatting
from database.column import Column


class Table:
    __table_name__ = None
    __join_table_definitions__: Dict = dict()
    __join_tables__: Dict = dict()

    @classmethod
    def get_schema_columns(cls) -> Generator[Column, None, None]:
        """ Returns the Column objects of a table. Using self.get_table_property_names to guarantee property order """

        return (getattr(cls, prop_name) for prop_name in cls.get_class_column_names())

    @classmethod
    def get_class_column_names(cls) -> Generator[str, None, None]:
        """ Returns class level attribute names (excluding privates and callables) """

        return (attr for attr, value in cls.__dict__.items() if not callable(getattr(cls, attr)) and not attr.startswith("__"))

    @classmethod
    def get_attribute_name_by_index(cls, index) -> str:

        return list(cls.get_class_column_names())[index]

    @classmethod
    def __create_table__(cls) -> str:
        """ Constructs the needed sql statements to create a database table from a Table class """

        sql = list()
        sql.append("CREATE TABLE IF NOT EXISTS %s(" % cls.__table_name__)

        sql_properties = list()
        sql_foreign_keys = list()

        for column in cls.get_schema_columns():
            property_components = list()

            property_components.append(column.property_name)
            property_components.append(column.data_type)

            if column.pk:
                property_components.append('PRIMARY KEY')

            if column.default_value is not None:
                property_components.append("DEFAULT %s" % DataFormatting.value_to_string(column, column.default_value, default_value=True))

            if column.unique:
                property_components.append('UNIQUE')

            if column.not_null:
                property_components.append('NOT NULL')

            if column.pk:
                sql_properties.insert(0, ' '.join(property_components))
            else:
                sql_properties.append(' '.join(property_components))

            if column.fk:
                sql_foreign_keys.append('FOREIGN KEY (%s) REFERENCES %s(%s)' % (column.property_name, column.fk_table.__table_name__, column.fk_property))

        sql.append(', \n'.join(sql_properties + sql_foreign_keys))
        sql.append(');')

        return ' \n'.join(sql)

    @classmethod
    def __drop_table__(cls) -> str:
        """Constructs the needed sql statements to drop a database table from a Table class"""

        return 'DROP TABLE IF EXISTS %s;' % cls.__table_name__

    @classmethod
    def __init_join_tables__(cls):

        for column in cls.get_schema_columns():

            if not column.fk:
                continue

            # todo : simplify the dict . . just the column is needed
            cls.__join_table_definitions__[column.fk_table.__name__] = {'table_class': column.fk_table,
                                                                        'fk': column.fk_property,
                                                                        'property': column.property_name,
                                                                        'column': column}

    @classmethod
    def table_schema_validation(cls) -> Tuple:
        """ Validates a table class for errors. Returns a tuple of the format Tuple[bool, List[str]] """

        no_errors_found: bool = True
        instance: Table.__subclasses__ = None
        errors: List = [no_errors_found, list()]

        try:
            instance = cls()
        except AttributeError as e:
            msg = 'Class level attribute of wrong type encountered. Column expected: %s' % str(e)
            logging.critical(msg)
            errors[1].append(msg)
            no_errors_found = False

        if instance:

            column_names = (list(instance.get_class_column_names()))
            instance_att_names = list(instance.get_instance_attribute_names())

            for column_name in column_names:
                attrib = getattr(cls, column_name)

                if not str(type(attrib)).endswith(".Column'>"):
                    msg = 'Class members not named __member_name__ must be of type -> Column: %s Type: %s' % (column_name, type(attrib))
                    logging.critical(msg)
                    errors[1].append(msg)
                    no_errors_found = False

            if column_names != instance_att_names:
                unexpected_attributes = list(set(instance_att_names) - set(column_names))
                missing_attributes = list(set(column_names) - set(instance_att_names))

                if unexpected_attributes:
                    msg = 'Unexpected instance attributes: %s' % str(unexpected_attributes)
                    logging.critical(msg)
                    errors[1].append(msg)
                    no_errors_found = False

                if missing_attributes:
                    msg = 'Missing instance attributes: %s' % str(missing_attributes)
                    logging.critical(msg)
                    errors[1].append(msg)
                    no_errors_found = False

        errors[0] = no_errors_found

        return tuple(errors)

    @staticmethod
    def read_blob_file(data):
        return sqlite.Binary(data.read())

    @staticmethod
    def md5_file_object(file_object) -> str:
        md5 = hashlib.md5(file_object.read()).hexdigest()
        file_object.seek(0)
        return md5

    def __init__(self):
        pass

    def __getitem__(self, item):
        return getattr(self, item)

    def __repr__(self) -> str:
        repr_string = '%s { %s }' % (self.__table_name__, ", ".join(["%s : %s" % (a, b) for a, b in zip(list(self.get_class_column_names()), list(self.get_values()))]))
        return repr_string

    @property
    def table_name(self) -> str:
        return self.__table_name__

    def finalize_init(self):
        self.__init_join_tables__()
        self.__setup_default_value__()

    def __setup_default_value__(self):
        for column in self.get_schema_columns():

            if column.default_value is None:
                continue

            try:
                if getattr(self, column.property_name):
                    continue
            except TypeError:
                continue

            setattr(self, column.property_name, column.default_value)

    def get_column_display_names(self) -> List[str]:
        """ Returns the display names of each column if they exist. Fallback is attribute name """

        display_names = list()

        for attrib in self.get_class_column_names():
            display_name = getattr(self.__class__, attrib).display_name

            if not display_name:
                display_name = attrib

            display_names.append(display_name)

        return display_names

    def get_instance_attribute_names(self) -> Generator[str, None, None]:
        """ returns instance level attribute names (excluding privates and callables) """

        return (attr for attr, value in self.__dict__.items() if not callable(getattr(self, attr)) and not attr.startswith("__"))

    def add_table_to_join_table_dict(self, key, value) -> None:

        self.__join_tables__[key] = value

    def fetch_join_tables(self, db_object: 'Database') -> None:

        [self.add_table_to_join_table_dict(join_table_name, self.select_reference_record(db_object, join_table_name)) for join_table_name in self.__join_table_definitions__.keys()]

    def select_reference_record_all(self, db_object: 'Database') -> List['Table']:
        """ returning table objects for all join tables """

        return [self.select_reference_record(db_object, join_table_name) for join_table_name in self.__join_table_definitions__.keys()]

    def select_reference_record(self, db_object: 'Database', join_table_name: str) -> 'Table':
        """ returning table object for a specific join tables """

        fk_table_info = self.__join_table_definitions__.get(join_table_name)

        if fk_table_info is None:
            return

        value = getattr(self, fk_table_info.get('property'))
        column = fk_table_info.get('column')

        if value is None:
            return

        condition = '%s=%s' % (fk_table_info.get('fk'), DataFormatting.value_to_string(column, value))

        return db_object.select_record(fk_table_info.get('table_class'), condition)

    def default_update_condition(self) -> str:
        """ Returning sql definition of default update condition """

        return 'id = %s' % self.id

    def from_sql_record(self, sql_row: List) -> None:
        """ Sets the record values from a sql record of type list """

        for column_name, value in zip(self.get_class_column_names(), sql_row):
            setattr(self, column_name, value)

    def get_values(self) -> Generator:
        """ Returns a generator for all the values """

        return (getattr(self, column_name) for column_name in self.get_class_column_names())

    def get_value_by_index(self, index: int):
        """ Gets the value of the nth attribute """

        try:
            return getattr(self, list(self.get_class_column_names())[index])
        except:
            return False

    def set_value_by_index(self, index: int, value):
        """ Sets the value of the nth attribute """

        try:
            attrib = list(self.get_class_column_names())[index]
            setattr(self, attrib, value)
            return True
        except:
            return False

    def reset_to_default(self) -> None:
        """ Resets the values of the instance to the defined default values of each Column """

        for column_name, column in zip(self.get_class_column_names(), self.get_schema_columns()):
            setattr(self, column_name, column.default_value)

    def from_json(self, json_string: str) -> None:
        """ Sets the record values from a json string """

        json_object = json.loads(json_string)

        for column_name, column in zip(self.get_class_column_names(), self.get_schema_columns()):
            setattr(self, column_name, json_object.get(column_name, column.default_value))

    def to_json(self) -> str:
        """ Returns a json string containing the table name, column names and values """

        json_data = dict()

        json_data["table_name"] = self.__table_name__
        json_data["headers"] = list(self.get_class_column_names())

        for prop in self.get_schema_columns():
            json_data[prop.property_name] = getattr(self, prop.property_name)

        return json.dumps(json_data)




