import os
from mr_database import MrDatabase
from table_schema_examples import City

DB_PATH = 'test_database.db'


def test_database_creation():

    if os.path.isfile(DB_PATH):
        os.remove(DB_PATH)

    db = MrDatabase(DB_PATH)
    db.create_table(City)
    db.drop_table(City)

    assert (type(db) == MrDatabase)


def test_table_not_exists():

    db = MrDatabase(DB_PATH)
    table_exists = db.table_exists(City)

    assert (table_exists is False)


def test_table_exists():

    db = MrDatabase(DB_PATH)
    db.create_table(City)
    table_exists = db.table_exists(City)

    assert (table_exists is True)


def test_drop_table():

    db = MrDatabase(DB_PATH)
    db.drop_table(City)
    table_exists = db.table_exists(City)

    assert (table_exists is False)


def test_insert_row():

    db = MrDatabase(DB_PATH)
    db.create_table(City)
    city1 = City()
    db.insert_record(city1)

    city2 = db.select_records(City)

    assert (city2[0].id == 1)


if __name__ == '__main__':
    test_database_creation()
    test_table_not_exists()
    test_table_exists()
    test_drop_table()
    test_insert_row()
