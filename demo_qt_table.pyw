from database.mrdatabase import MrDatabase
from database.mrdatabase import LogLevel
from table_schema_examples import City, Person
from PySide2 import QtGui, QtCore, QtWidgets
from qt_models.local_table_model import LocalTableModel
import sys
import os


class DatabaseTableWidget(QtWidgets.QWidget):

    def __init__(self, database: MrDatabase):
        super().__init__()

        self.database_table_model: LocalTableModel = LocalTableModel(database.select_records(City), database)

        self.table_view: QtWidgets.QTableView = None
        self.button_insert: QtWidgets.QPushButton = None
        self.button_delete: QtWidgets.QPushButton = None

        self.init_ui()
        self.setup_signals()

    def init_ui(self):
        self.resize(450, 300)
        self.setWindowTitle(LocalTableModel.__name__)

        self.button_insert = QtWidgets.QPushButton("Insert")
        self.button_delete = QtWidgets.QPushButton("Delete")

        self.table_view = QtWidgets.QTableView()
        self.table_view.setModel(self.database_table_model)

        self.table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSortingEnabled(True)
        self.table_view.sortByColumn(1, QtCore.Qt.AscendingOrder)
        self.table_view.updateGeometry()

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.button_insert)
        hbox.addWidget(self.button_delete)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.table_view, stretch=1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        # sorting by 0th column at startup
        self.database_table_model.sort(0)

        self.show()

    def setup_signals(self):

        self.button_insert.clicked.connect(self.on_click_insert_rows)
        self.button_delete.clicked.connect(self.on_click_remove_rows)

    @QtCore.Slot()
    def on_click_insert_rows(self):
        self.database_table_model.insertRows(0, 1)

    @QtCore.Slot()
    def on_click_remove_rows(self):
        """Continuous or single selection expected"""

        selected_rows = list()
        rows = set()

        # filter out unwanted entries so we end with only one object per row
        for selected_index in self.table_view.selectedIndexes():

            row_index = selected_index.row()

            if row_index not in rows:
                rows.add(row_index)
                selected_rows.append(selected_index)

        if not selected_rows:
            return

        self.database_table_model.removeRows(selected_rows[0].row(), len(rows))


if __name__ == '__main__':

    MrDatabase.logging(level=LogLevel.info)
    db = MrDatabase(os.path.abspath(os.path.join(__file__, os.pardir)), 'test.db')

    db.create_table(City)
    next_id = db.get_next_id('City', 'id')

    if next_id == 0:
        city1 = City()
        city1.id = db.get_next_id('City', 'id')
        city1.postalCode = 8300
        city1.cityName = 'Odder'
        db.insert_record(city1)

        city2 = City()
        city2.id = db.get_next_id('City', 'id')
        city2.postalCode = 8660
        city2.cityName = 'Skanderborg'
        db.insert_record(city2)

        city3 = City()
        city3.id = db.get_next_id('City', 'id')
        city3.postalCode = 2500
        city3.cityName = 'Valby'
        db.insert_record(city3)

    app = QtWidgets.QApplication(sys.argv)
    widget = DatabaseTableWidget(db)

    sys.exit(app.exec_())
