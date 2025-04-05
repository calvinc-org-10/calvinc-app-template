from typing import (Any, Dict, List, )

from .menucommand_constants import (MENUCOMMANDS, COMMANDNUMBER, )

# self, menuID: str, menuName: str, menuItems:Dict[int,Dict]):
# {'keys': {'MenuGroup': 1, 'MenuID': 0, 'OptionNumber': 0}, 
#     'values': {etc}}
test_menulist = [
{'keys': {'MenuGroup': 1, 'MenuID': 0, 'OptionNumber': 0},
    'values': {'OptionText': 'Admin Menu', 'Command': None, 'Argument': '', 'PWord': '', 'TopLine': None, 'BottomLine': None, }},
{'keys': {'MenuGroup': 1, 'MenuID': 0, 'OptionNumber': 1},
    'values': {'OptionText': 'User Admin', 'Command': 11, 'Argument': 'L10-WICS-UAdmin', 'PWord': '', 'TopLine': None, 'BottomLine': None, }},
{'keys': {'MenuGroup': 1, 'MenuID': 0, 'OptionNumber': 2},
    'values': {'OptionText': 'Edit Menu', 'Command': 91, 'Argument': '', 'PWord': '', 'TopLine': None, 'BottomLine': None, }},
{'keys': {'MenuGroup': 1, 'MenuID': 0, 'OptionNumber': 3},
    'values': {'OptionText': 'Django Admin', 'Command': 11, 'Argument': 'django-admin', 'PWord': '', 'TopLine': None, 'BottomLine': None, }},
{'keys': {'MenuGroup': 1, 'MenuID': 0, 'OptionNumber': 11},
    'values': {'OptionText': 'IncShip', 'Command': 1, 'Argument': '5', 'PWord': '', 'TopLine': None, 'BottomLine': None, }},
{'keys': {'MenuGroup': 1, 'MenuID': 0, 'OptionNumber': 19},
    'values': {'OptionText': 'Change Password', 'Command': 51, 'Argument': '', 'PWord': '', 'TopLine': None, 'BottomLine': None, }},
{'keys': {'MenuGroup': 1, 'MenuID': 0, 'OptionNumber': 20},
    'values': {'OptionText': 'Go Away!', 'Command': 200, 'Argument': '', 'PWord': '', 'TopLine': None, 'BottomLine': None, }},
{'keys': {'MenuGroup': 1, 'MenuID': 3, 'OptionNumber': 0},
    'values': {'OptionText': 'Calvin\'s Menu', 'Command': None, 'Argument': '', 'PWord': '', 'TopLine': 1, 'BottomLine': 1, }},
{'keys': {'MenuGroup': 1, 'MenuID': 3, 'OptionNumber': 4},
    'values': {'OptionText': 'new reference', 'Command': 11, 'Argument': 'newref', 'PWord': '', 'TopLine': None, 'BottomLine': None, }},
{'keys': {'MenuGroup': 1, 'MenuID': 3, 'OptionNumber': 1},
    'values': {'OptionText': 'HBL', 'Command': 11, 'Argument': 'HBLForm', 'PWord': '', 'TopLine': None, 'BottomLine': None, }},
{'keys': {'MenuGroup': 1, 'MenuID': 3, 'OptionNumber': 3},
    'values': {'OptionText': 'references', 'Command': 11, 'Argument': 'refsForm', 'PWord': '', 'TopLine': None, 'BottomLine': None, }},
{'keys': {'MenuGroup': 1, 'MenuID': 3, 'OptionNumber': 6},
    'values': {'OptionText': 'Invoices', 'Command': 11, 'Argument': 'InvoiceForm', 'PWord': '', 'TopLine': None, 'BottomLine': None, }},
{'keys': {'MenuGroup': 1, 'MenuID': 3, 'OptionNumber': 8},
    'values': {'OptionText': 'Invoices to Enter', 'Command': 11, 'Argument': 'InvoicesNotsubmitted', 'PWord': '', 'TopLine': None, 'BottomLine': None, }},
{'keys': {'MenuGroup': 1, 'MenuID': 3, 'OptionNumber': 11},
    'values': {'OptionText': 'Test 1', 'Command': 11, 'Argument': 'test01', 'PWord': '', 'TopLine': 1, 'BottomLine': 1, }},
{'keys': {'MenuGroup': 1, 'MenuID': 3, 'OptionNumber': 12},
    'values': {'OptionText': 'Test 2', 'Command': 11, 'Argument': 'test02', 'PWord': '', 'TopLine': 1, 'BottomLine': 1, }},
{'keys': {'MenuGroup': 1, 'MenuID': 3, 'OptionNumber': 14},
    'values': {'OptionText': 'Initial Loads', 'Command': 1, 'Argument': '6', 'PWord': '', 'TopLine': None, 'BottomLine': None, }},
{'keys': {'MenuGroup': 1, 'MenuID': 3, 'OptionNumber': 15},
    'values': {'OptionText': 'Spreadsheet Interface', 'Command': 1, 'Argument': '6', 'PWord': '', 'TopLine': None, 'BottomLine': None, }},
{'keys': {'MenuGroup': 1, 'MenuID': 3, 'OptionNumber': 19},
    'values': {'OptionText': 'Run SQL', 'Command': 31, 'Argument': '', 'PWord': '', 'TopLine': None, 'BottomLine': None, }},
{'keys': {'MenuGroup': 1, 'MenuID': 3, 'OptionNumber': 20},
    'values': {'OptionText': 'Return to Main Menu', 'Command': 1, 'Argument': '5', 'PWord': '', 'TopLine': 1, 'BottomLine': 1, }},
{'keys': {'MenuGroup': 1, 'MenuID': 5, 'OptionNumber': 0},
    'values': {'OptionText': 'Main Menu', 'Command': None, 'Argument': 'Default', 'PWord': '', 'TopLine': 1, 'BottomLine': 1, }},
{'keys': {'MenuGroup': 1, 'MenuID': 5, 'OptionNumber': 1},
    'values': {'OptionText': 'Calvin', 'Command': 1, 'Argument': '3', 'PWord': '', 'TopLine': None, 'BottomLine': None, }},
{'keys': {'MenuGroup': 1, 'MenuID': 5, 'OptionNumber': 2},
    'values': {'OptionText': 'Frequently Used Menu', 'Command': 1, 'Argument': '1', 'PWord': '', 'TopLine': None, 'BottomLine': None, }},
{'keys': {'MenuGroup': 1, 'MenuID': 5, 'OptionNumber': 17},
    'values': {'OptionText': 'Test', 'Command': 1, 'Argument': '4', 'PWord': '', 'TopLine': None, 'BottomLine': None, }},
{'keys': {'MenuGroup': 1, 'MenuID': 5, 'OptionNumber': 18},
    'values': {'OptionText': 'System Menu', 'Command': 1, 'Argument': '99', 'PWord': '', 'TopLine': 1, 'BottomLine': 1, }},
{'keys': {'MenuGroup': 1, 'MenuID': 5, 'OptionNumber': 19},
    'values': {'OptionText': 'Admin Menu', 'Command': 1, 'Argument': '0', 'PWord': '', 'TopLine': None, 'BottomLine': None, }},
{'keys': {'MenuGroup': 1, 'MenuID': 5, 'OptionNumber': 20},
    'values': {'OptionText': 'Go Away!', 'Command': 200, 'Argument': '', 'PWord': '', 'TopLine': 1, 'BottomLine': 1, }},
{'keys': {'MenuGroup': 1, 'MenuID': 99, 'OptionNumber': 0},
    'values': {'OptionText': 'System Menu', 'Command': None, 'Argument': '', 'PWord': '', 'TopLine': 1, 'BottomLine': 1, }},
{'keys': {'MenuGroup': 1, 'MenuID': 99, 'OptionNumber': 1},
    'values': {'OptionText': 'Edit Parameters', 'Command': 92, 'Argument': '', 'PWord': '', 'TopLine': 1, 'BottomLine': 1, }},
{'keys': {'MenuGroup': 1, 'MenuID': 99, 'OptionNumber': 2},
    'values': {'OptionText': 'Edit Greetings', 'Command': 93, 'Argument': '', 'PWord': '', 'TopLine': 1, 'BottomLine': 1, }},
{'keys': {'MenuGroup': 1, 'MenuID': 99, 'OptionNumber': 4},
    'values': {'OptionText': 'Edit Menu', 'Command': 91, 'Argument': '', 'PWord': '', 'TopLine': 1, 'BottomLine': 1, }},
{'keys': {'MenuGroup': 1, 'MenuID': 99, 'OptionNumber': 20},
    'values': {'OptionText': 'Main menu', 'Command': 1, 'Argument': '5', 'PWord': '', 'TopLine': 1, 'BottomLine': 1, }},
{'keys': {'MenuGroup': 1, 'MenuID': 6, 'OptionNumber': 0},
    'values': {'OptionText': 'Initial Loads', 'Command': None, 'Argument': '', 'PWord': '', 'TopLine': None, 'BottomLine': None, }},
{'keys': {'MenuGroup': 1, 'MenuID': 6, 'OptionNumber': 20},
    'values': {'OptionText': 'Return to Main Menu', 'Command': 1, 'Argument': '5', 'PWord': '', 'TopLine': None, 'BottomLine': None, }},
{'keys': {'MenuGroup': 1, 'MenuID': 6, 'OptionNumber': 2},
    'values': {'OptionText': 'init-load-HBL-00', 'Command': 11, 'Argument': 'init-load-HBL-00', 'PWord': '', 'TopLine': None, 'BottomLine': None, }},
{'keys': {'MenuGroup': 1, 'MenuID': 6, 'OptionNumber': 3},
    'values': {'OptionText': 'load Invoices', 'Command': 11, 'Argument': 'init-load-Inv-00', 'PWord': '', 'TopLine': None, 'BottomLine': None, }},
]

