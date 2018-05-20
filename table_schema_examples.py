#!/usr/bin/python3
# -*- coding: utf-8 -*-

from database.column import *
from database.table import *


class TableTemplate(Table):

    id = Column('id', DataTypes.integer, pk=True)
    myCol = Column('myCol', DataTypes.varchar(16), default='Hello World')


class BrokenTable(Table):

    id = Column('id', DataTypes.integer, pk=True)
    postalCode = Column('postalCode', DataTypes.smallint)
    cityName = Column('cityName', DataTypes.varchar(40), not_null=True, default='New York')
    cityId = Column('cityId', data_type=DataTypes.integer, default=0)

    def __init__(self):
        super().__init__()

        self.counter = 10


class City(Table):

    id = Column('id', DataTypes.integer, pk=True)
    postalCode = Column('postalCode', DataTypes.smallint, default=9999, display_name='Postal Code')
    cityName = Column('cityName', DataTypes.varchar(40), default='New York', display_name='City Name')


class Person(Table):

    id = Column('id', DataTypes.integer, pk=True)
    firstName = Column('firstName', DataTypes.varchar(40))
    lastName = Column('lastName', DataTypes.varchar(40))
    cityId = Column('cityId', data_type=DataTypes.integer, fk=(City, City.id), default=0)


class Image(Table):

    id = Column('id', DataTypes.integer, pk=True)
    md5 = Column('md5', DataTypes.char(32))
    imageName = Column('imageName', DataTypes.varchar(40))
    imageData = Column('imageData', DataTypes.blob)
