import sys
from PySide6.QtCore import QCoreApplication, Qt, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QApplication,
    QStackedWidget, QVBoxLayout, QWidget, )

from app.database import get_app_sessionmaker
from app_secrets import usr_auth_required
from calvincTools import calvincTools
# from calvincTools.cMenu import cMenu
# from calvincTools.usr_auth import LoginForm, current_user, set_current_user
from calvincTools.usr_auth.models import User_usrauth_not_used
from externalWebPageURL_Map import ExternalWebPageURL_Map
from menuformname_viewMap import FormNameToURL_Map
from sysver import (_appname, sysver, sysver_key, )


class MainScreen(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        if not self.objectName():
            self.setObjectName(u"MainWindow")

        pixsize=100
        cTools = calvincTools(
            app_sessionmaker=get_app_sessionmaker(),
            FormNameToURL_Map=FormNameToURL_Map,
            ExternalWebPageURL_Map=ExternalWebPageURL_Map,
            appname=_appname,
            logo=QPixmap("F:/calvincTools/calvincTools/assets/cTools.png").scaled(pixsize, pixsize, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation),
            appver=sysver[sysver_key],
            usr_auth=usr_auth_required,
            )

        # self.login_form = cTools.login_form()
        # self.login_form.login_successful.connect(self.go_to_menu)
        # self.menu_form = cTools.menu_form()
        # self.windowstack = cTools.main_window_stack()
        # self.windowstack.addWidget(self.login_form)
        # self.windowstack.addWidget(self.menu_form)

        llayout = QVBoxLayout(self)
        stack = cTools.main_window_stack()
        if stack is not None:
            llayout.addWidget(stack)
        self.setLayout(llayout)

        self.setWindowTitle(QCoreApplication.translate("MainWindow", _appname, None))

        cTools.login()
        
        # # login, if usr_auth is True
        # if usr_auth_required:
        #     self.go_to_login()
        # else:
        #     set_current_user(User_usrauth_not_used)  # set to dummy user since we're not using authentication
        #     self.go_to_menu()
        # endif usr_auth
    # __init__

    @Slot()
    # def go_to_menu(self):
    #     self.windowstack.setCurrentWidget(self.menu_form)
    #     cUsr = current_user()
    #     mGroup = cMenu._DFLT_menuGroup if cUsr is None else cUsr.menuGroup  # type: ignore
    #     self.menu_form.loadMenu(mGroup)    # type: ignore
    # # go_to_menu

    @Slot()
    # def go_to_login(self):
    #     if usr_auth_required:
    #         self.login_form.reset_fields()
    #         self.windowstack.setCurrentWidget(self.login_form)
    #     else:
    #         self.close()
    #         # should this be go_to_menu() instead? or should we just skip the login form entirely if usr_auth is False?
    #     # endif usr_auth
    # # go_to_login
# MainScreen
    def end_of_class(self):
        pass

########################################################
########################################################

if __name__ == "__main__":
    app = QApplication(sys.argv)

    topscreen = MainScreen()
    topscreen.show()

    sys.exit(app.exec())
