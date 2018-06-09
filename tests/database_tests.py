#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
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


def test_database_creation():

    if os.path.isfile(DB_PATH):
        os.remove(DB_PATH)

    db = MrDatabase(DB_PATH)
    db.create_table(City)
    db.drop_table(City)

    assert (type(db) == MrDatabase)


def test_create_table():

    db = MrDatabase(DB_PATH)
    db.drop_table(City)
    success = db.create_table(City)

    assert (success is True)


def test_drop_table():

    db = MrDatabase(DB_PATH)
    db.drop_table(City)
    db.create_table(City)
    success = db.drop_table(City)

    assert (success is True)


def test_table_not_exists():

    db = MrDatabase(DB_PATH)
    table_exists = db.table_exists(City)

    assert (table_exists is False)


def test_table_exists():

    db = MrDatabase(DB_PATH)
    db.create_table(City)
    table_exists = db.table_exists(City)

    assert (table_exists is True)


def test_insert_row():

    db = MrDatabase(DB_PATH)
    db.create_table(City)
    city1 = City()
    db.insert_record(city1)

    city2 = db.select_records(City)

    assert (city2[0].id == 1)


def test_delete_row():

    db = MrDatabase(DB_PATH)
    db.drop_table(City)
    db.create_table(City)

    db.insert_record(City())

    id_condition = 'id=1'

    city_record = db.select_record(City, id_condition)
    record_deleted = False

    if city_record.id == 1:
        db.delete_record(city_record)

        city_record = db.select_record(City, id_condition)

        if not city_record:
            record_deleted = True

    assert(record_deleted is True)


def test_batch_insert_records():
    db = MrDatabase(DB_PATH)

    db.drop_table(City)
    db.create_table(City)
    city_1 = City()

    with DatabaseConnection(db, con_type=ConType.batch):
        for clone_number in range(1000):
            new_city = city_1.clone()
            new_city.cityName += f'_{clone_number}'
            db.insert_record(new_city)

    last_clone = db.select_records(City).last()

    assert(last_clone.id == 1000)


def test_batch_update_records():
    db = MrDatabase(DB_PATH)

    db.drop_table(City)
    db.create_table(City)
    city_1 = City()

    with DatabaseConnection(db, con_type=ConType.batch):
        for clone_number in range(1000):
            new_city = city_1.clone()
            new_city.cityName += f'_{clone_number}'
            db.insert_record(new_city)

    cities = db.select_records(City)

    with DatabaseConnection(db, con_type=ConType.batch):
        for city_record in cities:

            city_record.cityName = f'New {city_record.cityName}'
            db.update_record(city_record)

    city_record = db.select_record(City, 'id=1000')

    assert(city_record.cityName == 'New New York_999')


def test_clone_record():
    city = City()
    city_clone = city.clone()

    assert(id(city) != id(city_clone))


def test_join_table():
    db = MrDatabase(DB_PATH)

    db.drop_table(City)
    db.drop_table(Person)
    db.create_table(City)
    db.create_table(Person)

    city = City()
    db.insert_record(city)

    person = Person()
    person.cityId = city.id

    db.insert_record(person)

    person_record = db.select_record(Person, 'id=1')
    city_record = person_record.select_join_record(db, City.get_table_name())

    assert(city_record.id == 1)


if __name__ == '__main__':
    test_join_table()

