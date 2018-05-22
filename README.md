# MrDatabase v. 0.9.4 Alpha
Databasing as Easy as it Gets!

## Simple Code Examples

### Create or Connect to Existing Database

```python
from database.mrdatabase import MrDatabase

db = MrDatabase('some/path/my.db')
```

### Create Table Class

Creating a new table class is super easy. This class works both as schema and record factory. Simply create a class that inherits from ```Table```. Add fields as class variables. Each field must be an instance of ```Column```. Voilà, the table is ready!

```python
from database.column import *
from database.table import *

class City(Table):

    id = Column(DataTypes.integer, pk=True)
    postalCode = Column(DataTypes.smallint, default=9999)
    cityName = Column(DataTypes.varchar(40), default='New York')
```

### Table Actions
```python
db.create_table(City)
db.drop_table(City)
```

### Record Actions
```python
city1 = City()
city1.id = db.increment_id("City", "id")
city1.postal_code = 10115
city1.city_name = 'Berlin'

db.insert_record(city1)
db.update_record(city1)
db.delete_record(city1)
all_cities = db.select_records(City)
```

# Release Notes
###Version 0.9.4 Alpha
- Added code examples to README.md
- Renamed ```MrDatabase.get_next_id``` to ```MrDatabase.increment_id```
- changed ```MrDatabase()``` to simply take a path instead of path and db name as separate arguments

###Version 0.9.3 Alpha
- property name is no longer required to be passed in as argument

### Version 0.9.2 Alpha
- Fixed demo_blob.py

### Version 0.9.1 Alpha
- Simplified Table definition
- Converted all query generation to use f-strings

### Version 0.9.0 Alpha
- Initial Commit
