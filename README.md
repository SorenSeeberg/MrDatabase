# MrDatabase v. 0.9.5 Alpha
Databasing as easy as it gets!

## Simple Code Examples

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

### Records (DML)
To insert, update or delete records in the database, you need record objects representing what you want to manipulate.

You can create new record objects like the ```city1``` example or you can fetch existing ones from the database using ```db.select_record``` or ```db.select_records```. Lastly you can call ```.clone``` on the record you want to copy. This method returns a ```copy.deepcopy``` if the record in question.

```python
city1 = City()
city1.id = db.increment_id('City', 'id')
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
By default, mutating actions like ```insert_record``` and ```update_record```, commit changes to the database one command at a time. This is very easy to work with, but for heavy work loads, this can be quite taxing on performance. If you need to call many mutating sql commands you can batch commands together to dramatically improve performance.

To set it up, you use the ```database_connection``` context manager. You pass it the ```db``` object and set ```commit=True```. Whenever you call a database mutating actions in scope of the ```database_connection```, you simply set ```commit=False``` on the individual commands. This way, the commit will only be called once you are done.
```python
from mr_database import database_connection

next_id: int = db.increment_id('Person', 'id')

with database_connection(db, commit=True):
    for person_id in range(next_id, next_id + 10000):
        new_person = person_1.clone()
        new_person.id = person_id
        new_person.firstName += f'_{person_id}'
        db.insert_record(new_person, commit=False)
```

The example above inserts 10.000 clones of a ```Person``` record. It takes less than 500ms.

# Release Notes
### Version 0.9.5 Alpha
- Added code example of how to do batching of sql commands (10K rows in less than half a sec)
- Added documentation of how to do batching of sql commands
- Added .clone() to record objects (based on copy.deepcopy)
- Experimented with script generation, but performance is too terrible

### Version 0.9.4 Alpha
- Added code examples to README.md
- Renamed ```MrDatabase.get_next_id``` to ```MrDatabase.increment_id```
- changed ```MrDatabase()``` to simply take a path instead of path and db name as separate arguments
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
