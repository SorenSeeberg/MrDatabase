from PySide2 import QtGui, QtCore, QtWidgets
from mr_database import MrDatabase
from mr_database import Table
from mr_database import Records
from database.databaseconnection import DatabaseConnection


class LocalTableModel(QtCore.QAbstractTableModel):

    def __init__(self, records, database: MrDatabase, parent=None):
        super().__init__(parent)
        self.__database__: MrDatabase = database
        self.__records__: Records = records
        self.__table__: Table.__subclasses__ = records.table_class()
        self.__headers__ = self.__records__[0].get_column_display_names()

    @property
    def database(self) -> MrDatabase:
        return self.__database__

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.__records__)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.__headers__)

    def flags(self, index: QtCore.QModelIndex):

        if index.column() == 0:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        else:
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index: QtCore.QModelIndex, role=None):

        row: int = index.row()
        column: int = index.column()

        if role == QtCore.Qt.EditRole:
            return self.__records__[row].get_value_by_index(column)

        if role == QtCore.Qt.DisplayRole:
            return self.__records__[row].get_value_by_index(column)

    def setData(self, q_model_index, value, role=None) -> bool:

        if role == QtCore.Qt.EditRole:

            row: int = q_model_index.row()
            column: int = q_model_index.column()

            if self.__records__[row].set_value_by_index(column, value):
                self.database.update_record(self.__records__[row])
                self.dataChanged.emit(q_model_index, q_model_index)
                return True

        return False

    def headerData(self, section, orientation, role=None):

        if role == QtCore.Qt.DisplayRole:

            if orientation == QtCore.Qt.Horizontal:

                if section < len(self.__headers__):
                    return self.__headers__[section]
                else:
                    return 'not implemented'

    def insertRows(self, position: int, rows: int, parent=QtCore.QModelIndex(), *args, **kwargs) -> bool:

        self.beginInsertRows(parent, position, position)

        new_record: Table.__subclasses__ = self.__table__()
        new_record.id = self.database.increment_id(new_record.get_table_name())
        self.__records__.append(new_record)
        self.database.insert_record(new_record)

        self.endInsertRows()

        return True

    def removeRows(self, position: int, rows: int, parent=QtCore.QModelIndex(), *args, **kwargs) -> bool:

        self.beginRemoveRows(parent, position, position + rows - 1)

        to_be_deleted = list()

        with DatabaseConnection(self.__database__, commit=True):

            for i in range(position, position + rows):

                record = self.__records__[i]

                self.database.sub_transaction(self.__database__.delete_record(record, commit=False))
                to_be_deleted.append(record)

        # deleting the row objects in a second pass to not mess with the list indices
        # while interacting with the database
        for record in to_be_deleted:
            self.__records__.remove(record)

        self.endRemoveRows()

        return True

    def sort(self, col: int, order: int=None) -> None:
        """Sort table by given column number"""

        self.layoutAboutToBeChanged.emit()
        self.__records__.sort(col, reverse=bool(order))
        self.layoutChanged.emit()
