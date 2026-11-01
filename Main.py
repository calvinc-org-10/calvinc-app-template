import sys
from PySide6.QtCore import QCoreApplication, Qt, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QApplication,
    QStackedWidget, QVBoxLayout, QWidget, )

from database import get_app_sessionmaker
import app_secrets
from calvincTools import calvincTools, CallerContext
# from calvincTools.cMenu import cMenu
# from calvincTools.usr_auth import LoginForm, current_user, set_current_user
from calvincTools.usr_auth.models import User_usrauth_not_used
from externalWebPageURL_Map import ExternalWebPageURL_Map
from menuformname_viewMap import FormNameToURL_Map
from config import config
from sysver import (_appname, sysver, sysver_key, )


class MainScreen(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        if not self.objectName():
            self.setObjectName(u"MainWindow")

        Qapp = QApplication.instance() or QApplication(sys.argv)
        # create the app logo after class creation
        # done here because the QApplication instance needs to exist before creating the QPixmap for the logo
        from config import Config
        Config.APP_LOGO = Config.init_app_logo()

        appConfig = config.get(app_secrets.config_to_use, None)
        appContext: CallerContext = CallerContext(
            Qapp=Qapp,
            config=appConfig,
            app_ssnmaker=get_app_sessionmaker(),
            cTools_bind_key=None,
            cTools_tablenames = None,
            cTools_models = None
        )
        
        cTools = calvincTools(
            caller_context=appContext,
            )

        llayout = QVBoxLayout(self)
        stack = cTools.main_window_stack()
        if stack is not None:
            llayout.addWidget(stack)
        self.setLayout(llayout)

        self.setWindowTitle(QCoreApplication.translate("MainWindow", _appname, None))

        cTools.login()
        
    # __init__
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

