#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from database.mrdatabase import MrDatabase
from database.mrdatabase import LogLevel
from database.mrdatabase import database_connection

""" import of table classes """
from table_schema_examples import City
from table_schema_examples import Person
from table_schema_examples import BrokenTable

mr_database = MrDatabase(os.path.abspath(os.path.join(__file__, os.pardir)), 'test_functionality.db')


def class_level_inheritance_testing():

    print(City())
    print(list(City.get_class_column_names()))
    print(Person())
    print(list(Person.get_class_column_names()))


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
    mr_database.drop_table(City)
    print('Dropping table: %s' % City.__name__)
    mr_database.drop_table(Person)
    print('Dropping table: %s' % Person.__name__)

    # create tables
    print('\nCreating Tables\n------------------------------------------')
    mr_database.create_table(City)
    print('Creating table: %s' % City.__name__)
    mr_database.create_table(Person)
    print('Creating table: %s' % Person.__name__)

    # Creation and insertion of records
    # If you use .get_next_id(), remember to insert your record before using it again.
    # Alternatively you can increment manually
    print('\nCreation and Insertion of Records\n------------------------------------------')
    city_1 = City(id=mr_database.get_next_id("City", "id"), postal_code=8300, city_name='Odder')
    print('City_1: %s' % city_1)
    person_1 = Person(id=mr_database.get_next_id("Person", "id"), firstName='Albert', lastName='Einstein', cityId=city_1.id)
    print('Person_1: %s' % person_1)
    mr_database.insert_record(city_1)
    mr_database.insert_record(person_1)

    city_2 = City(id=mr_database.get_next_id("City", "id"), postal_code=8660, city_name='Skanderborg')
    mr_database.insert_record(city_2)
    person_2 = Person(id=mr_database.get_next_id("Person", "id"), firstName='Niels', lastName='Bohr', cityId=city_2.id)

    # Changing cityName to boston and updating the record
    city_2.cityName = 'Boston'
    mr_database.update_record(city_2)

    # Creating a new city record. Using the from_json and to_json methods to transport the
    # properties of city2 to city_json. Then we update some of the fields and insert the record
    city_json = City()
    city_json.from_json(city_2.to_json())
    city_json.id = mr_database.get_next_id("City", "id")
    city_json.cityName = 'Frederiksberg'
    mr_database.insert_record(city_json)

    # selecting the newly inserted record
    city3: City = mr_database.select_record(City, condition='cityName="Frederiksberg"')
    print('City Name: %s' % city3.cityName)

    # selecting and printing all cities
    all_cities = mr_database.select_records(City)
    print('\nAll Cities\n------------------------------------------')
    for city_1 in all_cities:
        print(city_1)

    # Deleting city3
    mr_database.delete_record(city3)

    print('\nDefault Values of City()\n------------------------------------------')
    city3.reset_to_default()
    print(city3)

    print('\nReferenced City record from person_1\n------------------------------------------')
    referenced_record = person_1.select_reference_record(mr_database, 'City')
    print(referenced_record)

    referenced_records = person_2.select_reference_record_all(mr_database)

    print('\n------------------------\nAll Tests Complete')
