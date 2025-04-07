
# from django.db import models

from random import randint

from PySide6.QtWidgets import (QApplication, )
from PySide6.QtSql import (QSqlRelation, QSqlQuery, )
from .utils import (pleaseWriteMe, tblExists, cQSqlTableModel, cQSqlRelationalTableModel, )

from .database import cMenuDatabase
from .menucommand_constants import MENUCOMMANDS, COMMANDNUMBER
from .dbmenulist import (newgroupnewmenu_menulist, )


tblName_menuGroups = 'cMenu_menuGroups'
tblName_menuItems = 'cMenu_menuItems'
tblName_cParameters = 'cMenu_cParameters'
tblName_cGreetings = 'cMenu_cGreetings'

class menuGroups(cQSqlTableModel):
    """
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
    "GroupName" varchar(100) NOT NULL UNIQUE, 
    "GroupInfo" varchar(250) NOT NULL);
    """
    tblName = tblName_menuGroups
    def __init__(self, parent = None):
        initTable = not all(tblExists(self.tblName, cMenuDatabase))
        if initTable:
            self._createtable()
        super().__init__(self.tblName, cMenuDatabase, parent)
        if initTable:
            # create a starter group and menu
            newrec = self.record()
            newrec.setValue('GroupName', 'Group Name')
            newrec.setValue('GroupInfo', 'Group Info')

            #TODO: generic into newrec.save()            
            # dbTbl = menuGroups()
            dbTbl = self
            dbTbl.select()
            row = dbTbl.rowCount()
            dbTbl.insertRecord(row,newrec)
            if not dbTbl.submitAll():
                print("Failed to submit changes:", dbTbl.lastError().text())

            # fix if insertRecord didn't autosave
            grppk = dbTbl.record(row).value('id')

            # create a default menu
            # newgroupnewmenu_menulist to menuItems
            dbTbl = menuItems()
            dbTbl.setFilter('FALSE')
            dbTbl.select()
            for rec in newgroupnewmenu_menulist:
                newmenurec = dbTbl.record()
                newmenurec.setNull('id')
                newmenurec.setValue('MenuGroup_id', grppk)
                newmenurec.setValue('MenuID', 0)
                for fldNm, vlu in rec.items():
                    newmenurec.setValue(fldNm, vlu)
                dbTbl.insertRecord(0, newmenurec)
            newmenurec = dbTbl.record()
            newmenurec.setNull('id')
            newmenurec.setValue('MenuGroup_id', grppk)
            newmenurec.setValue('MenuID', 0)
            newmenurec.setValue('OptionNumber', 11)
            newmenurec.setValue('OptionText', 'Edit Menu')
            newmenurec.setValue('Command', COMMANDNUMBER.EditMenu)
            newmenurec.setValue('Argument', '')
            newmenurec.setValue('PWord', '')
            dbTbl.insertRecord(0, newmenurec)
            
            if not dbTbl.submitAll():
                print("Failed to submit changes:", dbTbl.lastError().text())

    def _createtable(self):
        query = QSqlQuery(cMenuDatabase)
        query.exec(f'''
            CREATE TABLE IF NOT EXISTS "{self.tblName}" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
                "GroupName" varchar(100) NOT NULL UNIQUE, 
                "GroupInfo" varchar(250) NOT NULL DEFAULT ""
                );
            ''')


