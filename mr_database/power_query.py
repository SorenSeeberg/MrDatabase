from mr_database import DataTypes
from mr_database import Table
from mr_database import Column

from typing import Union

TableName = Union[str, 'Table.__subclasses__()']
AttribName = Union[str, 'Column']


class City(Table):
    id = Column(DataTypes.integer, pk=True)
    postalCode = Column(DataTypes.smallint, default=9999, display_name='Postal Code')
    cityName = Column(DataTypes.varchar(40), default='New York', display_name='City Name')


class Person(Table):
    id = Column(DataTypes.integer, pk=True)
    firstName = Column(DataTypes.varchar(40))
    lastName = Column(DataTypes.varchar(40))
    cityId = Column(data_type=DataTypes.integer, fk=(City, 'id'), default=0)


class PowerQuery:

    def __init__(self):
        self.action_queue = list()

    @staticmethod
    def __resolve_input__(value) -> str:
        if not isinstance(value, str):
            return value.get_table_name()

        return value

    def SELECT(self, attributes):
        self.action_queue.append(f'SELECT {", ".join(attributes)}')
        return self

    def FROM(self, table_name: TableName):

        self.action_queue.append(f'FROM {self.__resolve_input__(table_name)}')
        return self

    def WHERE(self):
        self.action_queue.append('WHERE')
        return self

    def LIKE(self, attribute: str, compare_string: str):
        self.action_queue.append(f'{attribute} LIKE \'{compare_string}\'')
        return self

    def ORDER(self, *order_clauses: str):
        self.action_queue.append(f'ORDER BY {", ".join(order_clauses)}')
        return self

    @staticmethod
    def ASC(column_name: str) -> str:
        return PowerQuery.__sort_order__('ASC', column_name)

    @staticmethod
    def DESC(column_name: str) -> str:
        return PowerQuery.__sort_order__('DESC', column_name)

    @staticmethod
    def __sort_order__(sort_order: str, column_name: str) -> str:
        return f'{column_name} {sort_order}'

    def AND(self):
        self.action_queue.append('AND')
        return self

    def OR(self):
        self.action_queue.append('OR')
        return self

    def NOT(self):
        self.action_queue.append('NOT')
        return self

    def INNER_JOIN(self,
                   source_table: TableName,
                   source_attrib: AttribName,
                   target_table: TableName,
                   target_attrib: AttribName):

        source_table: str = self.__resolve_input__(source_table)
        source_attrib: str = self.__resolve_input__(source_attrib)
        target_table: str = self.__resolve_input__(target_table)
        target_attrib: str = self.__resolve_input__(target_attrib)

        self.action_queue.append(
            f'INNER JOIN {target_table} ON {target_table}.{target_attrib} = {source_table}.{source_attrib}')

        return self

    def expression(self, exp):
        self.action_queue.append(exp)
        return self

    def __compile__(self) -> str:
        return f'{" ".join(self.action_queue)};'

    def __repr__(self) -> str:
        return self.__compile__()


if __name__ == '__main__':
    query1 = PowerQuery().SELECT(['id', 'name']).FROM('Person').WHERE().expression('id > 10').AND().LIKE('name', 'john')
    query2 = PowerQuery().SELECT(['id', 'name']).FROM(Person).INNER_JOIN(Person, 'cityId', City, 'id')
    query3 = PowerQuery().SELECT(['id', 'name']).FROM(Person).ORDER(PowerQuery.ASC('id'), PowerQuery.DESC('name'))

    print(query1)
    print(query2)
    print(query3)
