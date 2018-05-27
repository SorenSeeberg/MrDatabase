#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

from mr_database import MrDatabase
from mr_database import LogLevel
from mr_database import DatabaseConnection, ConType

""" import of table classes """
from table_schema_examples import City
from table_schema_examples import Person
from table_schema_examples import BrokenTable


db = MrDatabase(os.path.join(os.path.abspath(os.path.join(__file__, os.pardir)), 'test_functionality.db'))
# db = MrDatabase(':memory:')


def class_level_inheritance_testing():

    print(City())
    print(list(City.get_column_names_cls()))
    print(Person())
    print(list(Person.get_column_names_cls()))


if __name__ == '__main__':
    # enables logging at 'DEBUG' level
    MrDatabase.logging(level=LogLevel.error)

    # Validating a table class for errors
    print('\nValidating BrokenTable\n------------------------------------------')
    validation_result = BrokenTable.table_schema_validation()
    if validation_result[0] is False:
        print("Errors found in BrokenTable")
        for error in validation_result[1]:
            print(error)

    # drop existing tables if exists
    print('\nDropping Tables\n------------------------------------------')
    db.drop_table(City)
    print('Dropping table: %s' % City.__name__)
    db.drop_table(Person)
    print('Dropping table: %s' % Person.__name__)

    # create tables
    print('\nCreating Tables\n------------------------------------------')
    db.create_table(City)
    print('Creating table: %s' % City.__name__)
    db.create_table(Person)
    print('Creating table: %s' % Person.__name__)

    # Creation and insertion of records
    # If you use .get_next_id(), remember to insert your record before using it again.
    # Alternatively you can increment manually
    print('\nCreation and Insertion of Records\n------------------------------------------')

    city_1 = City()
    city_1.id = db.increment_id("City", "id")
    city_1.postal_code = 8300
    city_1.city_name = 'Odder'

    print('City_1: %s' % city_1)
    person_1 = Person()
    person_1.id = db.increment_id("Person", "id")
    person_1.firstName = 'Albert'
    person_1.lastName = 'Einstein'
    person_1.cityId = city_1.id

    print('Person_1: %s' % person_1)
    db.insert_record(city_1)
    db.insert_record(person_1)

    city_2 = City()
    city_2.id = db.increment_id("City", "id")
    city_2.postal_code = 8660
    city_2.city_name = 'Skanderborg'

    db.insert_record(city_2)
    person_2 = Person()
    person_2.id = db.increment_id("Person", "id")
    person_2.firstName = 'Niels'
    person_2.lastName = 'Bohr'
    person_2.cityId = city_2.id
    db.insert_record(person_2)

    # Changing cityName to boston and updating the record
    city_2.cityName = 'Boston'
    db.update_record(city_2)

    # Creating a new city record. Using the from_json and to_json methods to transport the
    # properties of city2 to city_json. Then we update some of the fields and insert the record
    city_json = City()
    city_json.from_json(city_2.to_json())
    city_json.id = db.increment_id("City", "id")
    city_json.cityName = 'Frederiksberg'
    db.insert_record(city_json)

    # selecting the newly inserted record
    city3: City = db.select_record(City, condition='cityName="Frederiksberg"')
    print('City Name: %s' % city3.cityName)

    # selecting and printing all cities
    all_cities = db.select_records(City)
    print('\nAll Cities\n------------------------------------------')
    for city_1 in all_cities:
        print(city_1)

    # Deleting city3
    db.delete_record(city3)

    print('\nDefault Values of City()\n------------------------------------------')
    city3.reset_to_default()
    print(city3)

    print('\nReferenced City record from person_1\n------------------------------------------')
    referenced_record = person_1.select_reference_record(db, 'City')
    print(referenced_record)

    referenced_records = person_2.select_reference_record_all(db)

    print('\nInserting 10K clones of person_1\n------------------------------------------')

    next_id = db.increment_id('Person')

    with DatabaseConnection(db, con_type=ConType.batch):
        for person_id in range(next_id, next_id + 10000):
            new_person = person_1.clone()
            new_person.id = person_id
            new_person.firstName += f'_{person_id}'
            db.insert_record(new_person)

    for person in db.select_records(Person, 'id < 10'):
        print(person)

    print('\n------------------------\nAll Tests Complete')
