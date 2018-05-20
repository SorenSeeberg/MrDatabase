#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
import time
import uuid

from database.column import Column


class DataFormatting:

    @staticmethod
    def display_date(seconds) -> str:
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                  'November', 'December']

        date_comps = str(datetime.date.fromtimestamp(float(seconds) / 1000)).split('-')

        day = date_comps[2]

        if day.startswith('0') and len(day) > 1:
            day = day[1:]

        return '%s %s. %s' % (months[int(date_comps[1]) - 1], day, date_comps[0])

    @staticmethod
    def current_time() -> str:
        return str(int(time.time())) + '000'

    @staticmethod
    def new_guid() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def value_to_string(column_object, value, default=False):

        if default:
            value = column_object.default

        if column_object.data_type.startswith('CHAR') or column_object.data_type.startswith(
                'VARCHAR') or column_object.data_type == Column.data_types.datetime:
            return f"'{value}'"
        else:
            return f'{value}'