class menuItems(cQSqlRelationalTableModel):
    """
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
    "MenuID" smallint NOT NULL, 
    "OptionNumber" smallint NOT NULL, 
    "OptionText" varchar(250) NOT NULL, 
    "Command" integer NULL, 
    "Argument" varchar(250) NOT NULL, 
    "PWord" varchar(250) NOT NULL, 
    "TopLine" bool NULL, 
    "BottomLine" bool NULL, 
    "MenuGroup_id" bigint NULL REFERENCES "cMenu_menugroups" ("id") DEFERRABLE INITIALLY DEFERRED, 
        CONSTRAINT "mnuItUNQ_mGrp_mID_OptNum" UNIQUE ("MenuGroup_id", "MenuID", "OptionNumber"));
    """
    tblName = tblName_menuItems
    _groupKey = 'MenuGroup_id'
    _rltblName = tblName_menuGroups
    _db = cMenuDatabase
    def __init__(self, parent = None):
        if not all(tblExists(self.tblName, cMenuDatabase)):
            self._createtable()
        super().__init__(self.tblName, self._db, parent)
        self.setRelation(self.fieldIndex(self._groupKey), QSqlRelation(self._rltblName, 'id', 'GroupName'))
        self.select()
        # initial menu should be constructed, but menuGroups should handle that

    def selectStatement(self):
        base_sql = super().selectStatement()
        # Inject your extra field (example: calculated field)
        # Warning: This is fragile if the base class changes its SQL format
        return base_sql.replace(
            " FROM ",
            f", {self._groupKey} FROM "
        )

    def _createtable(self):
        if not all(tblExists(self._rltblName, cMenuDatabase)):
            dummycreate = menuGroups()  # will create if doesn't exist
        query = QSqlQuery(cMenuDatabase)
        query.exec(f'''
            CREATE TABLE IF NOT EXISTS "{self.tblName}" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
                "MenuID" smallint NOT NULL, 
                "OptionNumber" smallint NOT NULL, 
                "OptionText" varchar(250) NOT NULL DEFAULT "", 
                "Command" integer NULL, 
                "Argument" varchar(250) NOT NULL DEFAULT "", 
                "PWord" varchar(250) NOT NULL DEFAULT "", 
                "TopLine" bool NULL, "BottomLine" bool NULL, 
                "{self._groupKey}" bigint NULL 
                    REFERENCES "{self._rltblName}" ("id") DEFERRABLE INITIALLY DEFERRED, 
                CONSTRAINT "mnuItUNQ_mGrp_mID_OptNum" UNIQUE ("MenuGroup_id", "MenuID", "OptionNumber")
                );
            ''')
        query.exec(f'''
            CREATE INDEX "{self.tblName}_{self._groupKey}_e8382487" ON "{self.tblName}" ("{self._groupKey}");
            '''   
            )

class cParameters(cQSqlTableModel):
    """
    "ParmName" varchar(100) NOT NULL PRIMARY KEY, 
    "ParmValue" varchar(512) NOT NULL, 
    "UserModifiable" bool NOT NULL, 
    "Comments" varchar(512) NOT NULL);
    """
    tblName = tblName_cParameters
    def __init__(self, parent = None):
        if not all(tblExists(self.tblName, cMenuDatabase)):
            self._createtable()
        super().__init__(self.tblName, cMenuDatabase, parent)
        # self.setTable('cMenu_cparameters')
    
    def _createtable(self):
        query = QSqlQuery(cMenuDatabase)
        query.exec(f'''
            CREATE TABLE IF NOT EXISTS "{self.tblName}" (
                "ParmName" varchar(100) NOT NULL PRIMARY KEY, 
                "ParmValue" varchar(512) NOT NULL DEFAULT "", 
                "UserModifiable" bool NULL, 
                "Comments" varchar(512) NOT NULL DEFAULT ""
                );
            '''   
            )

def getcParm(req, parmname):
    r = cParameters()
    r.setFilter(f'ParmName="{parmname}"')
    if r.select():
        return r.record(0).value('ParmValue')
    else:
        return ''

def setcParm(req, parmname, parmvalue):
    #FIXMEFIXMERESTARTHERE
    pleaseWriteMe(QApplication.instance(), 'setcParm')
    return
    P, crFlag = cParameters.objects.get_or_create(ParmName=parmname)
    P.ParmValue = parmvalue
    P.save()


class cGreetings(cQSqlTableModel):
    """
    id = models.AutoField(primary_key=True)
    Greeting = models.CharField(max_length=2000)
    """
    tblName = tblName_cGreetings
    def __init__(self, parent = None):
        if not all(tblExists(self.tblName, cMenuDatabase)):
            self._createtable()
        super().__init__(self.tblName, cMenuDatabase, parent)
        # self.setTable('cMenu_cgreetings')
    def randomGreeting(self) -> str:
        # do better
        self.select()
        n = randint(1,self.rowCount()) - 1
        return self.record(n).value('Greeting')

    def _createtable(self):
        query = QSqlQuery(cMenuDatabase)
        query.exec(f'''
            CREATE TABLE IF NOT EXISTS "{self.tblName}" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
                "Greeting" varchar(2000) NOT NULL
                );
            '''   
            )

