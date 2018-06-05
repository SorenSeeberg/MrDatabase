#!/usr/bin/python3
# -*- coding: utf-8 -*-

from mr_database import DataTypes
from mr_database import Table
from mr_database import Column


class TableTemplate(Table):

    id = Column(DataTypes.integer, pk=True)
    myCol = Column(DataTypes.varchar(16), default='Hello World')


class BrokenTable(Table):

    id = Column(DataTypes.integer, pk=True)
    postalCode = Column(DataTypes.smallint)
    cityName = Column(DataTypes.varchar(40), not_null=True, default='New York')
    cityId = Column(data_type=DataTypes.integer, default=0)

    def __init__(self):
        super().__init__()

        self.counter = 10


class City(Table):

    id = Column(DataTypes.integer, pk=True)
    postalCode = Column(DataTypes.smallint, default=9999, display_name='Postal Code')
    cityName = Column(DataTypes.varchar(40), default='New York', display_name='City Name')

    def __init__(self):
        super().__init__()

        self.id: int = City.id.default
        self.postalCode: int = City.postalCode.default
        self.cityName: str = City.cityName.default


class Person(Table):

    id = Column(DataTypes.integer, pk=True)
    firstName = Column(DataTypes.varchar(40))
    lastName = Column(DataTypes.varchar(40))
    cityId = Column(data_type=DataTypes.integer, fk=(City, 'id'), default=0)


class Image(Table):

    id = Column(DataTypes.integer, pk=True)
    md5 = Column(DataTypes.char(32))
    imageName = Column(DataTypes.varchar(40))
    imageData = Column(DataTypes.blob)
