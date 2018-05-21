# MrDatabase
Connect PySide2 and SQLite with ease

## Version 0.9.2 Alpha (Current)
- Fixed demo_blob.py

# Table

Setting up a table is very easy

```python
class City(Table):

    id = Column('id', DataTypes.integer, pk=True)
    postalCode = Column('postalCode', DataTypes.smallint, default=9999, display_name='Postal Code')
    cityName = Column('cityName', DataTypes.varchar(40), default='New York', display_name='City Name')
```

# Release Notes

## Version 0.9.1 Alpha
- Simplified Table definition
- Converted all query generation to use f-strings

## Version 0.9.0 Alpha
- Initial Commit
