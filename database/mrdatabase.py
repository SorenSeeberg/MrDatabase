#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import List, Any, Tuple

import logging
import sqlite3 as sqlite

from database.databaseconnection import DatabaseConnection, ConType
from database.table import Table
from database.records import Records

# from flask import Markup
VERSION = '0.9.5 Alpha'


class LogLevel:

    debug = logging.DEBUG
    info = logging.INFO
    warning = logging.WARNING
    error = logging.ERROR
    critical = logging.CRITICAL


class MrDatabase:

    @classmethod
    def logging(cls, filename: str='mr_database.log', level: LogLevel=LogLevel.warning, filemode: str= 'w'):

        log_format: str = '%(levelname)s %(asctime)s - %(message)s'
        logging.basicConfig(filename=filename, level=level, filemode=filemode, format=log_format)

    @staticmethod
    def version() -> str:

        return VERSION

    def __init__(self, database_path: str):
        self.con: sqlite.connect = None
        self.cur: sqlite.Cursor = None
        self.database_path = database_path

    def create_table(self, table_class: Table.__subclasses__, con_type=ConType.query):

        with DatabaseConnection(self, con_type=con_type):
            sql = table_class.__create_table__()
            logging.info(sql)
            self.cur.execute(sql)

    def drop_table(self, table_class: Table.__subclasses__, con_type=ConType.query):

        with DatabaseConnection(self, con_type=con_type):
            sql = table_class.__drop_table__()
            logging.info(sql)
            self.cur.execute(sql)

    # @staticmethod
    # def html_markup(record_object):
    #
    #     record_object.html.val = Markup(record_object.html.val)

    def fetchone(self, sql: str) -> Tuple:

        with DatabaseConnection(self, con_type=ConType.query):
            self.cur.execute(sql)

            return self.cur.fetchone()

    def fetchall(self, sql: str) -> List[Tuple]:

        with DatabaseConnection(self, con_type=ConType.query):
            self.cur.execute(sql)

            return self.cur.fetchall()

    def __mutate__(self, sql: str, value_list: List[Any]=None) -> None:

        with DatabaseConnection(self, con_type=ConType.mutation):

            if value_list:
                self.cur.execute(sql, value_list)
            else:
                self.cur.execute(sql)

    def sub_transaction(self, sql: str, value_list: List[Any]=None) -> None:
        """
        Executing sql without a connection. The connection must come
        from elsewhere. This allows for transaction-like sql execution
        """

        if value_list:
            self.cur.execute(sql, value_list)
        else:
            self.cur.execute(sql)

    def delete_record(self, record_object: Table.__subclasses__, condition: str=None) -> str:
        """Constructing the sql for deleting a record"""

        if condition is None:
            condition = record_object.default_update_condition()

        sql = f'DELETE FROM {record_object.get_table_name()} WHERE {condition};'

        logging.info(f'DELETE RECORD: {sql}')

        self.__mutate__(sql)

        return sql

    def update_record(self, record_object: Table.__subclasses__, condition: str=None) -> str:
        """Constructing the sql for updating a record"""

        if condition is None:
            condition = record_object.default_update_condition()

        table_name = record_object.get_table_name()
        attributes = record_object.get_column_names_cls()
        values = list(record_object.get_values())
        update = ", ".join(f'{attrib}=?' for attrib in attributes)

        condition_params = condition.split('=')
        condition_string = "%s=?" % condition_params[0].strip()
        value_list = values + [int(condition_params[1].strip())]

        sql = f'UPDATE {table_name} SET {update} WHERE {condition_string};'

        logging.info(f'UPDATE RECORD: {sql} {value_list}')

        self.__mutate__(sql, value_list)

        return sql

    def insert_record(self, record_object: Table.__subclasses__) -> str:
        """Constructing the sql for inserting a record"""

        table_name = record_object.get_table_name()
        attributes = list(record_object.get_column_names_cls())
        values = list(record_object.get_values())

        values_string = ", ".join(len(attributes) * ['?'])
        attributes_string = ", ".join((str(attribute) for attribute in attributes))

        sql = f'INSERT INTO {table_name}({attributes_string}) VALUES ({values_string});'

        logging.info(f'INSERT RECORD: {sql} {values}')

        self.__mutate__(sql, list(values))

        return sql

    def select_record(self, table_class: Table.__subclasses__, condition: str) -> Table.__subclasses__:
        """Constructing the sql for selecting a record"""

        sql = f'SELECT * FROM {table_class.get_table_name()} WHERE {condition};'

        record = self.fetchone(sql)

        logging.info(f'GET RECORD: {sql}')

        if record:
            data_type_instance = table_class()
            data_type_instance.from_sql_record(record)

            return data_type_instance

    def select_records(self, table_class: Table.__subclasses__, condition: str=None, order_by: List[str]=None, order_asc: bool=True, limit: int=0) -> Records:

        sql_comps = list()

        sql_comps.append(f'SELECT * FROM {table_class.get_table_name()}')

        if condition is not None:
            sql_comps.append(f'WHERE {condition}')

        if order_by is not None:
            if order_asc:
                order = 'ASC'
            else:
                order = 'DESC'

            order_by = ', '.join(order_by)

            logging.info(order_by)
            logging.info(order)

            sql_comps.append(f'ORDER BY {order_by} {order}')

        if limit > 0:
            sql_comps.append(f'LIMIT {limit}')

        sql_comps.append(';')

        sql = ' '.join(sql_comps)

        logging.info(f'GET RECORDS: {sql}')

        records = self.fetchall(sql)

        def create_data_type(data_type, record):
            data_type_instance = data_type()
            data_type_instance.from_sql_record(record)

            return data_type_instance

        records: Records = Records([create_data_type(table_class, record) for record in records])

        return records

    def increment_id(self, table_name: str, column_name: str= 'id') -> int:

        try:
            with DatabaseConnection(self, con_type=ConType.query):
                self.cur.execute(f'SELECT MAX({column_name}) FROM {table_name};')
                current_highest_id = int(self.cur.fetchone()[0])
                return current_highest_id + 1
        except:
            return 0


