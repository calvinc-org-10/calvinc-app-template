# the Main Screen must be in a separate file because it has to be loaded AFTER django support

from PySide6.QtCore import (Qt, QCoreApplication, QMetaObject, Slot, )
from PySide6.QtGui import (QPixmap, )
from PySide6.QtWidgets import (QWidget, QStackedWidget, 
    QVBoxLayout, QScrollArea,
    )

from calvincTools.cMenu import cMenu
from calvincTools import calvincTools_init
from calvincTools.database import get_cMenu_sessionmaker
from calvincTools.usr_auth import (LoginForm, current_user)
from calvincTools.usr_auth.models import User, User_usrauth_not_used

from sysver import sysver, sysver_key, _appname

from menuformname_viewMap import FormNameToURL_Map
from externalWebPageURL_Map import ExternalWebPageURL_Map

from app.database import get_app_sessionmaker


class MainScreen(QWidget):
    current_user = None 
    
    def __init__(self, parent = None):
        super().__init__(parent)
        if not self.objectName():
            self.setObjectName(u"MainWindow")
        
        self.usr_auth=True
        
        calvincTools_init(
            usr_auth=False,     # to be deprecated
            app_sessionmaker=get_app_sessionmaker(),
            FormNameToURL_Map=FormNameToURL_Map,
            ExternalWebPageURL_Map=ExternalWebPageURL_Map,
            appname=_appname,
            appver=sysver[sysver_key],
            )

        pixsize=100
        self.login_form = LoginForm(
            formname=_appname + " Login",
            logo=QPixmap("F:/calvincTools/calvincTools/assets/cTools.png").scaled(pixsize, pixsize, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation),
            )
        self.login_form.login_successful.connect(self.go_to_menu)
        self.menu_form = cMenu(
            parent=None,
            # logo=logo,
            )
        self.windowstack = QStackedWidget(self)
        self.windowstack.addWidget(self.login_form)
        self.windowstack.addWidget(self.menu_form)

        llayout = QVBoxLayout(self)
        llayout.addWidget(self.windowstack)
        
        self.setLayout(llayout)
        
        self.setWindowTitle(QCoreApplication.translate("MainWindow", _appname, None))

        # login, if usr_auth is True
        if self.usr_auth:
            self.go_to_login()
        else:
            current_user = User_usrauth_not_used  # set to dummy user since we're not using authentication
            self.go_to_menu()
        # endif usr_auth
    # __init__

    @Slot()
    def go_to_menu(self):
        self.windowstack.setCurrentWidget(self.menu_form)
        mGroup = cMenu._DFLT_menuGroup if current_user is None else current_user.menuGroup  # type: ignore
        self.menu_form.loadMenu(mGroup)    # type: ignore
    # go_to_menu

    @Slot()
    def go_to_login(self):
        if self.usr_auth:
            self.login_form.reset_fields()
            self.windowstack.setCurrentWidget(self.login_form)
        else:
            self.close()
        # endif usr_auth
    # go_to_login
# MainScreen
