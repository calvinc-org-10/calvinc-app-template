from PySide6.QtSql import (QSqlDatabase, QSqlQuery )

app_dbName = 'D:\\AppDev\\datasets\\hbl.sqlite'

# class appdb(QSqlDatabase):
class appdb:
    _instance = None  # Store the singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_db()  # Correctly call the method after creating instance
        return cls._instance

    def _init_db(self):
        dbDriver = 'QSQLITE'
        connectName = 'app_incShip'

        # Check if the connection already exists
        if QSqlDatabase.contains(connectName):
            self.db = QSqlDatabase.database(connectName)
        else:
            self.db = QSqlDatabase.addDatabase(dbDriver, connectName)
            self.db.setDatabaseName(app_dbName)
            if not self.db.open():
                print("Database connection failed:", self.db.lastError().text())

    def connection(self):
        """Returns the QSqlDatabase connection"""
        return self.db

appDatabase = appdb().connection()