import PySide6
from PySide6.QtSql import (QSqlDatabase, QSqlQuery )

cMenu_dbName = "D:\\AppDev\\datasets\\hbl.sqlite"


class cMenudb:
    _instance = None  # Store the singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_db()  # Correctly call the method after creating instance
        return cls._instance
    # __new__

    def _init_db(self):
        dbDriver = 'QSQLITE'
        connectName = 'con_cMenu'

        # Check if the connection already exists
        if QSqlDatabase.contains(connectName):
            self.db = QSqlDatabase.database(connectName)
        else:
            self.db = QSqlDatabase.addDatabase(dbDriver, connectName)
            self.db.setDatabaseName(cMenu_dbName)
            if not self.db.open():
                print("Database connection failed:", self.db.lastError().text())
    # _init_db

    def connection(self):
        """Returns the QSqlDatabase connection"""
        return self.db
    # connection
# cMenudb

cMenuDatabase = cMenudb().connection()

