from typing import Union
import re


class Expressor:

    def __init__(self):
        self.re_fragments = list()

    @staticmethod
    def __resolve_input__(value) -> str:
        if not isinstance(value, str):
            return value.get_table_name()

        return value

    def __repr__(self) -> str:
        return r''.join(self.re_fragments)

    def __str__(self):
        return r''.join(self.re_fragments)

    def group(self, expression: 'Expressor'):
        self.re_fragments.append(f'({str(expression)})')
        return self

    def begin_line(self):
        """ Beginning of line '\A' """
        self.re_fragments.append(r'\A')
        return self

    def end_line(self):
        """ End of line '\Z' """
        self.re_fragments.append(r'\Z')
        return self

    def fixed_string(self, string: str):
        self.re_fragments.append(string)
        return self

    def sequence_string(self, sequence: str):

        self.re_fragments.append(f'[{sequence}]')
        return self

    def any(self):
        """ Any char except newline '.' """
        self.re_fragments.append('.')

    def zero_plus(self):
        self.re_fragments.append('*')
        return self

    def one_plus(self):
        self.re_fragments.append('+')
        return self

    def zero_or_one(self):
        self.re_fragments.append('?')
        return self

    def exactly(self, count: int):
        self.re_fragments.append(f'{{{count}}}')
        return self


if __name__ == '__main__':
    expression = Expressor().begin_line().sequence_string('A-Za-z0-9_%/').one_plus().end_line()

    name = Expressor().sequence_string('A-Za-z').one_plus()
    age = Expressor().sequence_string('0-9').exactly(2)
    name_and_age = Expressor().begin_line().fixed_string('name:').group(name).fixed_string('age:').group(age).end_line()
    print(name_and_age)

    print(expression)
    compiled = re.compile(str(expression))
    print(compiled)
    print(re.compile('\\A[A-Za-z0-9_%/]+\\Z'))
