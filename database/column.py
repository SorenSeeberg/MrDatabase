#!/usr/bin/python3
# -*- coding: utf-8 -*-


class DataTypes:

    @staticmethod
    def char(num_chars) -> str:

        return f'CHAR({num_chars})'

    @staticmethod
    def varchar(num_chars=None) -> str:

        if num_chars:
            return f'VARCHAR({num_chars})'
        else:
            return 'VARCHAR'

    smallint = 'SMALLINT'
    integer = 'INTEGER'
    datetime = 'DATETIME'
    blob = 'BLOB'


class Column:

    data_types: DataTypes = DataTypes

    def __init__(self,
                 data_type: str,
                 data_type_var=None,
                 default=None,
                 pk: bool=False,
                 fk: 'Table.__subclasses__'=None,
                 unique: bool=False,
                 not_null: bool=False,
                 display_name: str=None):

        self.data_type = data_type
        self.data_type_var = data_type_var
        self.default = default
        self.pk = pk

        if fk is not None:
            self.fk_table = fk[0]
            self.fk_property = fk[1]
            self.fk = True
        else:
            self.fk = False

        self.unique = unique
        self.not_null = not_null

        self.display_name = display_name

    def __len__(self):
        pass

    def __repr__(self) -> str:
        return f'Column({self.data_type})'

    def __eq__(self, other: 'Column') -> bool:
        pass




