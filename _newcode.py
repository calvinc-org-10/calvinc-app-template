from typing import (Dict, List, Tuple, Mapping, Any, )
import copy

from PySide6.QtCore import (Qt, QObject,
    Signal, Slot, 
    )
from PySide6.QtGui import (QFont, QIcon, )
from PySide6.QtWidgets import ( 
    QLayout, QGridLayout, QBoxLayout, QHBoxLayout, QVBoxLayout, 
    QWidget, QFrame, 
    QLabel, QLCDNumber, QLineEdit, QTextEdit, QPlainTextEdit, QPushButton, QCheckBox, QComboBox, QDateEdit,
    QDialog, QMessageBox, QFileDialog, QDialogButtonBox,
    QRadioButton, QGroupBox, QButtonGroup, 
    )

from sqlalchemy import (select, ) 
from sqlalchemy.orm import make_transient

from cMenu.database import get_cMenu_session, get_cMenu_sessionmaker, Repository
from cMenu.dbmenulist import MenuRecords
from cMenu.models import (menuGroups, menuItems, 
    newgroupnewmenu_menulist, )
from cMenu.menucommand_constants import MENUCOMMANDS, COMMANDNUMBER
from cMenu.utils import (
    recordsetList, 
    cQFmConstants, 
    cComboBoxFromDict, cstdTabWidget, cGridWidget,
    cQFmFldWidg, cSimpleRecordForm, cSimpleRecordForm_Base,
    pleaseWriteMe, areYouSure, 
    )


# copied from cMenu - if you change it here, change it there
_NUM_menuBUTTONS:int = 20
_NUM_menuBUTNCOLS:int = 2
_NUM_menuBTNperCOL: int = int(_NUM_menuBUTTONS/_NUM_menuBUTNCOLS)

Nochoice = {'---': None}    # only needed for combo boxes, not datalists


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# temporary for testing - remove once finished
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