newgroupnewmenu_menulist = [
{'MenuID': 0, 'OptionNumber': 0,
    'OptionText': 'New Menu', 'Command': None, 'Argument': 'Default', 'PWord': '', 'TopLine': 1, 'BottomLine': 1, },
{'MenuID': 0, 'OptionNumber': 19,
    'OptionText': 'Change Password', 'Command': COMMANDNUMBER.ChangePW, 'Argument': '', 'PWord': '', },
{'MenuID': 0, 'OptionNumber': 20,
    'OptionText': 'Go Away!', 'Command': COMMANDNUMBER.ExitApplication, 'Argument': '', 'PWord': '', },
]

newmenu_menulist = [
{'OptionNumber': 0,
    'OptionText': 'New Menu', 'Command': None, 'Argument': '', 'PWord': '', 'TopLine': 1, 'BottomLine': 1, },
{'OptionNumber': 20,
    'OptionText': 'Return to Main Menu', 'Command': COMMANDNUMBER.LoadMenu, 'Argument': '0', 'PWord': '', },
]


# from django.db.models import Min, QuerySet
# from .models import menuItems
from PySide6.QtSql import (QSqlRelationalTableModel, QSqlRelation, QSqlTableModel, QSqlQueryModel, QSqlRecord, QSqlQuery,  )
from .database import cMenuDatabase

