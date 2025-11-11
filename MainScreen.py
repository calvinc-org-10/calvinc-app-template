# the Main Screen must be in a separate file because it has to be loaded AFTER django support

from PySide6.QtCore import (QCoreApplication, QMetaObject, )
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea )

from cMenu.cMenu import cMenu
from sysver import sysver, sysver_key, _appname


class MainScreen(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        if not self.objectName():
            self.setObjectName(u"MainWindow")
            
        theMenu = cMenu(parent)
        llayout = QVBoxLayout(self)
        llayout.addWidget(theMenu)
        
        self.setLayout(llayout)
        
        self.setWindowTitle(QCoreApplication.translate("MainWindow", _appname, None))

        # QMetaObject.connectSlotsByName(self)
    # __init__


