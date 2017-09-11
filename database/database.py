#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import List, Any, Tuple

import os
import logging
import sqlite3 as sqlite

from database.table import Table
from database.records import Records

# from flask import Markup


class LogLevel:

    debug = logging.DEBUG
    info = logging.INFO
    warning = logging.WARNING
    error = logging.ERROR
    critical = logging.CRITICAL


class Database:

    @classmethod
    def logging(cls, filename: str='mr_database.log', level: LogLevel=LogLevel.warning, filemode: str= 'w'):

        log_format: str = '%(levelname)s %(asctime)s - %(message)s'
        logging.basicConfig(filename=filename, level=level, filemode=filemode, format=log_format)

    def __init__(self, database_path: str, database_name: str):
        self.con: sqlite.connect = None
        self.cur: sqlite.Cursor = None
        self.database_path: str = os.path.join(database_path, database_name)

    def create_table(self, table_class: Table.__subclasses__, commit=True):

        with database_connection(self, commit=commit):
            sql = table_class.__create_table__()
            logging.info(sql)
            self.cur.execute(sql)

    def drop_table(self, table_class: Table.__subclasses__, commit=True):

        with database_connection(self, commit=commit):
            sql = table_class.__drop_table__()
            logging.info(sql)
            self.cur.execute(sql)

    # @staticmethod
    # def html_markup(record_object):
    #
    #     record_object.html.val = Markup(record_object.html.val)

    def fetchone(self, sql: str) -> Tuple:

        with database_connection(self):
            self.cur.execute(sql)

            return self.cur.fetchone()

    def fetchall(self, sql: str) -> List[Tuple]:

        with database_connection(self):
            self.cur.execute(sql)

            return self.cur.fetchall()

    def __insert_record__(self, sql: str, value_list: List[Any]):

        with database_connection(self, commit=True):
            self.cur.execute(sql, value_list)

    def __update_record__(self, sql: str, value_list: List[Any]):

        with database_connection(self, commit=True):
            self.cur.execute(sql, value_list)

    def __delete_record__(self, sql: str) -> None:

        with database_connection(self, commit=True):
            self.cur.execute(sql)

    def sub_transaction(self, sql: str, value_list: List[Any]=None) -> None:
        """Executing sql without a connection. The connection must come
        from elsewhere. This allows for transaction-like sql execution
        """

        if value_list:
            self.cur.execute(sql, value_list)
        else:
            self.cur.execute(sql)

    def execute_script(self, sql_command_list: List[str], commit=True) -> None:

        sql_script = '\n'.join(sql_command_list)

        if commit:

            with database_connection(self):
                self.cur.executescript(sql_script)

        else:

            self.cur.executescript(sql_script)

    def delete_record(self, record_object: Table.__subclasses__, condition: str=None, commit: bool=True) -> str:
        """Constructing the sql for deleting a record"""

        if condition is None:
            condition = record_object.default_update_condition()

        sql = "DELETE FROM %s WHERE %s;" % (record_object.__table_name__, condition)

        logging.info("DELETE RECORD: %s" % sql)

        if commit:
            self.__delete_record__(sql)

        return sql

    def update_record(self, record_object: Table.__subclasses__, condition: str=None, commit: bool=True) -> str:
        """Constructing the sql for updating a record"""

        if condition is None:
            condition = record_object.default_update_condition()

        table_name = record_object.__table_name__
        attributes = record_object.get_class_column_names()
        values = list(record_object.get_values())
        update = ", ".join("%s=?" % attrib for attrib in attributes)

        condition_params = condition.split('=')
        condition_string = "%s=?" % condition_params[0].strip()
        value_list = values + [int(condition_params[1].strip())]

        sql = "UPDATE %s SET %s WHERE %s;" % (table_name, update, condition_string)

        logging.info("UPDATE RECORD: %s %s" % (sql, value_list))

        if commit:
            self.__update_record__(sql, value_list)

        return sql

    def insert_record(self, record_object: Table.__subclasses__, commit: bool=True) -> str:
        """Constructing the sql for inserting a record"""

        table_name = record_object.__table_name__
        attributes = list(record_object.get_class_column_names())
        values = list(record_object.get_values())

        values_string = ", ".join(len(attributes) * ['?'])
        attributes_string = ", ".join((str(attribute) for attribute in attributes))

        sql = "INSERT INTO %s(%s) VALUES (%s);" % (table_name, attributes_string, values_string)

        logging.info("INSERT RECORD: %s %s" % (sql, values))

        if commit:
            self.__insert_record__(sql, list(values))
        else:
            self.cur.execute(sql, list(values))

        return sql

    def select_record(self, table_class: Table.__subclasses__, condition: str) -> Table:
        """Constructing the sql for selecting a record"""

        sql = "SELECT * FROM %s WHERE %s;" % (table_class.__table_name__, condition)

        record = self.fetchone(sql)

        logging.info("GET RECORD: %s" % sql)

        if record:
            data_type_instance = table_class()
            data_type_instance.from_sql_record(record)

            return data_type_instance

    def select_records(self, table_class: Table.__subclasses__, condition: str=None, order_by: List[str]=None, order_asc: bool=True, limit: int=0) -> Records:

        sql_comps = list()

        sql_comps.append("SELECT * FROM %s" % table_class.__table_name__)

        if condition is not None:
            sql_comps.append("WHERE %s" % condition)

        if order_by is not None:
            if order_asc:
                order = 'ASC'
            else:
                order = 'DESC'

            order_by = ', '.join(order_by)

            logging.info(order_by)
            logging.info(order)

            sql_comps.append('ORDER BY %s %s' % (order_by, order))

        if limit > 0:
            sql_comps.append('LIMIT %s' % limit)

        sql_comps.append(';')

        sql = ' '.join(sql_comps)

        logging.info("GET RECORDS: %s" % sql)

        records = self.fetchall(sql)

        def create_data_type(data_type, record):
            data_type_instance = data_type()
            data_type_instance.from_sql_record(record)

            return data_type_instance

        return Records([create_data_type(table_class, record) for record in records])

    def get_next_id(self, table_name: str, column_name: str='id') -> int:

        try:
            with database_connection(self, commit=False):
                self.cur.execute("SELECT MAX(%s) FROM %s;" % (column_name, table_name))
                current_highest_id = int(self.cur.fetchone()[0])
                return current_highest_id + 1
        except:
            return 0


class database_connection:

    def __init__(self, database_object: Database, commit: bool=True):

        self.database_object = database_object
        self.commit = commit

    def __enter__(self):
        self.database_object.con = sqlite.connect(self.database_object.database_path)
        self.database_object.cur = self.database_object.con.cursor()

    def __exit__(self, *args):
        if self.commit:
            self.database_object.con.commit()

        self.database_object.con.close()
        self.database_object.con = None
        self.database_object.cur = None

