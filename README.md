# MrDatabase v. 0.9.10
Databasing as easy as it gets! An ORM on top of SQLite3

## Simple Code Examples

### Installation

`pip install mrdatabase`

### Create a Database

When creating an instance of MrDatabase, it will check if the path points to an existing sqlite .db file. If it does not, it will create it.

```python
from mr_database import MrDatabase

db = MrDatabase('some/path/my.db')
```

Most connecting and disconnecting actions with the database is handled by the internals of MrDatabase.

### Tables (DDL)

Creating a new table class is super easy. This class works both as schema and record factory. Simply create a class that inherits from ```Table```. Add fields as class variables. Each field must be an instance of ```Column```. Voilà, the table is ready!

```python
from mr_database import Column
from mr_database import Table
from mr_database import DataTypes

class City(Table):

    id = Column(DataTypes.integer, pk=True)
    postalCode = Column(DataTypes.smallint, default=9999)
    cityName = Column(DataTypes.varchar(40), default='New York')
```

With a table class in hand, creating or dropping a table in the database is as easy as shown below!

```python
db.create_table(City)
db.drop_table(City)
```

### Type Hinting

If you want Python 3 style type hints on your record intances, you will have to be a bit more verbose in how you define the table class.

You will have to make an `__init__` method, initialize the super class and add each of the attributes, with type hint and set the default value from the class level ```Column``` objects. It may sound complicated, but if you look below, it's quite doable. Type hinting can be extremely helpful. Especially if you use an editor like PyCharm.

```Python
class City(Table):

    id = Column(DataTypes.integer, pk=True)
    postalCode = Column(DataTypes.smallint, default=9999)
    cityName = Column(DataTypes.varchar(40), default='New York')

    def __init__(self):
        super().__init__()

        self.id: int = City.id.default
        self.postalCode: int = City.postalCode.default
        self.cityName: str = City.cityName.default
```

### Records (DML)
To insert, update or delete records in the database, you need record objects representing what you want to manipulate.

If you have setup an integer primary key on your table, the pimary key attribute will auto increment when inserting records. When you insert, the id of your record object will be updated with the assigned id.

You can create new record objects like the `city1` example, where you make an instance of a table class, or you can fetch existing ones from the database using `db.select_record` or `db.select_records`. Lastly you can call `.clone()` on the record you want to copy. This method returns a `copy.deepcopy` if the record in question.

```python
city1 = City()
city1.postal_code = 10115
city1.city_name = 'Berlin'

cities = db.select_records(City)                                # all cities
cities = db.select_records(City, condition='postalCode > 4000') # all cities with a postal code > 4000
a_city = db.select_record(City, condition='cityName="Berlin"')  # just Berlin

city2 = city1.clone()                                           # clone (copy.deepcopy)

db.insert_record(city1)
db.update_record(city1)
db.delete_record(city1)
```

### Batching
By default, mutating actions like `insert_record` and `update_record`, commit changes to the database one action at a time. This is very easy to work with, but for heavy work loads, this can be quite taxing on performance. If you need to execute many mutating actions you can batch actions together to dramatically improve performance.

To set it up, you use the `DatabaseConnection` context manager. You pass it the `db` object and set `con_type=ConType.batch`. All database actions called within the `DatabaseConnection` will use the database connection managed by `DatabaseConnection`.

```python
from mr_database import DatabaseConnection
from mr_database import ConType

with DatabaseConnection(db, con_type=ConType.batch):
    for clone_number in range(10000):
        new_person = person_1.clone()
        new_person.firstName += f'_{clone_number}'
        db.insert_record(new_person)
```

The example above inserts 10.000 clones of a `Person()` record. It takes less than 500 ms on a standard laptop ano 2017.

### Many to Many Relationships

As an example we have some images that can have some tags. This is a classic many to many relationship. To set it up you create the `Image` and the `Tag` table with no knowledge of or reference to eachother.

```Python
class Image(Table):
    id = Column(DataTypes.integer, pk=True)
    imageName = Column(DataTypes.varchar(40))
    sizeX = Column(DataTypes.integer)
    sizeY = Column(DataTypes.integer)


class Tag(Table):
    id = Column(DataTypes.integer, pk=True)
    tagName = Column(DataTypes.varchar(40))
```

Then you create a table, describing a relation between an image and a tag. I also like to give this table an id. Another way is to use the two foreign keys in combination as a `composite key`.

```Python
class ImageTag(Table):
    id = Column(DataTypes.integer, pk=True)
    imageId = Column(DataTypes.integer, fk=(Image, 'id'))
    tagId = Column(DataTypes.integer, fk=(Tag, 'id'))
```

When creating the tables in the database, remember to do it in the right order. `ImageTag` depends on `Image` and `Tag`, so you should create the junktion table last.

```Python
db.create_table(Image)
db.create_table(Tag)
db.create_table(ImageTag)
```

### Self Referencing Table

When creating a self referencing table, Python won't let you pass in the class object to the Column class. Instead, add the class name as a string. Only do this for self referencing!

```Python
class Tag(Table):
    id = Column(DataTypes.integer, pk=True)
    tagName = Column(DataTypes.varchar(40))
    parentId = Column(DataTypes.integer, fk=('Tag', 'id')
```

# Release Notes

### Version 0.9.10
- Added beginning of PowerQuery for building custom sql statements

### Version 0.9.9
- Added documentation of many to many relationships
- Added test for junction tables
- Added support for self referencing tables
- Added test for self referencing tables

### Version 0.9.8
- Renaming project name from mr_database to mrdatabase

### Version 0.9.7
- Renaming project name from MrDatabase to mr_database 

### Version 0.9.6 Alpha
- Added pytest code for most functionality
- Added MrDatabase.table_exists
- Renamed get_referenced_record to get_join_record
- Renamed get_referenced_record_all to select_join_record_all
- Moved demo code into /samples/ module
- Updated .gitignore to reflect changes
- Updated documentation (batching)
- Run_tests.bat now assumes python.exe is on PATH
- Preparing a pypi package (setup.py, cleaning project, etc.)

### Version 0.9.5 Alpha
- Added code example of how to do batching of sql commands (10K rows in less than half a sec)
- Added documentation of how to do batching of sql commands
- Added .clone() to record objects (based on copy.deepcopy)
- Experimented with script generation, but performance is too te rrible
- Refactored database_connection (now DatabaseConnection) to better distinguish between mutation, query and batch.
- Added ConType enum class (mutation, query, batch)
- Cleanup, simplification and optimization of Table class
- Cleanup, simplification and optimization of MrDatabase class
- Added autoincrementation for integer primary keys
- Changed the pyside samples to use the new DatabaseConnection
- Added record instance type hint example to documentation


### Version 0.9.4 Alpha
- Added code examples to README.md
- Renamed `MrDatabase.get_next_id` to `MrDatabase.increment_id`
- changed `MrDatabase()` to simply take a path instead of path and db name as separate arguments
- created unified namespace for imports

### Version 0.9.3 Alpha
- property name is no longer required to be passed in as argument

### Version 0.9.2 Alpha
- Fixed demo_blob.py

### Version 0.9.1 Alpha
- Simplified Table definition
- Converted all query generation to use f-strings

### Version 0.9.0 Alpha
- Initial Commit
