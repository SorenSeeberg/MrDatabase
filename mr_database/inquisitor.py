from typing import Union
import re

TableName = Union[str, 'Table.__subclasses__()']
AttribName = Union[str, 'Column']

like_pattern = re.compile('\A[A-Za-z0-9_%/]+\Z')
like_chars_pattern = re.compile('[^A-Za-z0-9_%/]+')


class Inquisitor:

    def __init__(self):
        self.sql_fragments = list()

    @staticmethod
    def __resolve_input__(value) -> str:
        if not isinstance(value, str):
            return value.get_table_name()

        return value

    def SELECT(self, attributes):
        self.sql_fragments.append(f'SELECT {", ".join(attributes)}')
        return self

    def FROM(self, table_name: TableName):

        self.sql_fragments.append(f'FROM {self.__resolve_input__(table_name)}')
        return self

    def WHERE(self):
        self.sql_fragments.append('WHERE')
        return self

    def LIKE(self, attribute: str, compare_string: str):

        if not re.search(like_pattern, compare_string):
            compare_string = like_chars_pattern.sub('', compare_string)

        self.sql_fragments.append(f'{attribute} LIKE \'{compare_string}\'')
        return self

    def ORDER(self, *order_clauses: str):
        self.sql_fragments.append(f'ORDER BY {", ".join(order_clauses)}')
        return self

    @staticmethod
    def ASC(column_name: str) -> str:
        return Inquisitor.__sort_order__('ASC', column_name)

    @staticmethod
    def DESC(column_name: str) -> str:
        return Inquisitor.__sort_order__('DESC', column_name)

    @staticmethod
    def __sort_order__(sort_order: str, column_name: str) -> str:
        return f'{column_name} {sort_order}'

    def AND(self):
        self.sql_fragments.append('AND')
        return self

    def OR(self):
        self.sql_fragments.append('OR')
        return self

    def NOT(self):
        self.sql_fragments.append('NOT')
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

        self.sql_fragments.append(
            f'INNER JOIN {target_table} ON {target_table}.{target_attrib} = {source_table}.{source_attrib}')

        return self

    def expression(self, exp):
        self.sql_fragments.append(exp)
        return self

    def __compile__(self) -> str:
        return f'{" ".join(self.sql_fragments)};'

    def __repr__(self) -> str:
        return '\n'.join(self.sql_fragments) + ';\n'