class MenuRecords(QSqlRelationalTableModel):
# class MenuRecords(QSqlQueryModel):
    # mSource = menuItems.objects
    _tblName = 'cMenu_menuitems'
    _groupKey = 'MenuGroup_id'
    _rltblName = 'cMenu_menuGroups'
    _db = cMenuDatabase
    # _theQuery = f"""
    #     SELECT 
    #         t.*,
    #         r.GroupName
    #     FROM {_tblName} t
    #       LEFT JOIN {_rltblName} r ON t.MenuGroup_id = r.id
    # """
    
    def __init__(self, parent = None, db = None):
        if db is None:
            db = self._db
        super().__init__(parent, db)
        # if db is None:
        #     super().__init__(parent)
        # else:
        #     super().__init__(parent, db)
        self.setTable(self._tblName)
        self.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)    # think about this - pass as parm?
        self.setRelation(self.fieldIndex(self._groupKey), QSqlRelation(self._rltblName, 'id', 'GroupName'))
        
        self.select()

    def selectStatement(self):
        base_sql = super().selectStatement()
        # Inject your extra field (example: calculated field)
        # Warning: This is fragile if the base class changes its SQL format
        return base_sql.replace(
            " FROM ",
            f", {self._groupKey} FROM "
        )


    def menuAttr(self, mGroup:int, mID:int, Opt:int, AttrName:str) -> Any:
        cond = f'MenuGroup_id={mGroup} AND MenuID={mID} AND OptionNumber={Opt}'
        self.setFilter(cond)
        return self.record(0).field(AttrName).value()
        # return self.mSource.filter(MenuGroup=mGroup,MenuID=mID,OptionNumber=Opt).first().values(AttrName)
        # return list(menuRec['values'][AttrName] \
        #                 for menuRec in self.mSource \
        #                 if menuRec['keys']['MenuGroup']==mGroup \
        #                     and menuRec['keys']['MenuID']==mID \
        #                     and menuRec['keys']['OptionNumber']==Opt \
        #     )[0]

    def dfltMenuID_forGroup(self, mGroup:int) -> int:
        cond = f'MenuGroup_id={mGroup} AND Argument LIKE "default" AND OptionNumber=0'
        self.setFilter(cond)
        retval = self.record(0).field('MenuID').value()
        # if self.filter(MenuGroup=mGroup,Argument__iexact='default',OptionNumber=0).exists():
        if not self.record(0).value('id'):
            tbl = self.tableName()
            grpFld = 'MenuGroup_id'
            cond = f'{grpFld}={mGroup}'
            minval = f'MIN(MenuID)'
            sqlWhere = f'OptionNumber=0'
            sqlStat = f'SELECT {minval} AS minval FROM {tbl}'
            sqlStat += f' WHERE {sqlWhere}'
            sqlStat += f' GROUP BY {grpFld}'
            sqlStat += f' HAVING {grpFld}={mGroup}'
            minfound = QSqlQueryModel()
            minfound.setQuery(sqlStat, cMenuDatabase)
            retval = minfound.record(0).value('minval')
        return retval
        # return list(menuRec['keys']['MenuID'] \
        #                 for menuRec in self.mSource \
        #                 if menuRec['keys']['MenuGroup']==mGroup \
        #                     and menuRec['keys']['OptionNumber']==0 \
        #                     and menuRec['values']['Argument'].lower() == 'default'\
        #     )[0]
    
    def dfltMenuGroup(self) -> int:
        sqlstmnt = f'SELECT MIN(MenuGroup_id) as dfltGroup FROM {self._tblName}'
        tmpQuery = QSqlQuery(sqlstmnt, self._db)
        tmpQuery.first()
        return tmpQuery.record().field('dfltGroup').value()
        # return self.aggregate(mGroup=Min('MenuGroup'))['mGroup']
    
    def menuDict(self, mGroup:int, mID:int) ->  Dict[int,Dict[str, Any]]:
        cond = f'MenuGroup_id={mGroup} AND MenuID={mID}'
        self.setFilter(cond)
        return { self.record(n).field('OptionNumber').value(): 
                    { self.record(n).fieldName(f): self.record(n).field(f).value() for f in range(self.columnCount())}
                for n in range(self.rowCount()) }
        # return { mRec['OptionNumber']: mRec for mRec in self.filter(MenuGroup=mGroup,MenuID=mID).values() }
        # return { mRec['keys']['OptionNumber']: mRec['values'] \
        #             for mRec in self.mSource \
        #             if mRec['keys']['MenuGroup']==mGroup \
        #                 and mRec['keys']['MenuID']==mID 
        #     }
    
    # def menuDBRecs(self, mGroup:int, mID:int) ->  QuerySet:
    def menuDBRecs(self, mGroup:int, mID:int) ->  Dict[int, QSqlRecord]:
        cond = f'MenuGroup_id={mGroup} AND MenuID={mID}'
        self.setFilter(cond)
        return { self.record(n).field('OptionNumber').value(): QSqlRecord(self.record(n)) 
                for n in range(self.rowCount()) }
        # return self.filter(MenuGroup=mGroup,MenuID=mID)
        # return { mRec['keys']['OptionNumber']: mRec['values'] \
        #             for mRec in self.mSource \
        #             if mRec['keys']['MenuGroup']==mGroup \
        #                 and mRec['keys']['MenuID']==mID 
        #     }
    
    def menuExist(self, mGroup:int, mID:int) ->  bool:
        sqlstmnt = f'SELECT 1 FROM {self._tblName} WHERE MenuGroup_id={mGroup} AND MenuID={mID} AND OptionNumber=0'
        tmpQuery = QSqlQuery(sqlstmnt, self._db)
        return tmpQuery.first()
        # return self.filter(MenuGroup=mGroup,MenuID=mID,OptionNumber=0).exists()
        # return any(list(True \
        #             for mRec in self.mSource \
        #             if mRec['keys']['MenuGroup']==mGroup \
        #                 and mRec['keys']['MenuID']==mID \
        #                 and mRec['keys']['OptionNumber']==0 \
        #     ))

    def newgroupnewmenuDict(self, mGroup:int, mID:int) ->  List[Dict]:
        return newgroupnewmenu_menulist
    def newmenuDict(self, mGroup:int, mID:int) ->  List[Dict]:
        return newmenu_menulist
    