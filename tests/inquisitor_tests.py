#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from mr_database import Inquisitor as IQ
from mr_database import MrDatabase
from mr_database import DatabaseConnection
from mr_database import ConType
from mr_database import Table
from mr_database import Column
from mr_database import DataTypes

DB_PATH = 'test_database.db'


class City(Table):
    id = Column(DataTypes.integer, pk=True)
    postalCode = Column(DataTypes.smallint, default=9999, display_name='Postal Code')
    cityName = Column(DataTypes.varchar(40), default='New York', display_name='City Name')


class Person(Table):
    id = Column(DataTypes.integer, pk=True)
    firstName = Column(DataTypes.varchar(40))
    lastName = Column(DataTypes.varchar(40))
    cityId = Column(data_type=DataTypes.integer, fk=(City, 'id'), default=0)


if __name__ == '__main__':
    query1 = IQ().SELECT(['id', 'name']).FROM('Person').WHERE().expression('id > 10').AND().LIKE('name', 'john')
    query2 = IQ().SELECT(['id', 'name']).FROM(Person).INNER_JOIN(Person, 'cityId', City, 'id')
    query3 = IQ().SELECT(['id', 'name']).FROM(Person).ORDER(IQ.ASC('id'), IQ.DESC('name'))
    query4 = IQ().SELECT(['id', 'name']).FROM(Person).WHERE().LIKE('name', '%%\njo\\_n. --')

    # print(query1)
    # print(query2)
    # print(query3)
    print(query4)
