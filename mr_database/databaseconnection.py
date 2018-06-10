import sqlite3 as sqlite


class ConType:

    query = 0
    mutation = 1
    batch = 2


class DatabaseConnection:

    is_batching = False

    def __init__(self, database_object: 'MrDatabase', con_type: int=ConType.mutation):

        self.database_object = database_object
        self.con_type: int = con_type

    def __enter__(self):

        if self.con_type == ConType.query:
            if not DatabaseConnection.is_batching:
                self.connect()

        elif self.con_type == ConType.mutation:
            if not DatabaseConnection.is_batching:
                self.connect()

        elif self.con_type == ConType.batch:
            self.connect()
            DatabaseConnection.is_batching = True

    def __exit__(self, *args):

        if self.con_type == ConType.query:
            if not self.is_batching:
                self.close()

        elif self.con_type == ConType.mutation:

            if not self.is_batching:
                self.commit()
                self.close()

        elif self.con_type == ConType.batch:
            DatabaseConnection.is_batching = False
            self.commit()
            self.close()

    def connect(self):
        self.database_object.con = sqlite.connect(self.database_object.database_path)
        self.database_object.cur = self.database_object.con.cursor()

    def commit(self):
        self.database_object.con.commit()

    def close(self):
        self.database_object.con.close()
