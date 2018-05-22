# MrDatabase v. 0.9.4 Alpha
Databasing as easy as it gets!

## Simple Code Examples

### Create a Database

When creating an instance of MrDatabase, it will see if the database already exists. If it does not, it will create it.

```python
from mr_database import MrDatabase

db = MrDatabase('some/path/my.db')
```

All connecting and disconnecting to the database is handled by the internals of MrDatabase.

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
To insert, update or delete records from the database, you need record objects representing what you want to manipulate.

You can create new records objects like the ```city1``` example or you can fetch them from the database using ```db.select_record``` or ```db.select_records```

```python
city1 = City()
city1.id = db.increment_id("City", "id")
city1.postal_code = 10115
city1.city_name = 'Berlin'

cities = db.select_records(City)
a_city = db.select_record(City, condition='cityName="Berlin"')

db.insert_record(city1)
db.update_record(city1)
db.delete_record(city1)
```

# Release Notes
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
