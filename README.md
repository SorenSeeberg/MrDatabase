# MrDatabase
Connect PySide2 and SQLite with ease

## Version 0.9.3 Alpha (Current)
- property name is no longer required to be passed in as argument

# Table

Setting up a table is very easy

```python
class City(Table):

    id = Column(DataTypes.integer, pk=True)
    postalCode = Column(DataTypes.smallint, default=9999)
    cityName = Column(DataTypes.varchar(40), default='New York')
```

# Release Notes

## Version 0.9.2 Alpha
- Fixed demo_blob.py

## Version 0.9.1 Alpha
- Simplified Table definition
- Converted all query generation to use f-strings

## Version 0.9.0 Alpha
- Initial Commit
