#!/usr/bin/python3
# -*- coding: utf-8 -*-

from database.column import *
from database.table import *


class TableTemplate(Table):

    __table_name__ = 'TableTemplate'

    id = Column('id', DataTypes.integer, pk=True)
    myCol = Column('myCol', DataTypes.varchar(16), default_value='Hello World')

    def __init__(self, id=None, myCol=None):
        super().__init__()

        self.id = id
        self.myCol = myCol

        self.finalize_init()


class BrokenTable(Table):

    __table_name__ = 'BrokenTable'

    id = Column('id', DataTypes.integer, pk=True)
    postalCode = Column('postalCode', DataTypes.smallint)
    cityName = Column('cityName', DataTypes.varchar(40), not_null=True, default_value='New York')
    cityId = Column('cityId', data_type=DataTypes.integer, default_value=0)

    def __init__(self, id=None, postal_code=None, city_name=None):
        super().__init__()

        self.id = id
        self.postalCode = postal_code
        self.cityName = city_name

        self.counter = 10

        self.finalize_init()


class City(Table):

    __table_name__ = 'City'

    id = Column('id', DataTypes.integer, pk=True)
    postalCode = Column('postalCode', DataTypes.smallint, default_value=9999, display_name='Postal Code')
    cityName = Column('cityName', DataTypes.varchar(40), default_value='New York', display_name='City Name')

    def __init__(self, id=None, postal_code=None, city_name=None):
        super().__init__()

        self.id = id
        self.postalCode = postal_code
        self.cityName = city_name

        self.finalize_init()


class Person(Table):

    __table_name__ = 'Person'

    id = Column('id', DataTypes.integer, pk=True)
    firstName = Column('firstName', DataTypes.varchar(40))
    lastName = Column('lastName', DataTypes.varchar(40))
    cityId = Column('cityId', data_type=DataTypes.integer, fk=(City, City.id), default_value=0)

    def __init__(self, id=None, firstName=None, lastName=None, cityId=None):
        super().__init__()

        self.id = id
        self.firstName = firstName
        self.lastName = lastName
        self.cityId = cityId

        self.finalize_init()


class Image(Table):

    __table_name__ = 'Image'

    id = Column('id', DataTypes.integer, pk=True)
    md5 = Column('md5', DataTypes.char(32))
    imageName = Column('imageName', DataTypes.varchar(40))
    imageData = Column('imageData', DataTypes.blob)

    def __init__(self, id=None, md5=None, imageName=None, imageData=None):
        super().__init__()

        self.id = id
        self.md5 = md5
        self.imageName = imageName
        self.imageData = imageData

        self.finalize_init()
