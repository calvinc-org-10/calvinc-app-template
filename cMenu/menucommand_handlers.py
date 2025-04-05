from typing import (Dict, List, Tuple, Any, )

from PySide6.QtCore import (Qt, QObject,
    Signal, Slot, 
    QAbstractTableModel, QModelIndex, )
from PySide6.QtSql import (QSqlRecord, QSqlQuery, QSqlQueryModel, )
from PySide6.QtGui import (QFont, QIcon, )
from PySide6.QtWidgets import ( QStyle, 
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QFormLayout, QFrame, 
    QTableView, QHeaderView,
    QDialog, QMessageBox, QFileDialog, QDialogButtonBox,
    QLabel, QLCDNumber, QLineEdit, QTextEdit, QPlainTextEdit, QPushButton, QCheckBox, QComboBox, 
    QRadioButton, QGroupBox, QButtonGroup, 
    QSizePolicy, 
    )

# there's no need to import cMenu, plus it's a circular ref - cMenu depends heavily on this module
# from .kls_cMenu import cMenu 

from menuformname_viewMap import FormNameToURL_Map

from .database import cMenuDatabase
from .dbmenulist import (MenuRecords, newgroupnewmenu_menulist, newmenu_menulist, )
from sysver import sysver
from .menucommand_constants import MENUCOMMANDS, COMMANDNUMBER
from .models import (menuItems, menuGroups, )
from .utils import (cComboBoxFromDict, cQFmFldWidg, cQFmNameLabel, QRawSQLTableModel, cQFmNameLabel,
    cQSqlTableModel, cQSqlRelationalTableModel, 
    UnderConstruction_Dialog, areYouSure,
    Excelfile_fromqs, ExcelWorkbook_fileext,
    pleaseWriteMe,  
    )


# copied from cMenu - if you change it here, change it there
_NUM_menuBUTTONS:int = 20
_NUM_menuBUTNCOLS:int = 2
_NUM_menuBTNperCOL: int = int(_NUM_menuBUTTONS/_NUM_menuBUTNCOLS)

Nochoice = {'---': None}    # only needed for combo boxes, not datalists

# fontFormTitle = QFont()
# fontFormTitle.setFamilies([u"Copperplate Gothic"])
# fontFormTitle.setPointSize(24)


def FormBrowse(parntWind, formname, *args, **kwargs):
    urlIndex = 0
    viewIndex = 1

    # theForm = 'Form ' + formname + ' is not built yet.  Calvin needs more coffee.'
    theForm = None
    # formname = formname.lower()
    if formname in FormNameToURL_Map:
        if FormNameToURL_Map[formname][urlIndex]:
            # figure out how to repurpose this later
            # url = FormNameToURL_Map[formname][urlIndex]
            # try:
            #     theView = resolve(reverse(url)).func
            #     urlExists = True
            # except (Resolver404, NoReverseMatch):
            #     urlExists = False
            # # end try
            # if urlExists:
            #     theForm = theView(req)
            # else:
            #     formname = f'{formname} exists but url {url} '
            # #endif
            pass
        elif FormNameToURL_Map[formname][viewIndex]:
            try:
                fn = FormNameToURL_Map[formname][viewIndex]
                viewExists = True
            except NameError:
                viewExists = False
            #end try
            if viewExists:
                # dtheForm = fn(parntWind)
                theForm = fn(*args, **kwargs)
            else:  
                formname = f'{formname} exists but view {FormNameToURL_Map[formname][viewIndex]}'
            #endif
    if not theForm:
        formname = f'Form {formname} is not built yet.  Calvin needs more coffee.'
        # print(formname)
        UnderConstruction_Dialog(parntWind, formname).show()
    else:
        # print(f'about to show {theForm}')
        # theForm.show()
        # print(f'done showing')
        return theForm
    # endif

    # must be rendered if theForm came from a class-based-view
    # if hasattr(theForm,'render'): theForm = theForm.render()
    # return theForm

def ShowTable(parntWind, tblname):
    # showing a table is nothing more than another form
    return FormBrowse(parntWind,tblname)

#####################################################
#####################################################

class QWGetSQL(QWidget):
    runSQL = Signal(str)    # Emitted with the SQL string when run is clicked
    cancel = Signal()       # Emitted when cancel is clicked    
    
    def __init__(self, parent = None):
        super().__init__(parent)

        font = QFont()
        font.setPointSize(12)
        self.setFont(font)
        
        self.layoutForm = QVBoxLayout(self)
        
        # Form Header Layout
        self.layoutFormHdr = QVBoxLayout()
        
        self.lblFormName = cQFmNameLabel()
        self.lblFormName.setText(self.tr('Enter SQL'))
        self.setWindowTitle(self.tr('Enter SQL'))
        self.layoutFormHdr.addWidget(self.lblFormName)
        self.layoutFormHdr.addSpacing(20)
        
        # main area for entering SQL
        self.layoutFormMain = QFormLayout()
        self.txtedSQL = QTextEdit()
        self.layoutFormMain.addRow(self.tr('SQL statement'), self.txtedSQL)
        
        # run/Cancel buttons
        self.layoutFormActionButtons = QHBoxLayout()
        self.buttonRunSQL = QPushButton( QIcon.fromTheme(QIcon.ThemeIcon.Computer), self.tr('Run SQL') ) 
        self.buttonRunSQL.clicked.connect(self._on_run_sql_clicked)
        self.layoutFormActionButtons.addWidget(self.buttonRunSQL, alignment=Qt.AlignmentFlag.AlignRight)
        self.buttonCancel = QPushButton( QIcon.fromTheme(QIcon.ThemeIcon.WindowClose), self.tr('Cancel') ) 
        self.buttonCancel.clicked.connect(self._on_cancel_clicked)
        self.layoutFormActionButtons.addWidget(self.buttonCancel, alignment=Qt.AlignmentFlag.AlignRight)
        
        # generic horizontal lines
        horzline = QFrame()
        horzline.setFrameShape(QFrame.Shape.HLine)
        horzline.setFrameShadow(QFrame.Shadow.Sunken)
        horzline2 = QFrame()
        horzline2.setFrameShape(QFrame.Shape.HLine)
        horzline2.setFrameShadow(QFrame.Shadow.Sunken)
        
        # status message
        self.lblStatusMsg = QLabel()
        self.lblStatusMsg.setText('\n\n')
        
        # Hints
        self.lblHints = QPlainTextEdit()
        self.lblHints.setReadOnly(True)
        txtHints = 'PRAGMA table_list;'
        txtHints += '\nPRAGMA table_xinfo(tablname);'
        self.lblHints.setPlainText(txtHints)
        
        self.layoutForm.addLayout(self.layoutFormHdr)
        self.layoutForm.addLayout(self.layoutFormMain)
        self.layoutForm.addLayout(self.layoutFormActionButtons)
        self.layoutForm.addWidget(horzline)
        self.layoutForm.addWidget(self.lblStatusMsg)
        self.layoutForm.addWidget(horzline2)
        self.layoutForm.addWidget(self.lblHints)
        
    def _on_run_sql_clicked(self):
        # Emit the runSQL signal with the text from the editor.
        sql_text = self.txtedSQL.toPlainText()
        self.runSQL.emit(sql_text)

    def _on_cancel_clicked(self):
        # Emit the cancel signal.
        self.cancel.emit()        

    def closeEvent(self, event):
        self.cancel.emit()  # Emit the signal
        event.accept()  # Accept the close event (allows the window to close)

class QWShowSQL(QWidget):
    ReturnToSQL = Signal()
    closeMe = Signal()
    closeBoth = Signal()
    
    def __init__(self, qmodel:QSqlQueryModel, parent:QWidget = None):
        super().__init__(parent)

        # save incoming for future use if needed
        origSQL = qmodel.query().lastQuery()
        # rowCount will not return true count if not all rows fetched
        while qmodel.canFetchMore():
            qmodel.fetchMore()
        numrows = qmodel.rowCount()
        colNames = [qmodel.headerData(x,Qt.Orientation.Horizontal) for x in range(qmodel.columnCount())]

        font = QFont()
        font.setPointSize(12)
        self.setFont(font)
        
        self.layoutForm = QVBoxLayout(self)
        
        # Form Header Layout
        self.layoutFormHdr = QVBoxLayout()
        
        self.lblFormName = cQFmNameLabel()
        self.lblFormName.setText(self.tr('SQL Results'))
        self.setWindowTitle(self.tr('SQL Results'))
        self.layoutFormHdr.addWidget(self.lblFormName)
        
        self.layoutFormSQLDescription = QFormLayout()
        lblOrigSQL = QLabel()
        lblOrigSQL.setText(origSQL)
        lblnRecs = QLabel()
        lblnRecs.setText(f'{numrows}')
        lblcolNames = QLabel()
        lblcolNames.setText(str(colNames))
        self.layoutFormSQLDescription.addRow('SQL Entered:', lblOrigSQL)
        self.layoutFormSQLDescription.addRow('rows affctd:', lblnRecs)
        self.layoutFormSQLDescription.addRow('cols:', lblcolNames)
        

        # main area for displaying SQL
        self.layoutFormMain = QVBoxLayout()
        
        resultTable = QTableView()
        # resultTable.verticalHeader().setHidden(True)
        header = resultTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        # Apply stylesheet to control text wrapping
        resultTable.setStyleSheet("""
        QHeaderView::section {
            padding: 5px;
            font-size: 12px;
            text-align: center;
            white-space: normal;  /* Allow text to wrap */
        }
        """)
        resultTable.setModel(qmodel)
        self.layoutFormMain.addWidget(resultTable)
        
        #  buttons
        self.layoutFormActionButtons = QHBoxLayout()
        self.buttonGetSQL = QPushButton( QIcon.fromTheme(QIcon.ThemeIcon.GoPrevious), self.tr('Back to SQL') ) 
        self.buttonGetSQL.clicked.connect(self._return_to_sql)
        self.layoutFormActionButtons.addWidget(self.buttonGetSQL, alignment=Qt.AlignmentFlag.AlignRight)
        self.buttonDLResults = QPushButton( QIcon.fromTheme(QIcon.ThemeIcon.DocumentSave), self.tr('D/L Results') ) 
        self.buttonDLResults.clicked.connect(self.DLResults)
        self.layoutFormActionButtons.addWidget(self.buttonDLResults, alignment=Qt.AlignmentFlag.AlignRight)
        self.buttonCancel = QPushButton( QIcon.fromTheme(QIcon.ThemeIcon.WindowClose), self.tr('Close') ) 
        self.buttonCancel.clicked.connect(self._on_cancel_clicked)
        self.layoutFormActionButtons.addWidget(self.buttonCancel, alignment=Qt.AlignmentFlag.AlignRight)
        
        # generic horizontal lines
        horzline = QFrame()
        horzline.setFrameShape(QFrame.Shape.HLine)
        horzline.setFrameShadow(QFrame.Shadow.Sunken)
        
        self.layoutForm.addLayout(self.layoutFormHdr)
        self.layoutForm.addLayout(self.layoutFormSQLDescription)
        self.layoutForm.addLayout(self.layoutFormMain)
        self.layoutForm.addWidget(horzline)
        self.layoutForm.addLayout(self.layoutFormActionButtons)
        
        colfctr = 90
        self.setMinimumWidth(colfctr*len(colNames))
        
    @Slot()
    def DLResults(self):
        ExcelFileNamePrefix = "SQLresults"
        # Excel_qdict = [{self.colNames[x]:cRec[x] for x in range(len(self.colNames))} for cRec in self.rows]
        Excel_qdict = self.rows
        xlws = Excelfile_fromqs(Excel_qdict)
        filName, _ = QFileDialog.getSaveFileName(self, 
            caption="Enter Spreadsheet File Name",
            filter=f'{ExcelFileNamePrefix}*{ExcelWorkbook_fileext}',
            selectedFilter=f'*{ExcelWorkbook_fileext}'
        )
        if filName:
            xlws.save(filName)     
        
    def _return_to_sql(self):
        self.ReturnToSQL.emit()

    def _on_cancel_clicked(self):
        # Emit the cancel signal.
        self.closeBoth.emit()        

    def closeEvent(self, event):
        self.closeMe.emit()  # Emit the signal
        event.accept()  # Accept the close event (allows the window to close)
    
class cMRunSQL(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.inputSQL:str = None
        self.qmodel:QSqlQueryModel = None
        self.colNames:str|List[str] = None
        self.wndwAlive:Dict[str,bool] = {}
        
        self.wndwGetSQL = QWGetSQL(parent)
        self.wndwGetSQL.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.wndwGetSQL.runSQL.connect(self.rawSQLexec)
        self.wndwGetSQL.cancel.connect(self._on_cancel)
        self.wndwAlive['Get'] = True
        self.wndwGetSQL.destroyed.connect(lambda: self.wndwDest('Get'))
        
        self.wndwShowSQL = None        # will be redefined later

    def wndwDest(self, whichone:str):
        self.wndwAlive[whichone] = False
        
    def show(self):
        self.wndwGetSQL.show()
        
    @Slot(str)
    def rawSQLexec(self, inputSQL:str):
        self.qmodel = QSqlQueryModel()
        self.qmodel.setQuery(inputSQL, appDatabase)
        
        if self.qmodel.lastError().isValid():
            print(self.qmodel.lastError())
            self.wndwGetSQL.lblStatusMsg.setText(f'ERROR: {self.qmodel.lastError()}')
        else:
            self.rawSQLshow()
            
        # old code        
        # sqlerr = None
        # with db.connection.cursor() as djngocursor:
        #     try:
        #         djngocursor.execute(inputSQL)
        #     except Exception as err:
        #         sqlerr = err
        #     if not sqlerr:
        #         colNames = []
        #         if djngocursor.description:
        #             colNames = [col[0] for col in djngocursor.description]
        #             rows = dictfetchall(djngocursor)
        #         else:
        #             colNames = 'NO RECORDS RETURNED; ' + str(djngocursor.rowcount) + ' records affected'
        #             rows = []
        #         #endif cursor.description

        #         self.inputSQL = inputSQL        # preserve for later use
        #         self.rows = rows                # preserve for later use
        #         self.colNames = colNames        # preserve for later use
        #         self.rawSQLshow()
        #     else:  
        #         # show sqlerr in self.wndwGetSQL
        #         self.wndwGetSQL.lblStatusMsg.setText(f'ERROR: {sqlerr}')
        #         # self.wndwGetSQL.repaint()
        #     #endif not sqlerr
        # #end with

    def rawSQLshow(self):
        self.wndwShowSQL = QWShowSQL(self.qmodel, self.parent())
        self.wndwShowSQL.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.wndwShowSQL.ReturnToSQL.connect(self._ShowToGetSQL)
        self.wndwShowSQL.closeBoth.connect(self._on_cancel)

        self.wndwAlive['Show'] = True
        self.wndwShowSQL.destroyed.connect(lambda: self.wndwDest('Show'))


        self.wndwGetSQL.hide()
        self.wndwShowSQL.show()

    @Slot()
    def _ShowToGetSQL(self):
        if self.wndwAlive.get('Show'):
            self.wndwShowSQL.close()
        self.wndwGetSQL.show()
        
    @Slot()
    def _on_cancel(self):
        # Handle the cancellation by closing both windows.
        self._close_all()

    def _close_all(self):
        # Close the child widget if it exists.
        if self.wndwAlive.get('Get'):
            self.wndwGetSQL.close()
        if self.wndwAlive.get('Show'):
            self.wndwShowSQL.close()
        # Close this widget (cMRunSQL) as well.
        self.close()

#############################################
#############################################
#############################################

class cWidgetMenuItem(QWidget):
    _db = cMenuDatabase
    _menuItemstblName = 'cMenu_menuitems'
    _menuGrouptblName = 'cMenu_menugroups'
    formFields:Dict[str, QWidget] = {}

    requestMenuReload:Signal = Signal()
    
    class cEdtMnuItmDlg_CopyMove_MenuItm(QDialog):
        intCMChoiceCopy:int = 10
        intCMChoiceMove:int = 20
        
        def __init__(self, menuGrp:int, menuID:int, optionNumber:int, parent:QWidget = None):
            super().__init__(parent)
            
            self.setWindowModality(Qt.WindowModality.WindowModal)
            self.setWindowTitle(parent.windowTitle() if parent else 'Copy/Move Menu Item')

            self.dlgButtons:QDialogButtonBox = None # to be defined later, but must exist now

            lblDlgTitle = QLabel(self.tr(f' Copy or Move Menu Item {menuID}, {optionNumber}'))

            ##################################################
            # set up menuGroup, menuID, menuOption comboboxes
            layoutNewItemID = QGridLayout()

            lblMenuGroupID = QLabel(self.tr('Menu Group'))
            self.combobxMenuGroupID = cComboBoxFromDict(self.dictmenuGroup(), parent=self)
            self.combobxMenuGroupID.activated.connect(self.loadMenuIDs)

            lblMenuID = QLabel(self.tr('Menu'))
            self.combobxMenuID = cComboBoxFromDict(self.dictmenus(menuGrp), parent=self)
            # self.loadMenuIDs(menuGrp) - not necessary - done with initialization
            self.combobxMenuID.activated.connect(self.loadMenuOptions)

            lblMenuOption = QLabel(self.tr('Option'))
            self.combobxMenuOption = cComboBoxFromDict({}, parent=self)
            self.combobxMenuOption.activated.connect(self.menuOptionChosen)

            layoutNewItemID.addWidget(lblMenuGroupID,0,0)
            layoutNewItemID.addWidget(self.combobxMenuGroupID,1,0)
            layoutNewItemID.addWidget(lblMenuID,0,1)
            layoutNewItemID.addWidget(self.combobxMenuID,1,1)
            layoutNewItemID.addWidget(lblMenuOption,0,2)
            layoutNewItemID.addWidget(self.combobxMenuOption,1,2)

            self.combobxMenuGroupID.setCurrentIndex(self.combobxMenuGroupID.findData(menuGrp))
            self.loadMenuIDs(menuGrp)
            ##################################################            
            
            visualgrpboxCopyMove = QGroupBox(self.tr("Copy / Move"))
            layoutgrpCopyMove = QHBoxLayout()
            # Create radio buttons
            radioCopy = QRadioButton(self.tr("Copy"))
            radioMove = QRadioButton(self.tr("Move"))
            # Add radio buttons to the layout
            layoutgrpCopyMove.addWidget(radioCopy)
            layoutgrpCopyMove.addWidget(radioMove)
            visualgrpboxCopyMove.setLayout(layoutgrpCopyMove)
            # Create a QButtonGroup for logical grouping
            self.lgclbtngrpCopyMove = QButtonGroup()
            self.lgclbtngrpCopyMove.addButton(radioCopy, id=self.intCMChoiceCopy)
            self.lgclbtngrpCopyMove.addButton(radioMove, id=self.intCMChoiceMove)
            # Add the QGroupBox to the main layout

            self.dlgButtons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel,
                Qt.Orientation.Horizontal,
                )
            self.dlgButtons.accepted.connect(self.accept)
            self.dlgButtons.rejected.connect(self.reject)            
            self.dlgButtons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

            layoutMine = QVBoxLayout()
            layoutMine.addWidget(lblDlgTitle)
            layoutMine.addWidget(visualgrpboxCopyMove)
            layoutMine.addLayout(layoutNewItemID)
            layoutMine.addWidget(self.dlgButtons)
            
            self.setLayout(layoutMine)

        def dictmenuGroup(self) -> Dict[str, int]:
            rs = menuGroups().recordsetList(['id', 'GroupName'])
            retDict = {d['GroupName']:d['id'] for d in rs}
            return retDict
        def dictmenus(self, mnuGrp:int) -> Dict[str, int]:
            tbl = menuItems()
            # tbl = MenuRecords()
            tbl.setFilter(f'MenuGroup_id = {mnuGrp} AND OptionNumber = 0')
            rs = tbl.recordsetList(['MenuID', 'OptionText'])
            retDict = Nochoice | {d['OptionText']:d['MenuID'] for d in rs}
            return retDict
        def dictmenuOptions(self, mnuID:int) -> List[int]:
            mnuGrp:int = self.combobxMenuGroupID.currentData()
            tbl = menuItems()
            # tbl = MenuRecords()
            tbl.setFilter(f'MenuGroup_id={mnuGrp} AND MenuID={mnuID}')
            # .values_list('OptionNumber', flat=True)
            definedOptions = [rec['OptionNumber'] for rec in tbl.recordsetList(['OptionNumber'])]
            return Nochoice | { str(n+1): n+1 for n in range(_NUM_menuBUTTONS) if n+1 not in definedOptions }

        @Slot()
        def loadMenuIDs(self, idx:int):
            mnuGrp:int = self.combobxMenuGroupID.currentData()
            # if self.combobxMenuGroupID.currentIndex() != -1:
            if mnuGrp is not None:
                self.combobxMenuID.replaceDict(self.dictmenus(mnuGrp))
            self.combobxMenuID.setCurrentIndex(-1)
            self.combobxMenuOption.clear()
            self.enableOKButton()
        @Slot()
        def loadMenuOptions(self, idx:int):
            mnuID:int = self.combobxMenuID.currentData()
            #if self.combobxMenuID.currentIndex() != -1:
            if mnuID is not None:
                self.combobxMenuOption.replaceDict(self.dictmenuOptions(mnuID))
            self.combobxMenuOption.setCurrentIndex(-1)
            self.enableOKButton()
        @Slot()
        def menuOptionChosen(self, idx:int):
            self.enableOKButton()
        def enableOKButton(self):
            if not self.dlgButtons:
                return
            all_GrpIdOption_chosen = all([
                self.combobxMenuGroupID.currentIndex() != -1,
                self.combobxMenuID.currentIndex() != -1,
                self.combobxMenuOption.currentIndex() != -1,
            ])
            self.dlgButtons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(all_GrpIdOption_chosen)
        
        def exec(self):
            ret = super().exec()
            copymove = self.lgclbtngrpCopyMove.checkedId()
            chosenMenuGroup = self.combobxMenuGroupID.currentData()
            chosenMenuID = self.combobxMenuID.currentData()
            chosenMenuOption = self.combobxMenuOption.currentData()
            return (
                ret, 
                copymove != self.intCMChoiceMove,   # True unless Move checked
                # return (Group, Menu, OptrNum) tuple
                (chosenMenuGroup, chosenMenuID, chosenMenuOption),
                )
    
    def __init__(self, menuitmRec:QSqlRecord, parent:QWidget = None):
        super().__init__(parent)
        
        self.setObjectName('cWidgetMenuItem')
        
        self.currRec = menuitmRec
        
        font = QFont()
        font.setPointSize(7)
        self.setFont(font)

        self.layoutFormMain = QHBoxLayout(self)
        self.layoutFormMain.setContentsMargins(0,0,0,0)
        self.layoutFormMain.setSpacing(0)
        
        self.layoutFormMainLeft = QVBoxLayout()
        self.layoutFormMainLeft.setContentsMargins(0,0,0,0)
        self.layoutFormMainLeft.setSpacing(0)

        ##
        self.layoutFormLine1 = QHBoxLayout()
        self.layoutFormLine1.setContentsMargins(0,0,0,0)
        self.layoutFormLine1.setSpacing(0)
        
        # self.lnedtOptionNumber = QLineEdit(self)
        modlFld='OptionNumber'
        wdgt = cQFmFldWidg(QLineEdit,
            lblText='Option Number', modlFld=modlFld, parent=self)
        self.formFields[modlFld] = wdgt
        self.lnedtOptionNumber = wdgt
        # self.lnedtOptionNumber.setProperty('modelField', 'OptionNumber')
        # self.lnedtOptionNumber.setValue = self.lnedtOptionNumber.setText
        wdgt._wdgt.setProperty('noedit', True)
        wdgt._wdgt.setReadOnly(True)
        wdgt._wdgt.setFrame(False)
        wdgt._wdgt.setMaximumWidth(25)
        wdgt._wdgt.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        modlFld='OptionText'
        wdgt = cQFmFldWidg(QLineEdit, lblText='OptionText: ', modlFld=modlFld, parent=self)
        self.formFields[modlFld] = wdgt
        self.fldOptionText = wdgt
        wdgt.signalFldChanged.connect(lambda: self.changeField(self.fldOptionText))

        modlFld='TopLine'
        wdgt = cQFmFldWidg(QCheckBox, lblText='Top Line', lblChkBxYesNo={True:'YES', False:'NO'}, 
                modlFld=modlFld, parent=self)
        self.formFields[modlFld] = wdgt
        self.fldMenuItemTopLine = wdgt
        wdgt.signalFldChanged.connect(lambda newstate: self.changeField(self.fldMenuItemTopLine))

        modlFld='BottomLine'
        wdgt = cQFmFldWidg(QCheckBox, lblText='Btm Line', lblChkBxYesNo={True:'YES', False:'NO'}, 
                modlFld=modlFld, parent=self)
        self.formFields[modlFld] = wdgt
        self.fldMenuItemBottomLine = wdgt
        wdgt.signalFldChanged.connect(lambda newstate: self.changeField(self.fldMenuItemBottomLine))

        # self.layoutFormLine1.addWidget(self.lblOptionNumber)
        self.layoutFormLine1.addWidget(self.lnedtOptionNumber)
        self.layoutFormLine1.addWidget(self.fldOptionText)
        self.layoutFormLine1.addWidget(self.fldMenuItemTopLine)
        self.layoutFormLine1.addWidget(self.fldMenuItemBottomLine)

        ##

        self.layoutFormLine2 = QHBoxLayout()
        self.layoutFormLine2.setContentsMargins(0,0,0,0)
        self.layoutFormLine2.setSpacing(0)

        modlFld='Command'
        wdgt = cQFmFldWidg(cComboBoxFromDict, lblText='Command:', modlFld=modlFld, 
            choices=vars(COMMANDNUMBER), parent=self)
        self.formFields[modlFld] = wdgt
        self.fldCommand = wdgt
        wdgt.signalFldChanged.connect(lambda x: self.changeField(self.fldCommand))

        modlFld='Argument'
        wdgt = cQFmFldWidg(QLineEdit, lblText='Argument: ', modlFld=modlFld, parent=self)
        self.formFields[modlFld] = wdgt
        self.fldArgument = wdgt
        wdgt.signalFldChanged.connect(lambda: self.changeField(self.fldArgument))

        modlFld='PWord'
        wdgt = cQFmFldWidg(QLineEdit, lblText='Password: ', modlFld='PWord', parent=self)
        self.formFields[modlFld] = wdgt
        self.fldPWord = wdgt
        wdgt.signalFldChanged.connect(lambda: self.changeField(self.fldPWord))

        self.layoutFormLine2.addWidget(self.fldCommand)
        self.layoutFormLine2.addWidget(self.fldArgument)
        self.layoutFormLine2.addWidget(self.fldPWord)

        self.layoutFormMainLeft.addLayout(self.layoutFormLine1)
        self.layoutFormMainLeft.addLayout(self.layoutFormLine2)
        ##
        
        self.layoutFormMainRight = QVBoxLayout()
        self.layoutFormMainRight.setContentsMargins(0,0,0,0)
        self.layoutFormMainRight.setSpacing(0)

        self.btnCommit = QPushButton(self.tr('Save\nChanges'), self)
        self.btnCommit.clicked.connect(self.writeRecord)
        # self.btnCommit.setFixedSize(60, 30)  # Adjust width and height
        self.btnCommit.setStyleSheet("padding: 2px; margin: 0;")  # Remove extra padding

        self.btnMoveCopy = QPushButton(self.tr('Copy / Move'), self)
        self.btnMoveCopy.clicked.connect(self.copyMenuOption)
        # self.btnMoveCopy.setFixedSize(60, 30)  # Adjust width and height
        self.btnMoveCopy.setStyleSheet("padding: 2px; margin: 0;")  # Remove extra padding

        self.btnRemove = QPushButton(self.tr('Remove'), self)
        self.btnRemove.clicked.connect(self.rmvMenuOption)
        # self.btnRemove.setFixedSize(60, 30)  # Adjust width and height
        self.btnRemove.setStyleSheet("padding: 2px; margin: 0;")  # Remove extra padding

        self.layoutFormMainRight.addWidget(self.btnMoveCopy)
        self.layoutFormMainRight.addWidget(self.btnRemove)
        self.layoutFormMainRight.addWidget(self.btnCommit)

        # # minimize sizing
        # for widget in [self.lnedtOptionNumber, self.fldOptionText, self.fldMenuItemTopLine, 
        #             self.fldMenuItemBottomLine, self.fldCommand, self.fldArgument, self.fldPWord, self.btnCommit]:
        #     widget.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        # self.lnedtOptionNumber._wdgt.setFixedHeight(20)  # Adjust height to minimize space
        # self.fldOptionText._wdgt.setFixedHeight(20)
        # self.fldArgument._wdgt.setFixedHeight(20)
        # self.fldPWord._wdgt.setFixedHeight(20)

        self.layoutFormMain.addLayout(self.layoutFormMainLeft)
        self.layoutFormMain.addLayout(self.layoutFormMainRight)
        
        self.fillFormFromcurrRec()

    # __init__

    ##########################################
    ########    Create

    # this widget doesn't create new records

    ##########################################
    ########    Read

    def fillFormFromcurrRec(self):
        cRec:QSqlRecord = self.currRec
    
        # move to class var?
        forgnKeys = {
            'id': cRec.value('id') if cRec else '',
            'MenuGroup': cRec.value('MenuGroup_id') if cRec else '',
            }
        # move to class var?
        valu_transform_flds = {
        }
        # for field in cRec._meta.get_fields():
        for n in range(cRec.count()):
            fieldname = cRec.fieldName(n)
            field_value = cRec.value(fieldname)
            field_valueStr = str(field_value)
            if fieldname in forgnKeys:
                field_valueStr = str(forgnKeys[fieldname])
            if fieldname in valu_transform_flds:
                field_valueStr = valu_transform_flds[fieldname][0](field_value)
            
            if fieldname in self.formFields:
                wdgt = self.formFields[fieldname]
                wdgt.setValue(field_valueStr)
            #endif field.name in self.formFields
        #endfor field in cRec
        
        # fix this later ...
        
        self.btnMoveCopy.setEnabled(cRec.value('id') is not None)
        self.btnRemove.setEnabled(cRec.value('id') is not None)
        
        self.setFormDirty(self, False)
    # fillFormFromRec


    ##########################################
    ########    Update

    @Slot()
    def changeField(self, wdgt:cQFmFldWidg) -> bool:
        # move to class var?
        forgnKeys = {   
            'MenuGroup',
            }
        # move to class var?
        valu_transform_flds = {
        }
        cRec:QSqlRecord = self.currRec
        dbField = wdgt.modelField()

        wdgt_value = wdgt.Value()

        if dbField in forgnKeys:
            dbField += '_id'
        if dbField in valu_transform_flds:
            wdgt_value = valu_transform_flds[dbField][1](wdgt_value)

        if wdgt_value or isinstance(wdgt_value,bool):
            cRec.setValue(dbField, wdgt_value)
            self.setFormDirty(wdgt, True)

            return True
        else:
            return False
        # endif wdgt_value
    # changeField
    
    @Slot()
    def writeRecord(self):
        if not self.isFormDirty():
            return
        
        cRec:QSqlRecord = self.currRec
        dbTbl = menuItems()
        pkTblName = f'{dbTbl.primaryKey().field(0).tableName()}'
        pkFldName = f'{dbTbl.primaryKey().field(0).name()}'
        pkFullName = f'{pkTblName}.{pkFldName}'
        pk = cRec.value(pkFldName)
        
        if pk:
            dbTbl.setFilter(f'{pkFullName}={pk}')
            dbTbl.select()
            for row in range(dbTbl.rowCount()): # row should be 0
                if dbTbl.record(row).value(pkFldName) == pk:
                    dbTbl.setRecord(row, cRec)
                    break
            #endfor
        else:
            # force values on flds with NOT NULL constraint
            notnullFlds = {
                # "MenuID" really should have a value
                # "OptionNumber" should have a value or else something's SERIOUSLY wrong
                "OptionText" : "", 
                "Argument" : "", 
                "PWord" : "", 
            }
            for fldName, replVal in notnullFlds.items():
                if not cRec.value(fldName):
                    cRec.setValue(fldName, replVal)
            dbTbl.select()
            row = dbTbl.rowCount()
            dbTbl.insertRecord(row,cRec)
        #endif pk

        if not dbTbl.submitAll():
            print("Failed to submit changes:", dbTbl.lastError().text())
        
        # reread record
        mGrp, mID, Opt = (cRec.value('MenuGroup_id'), cRec.value('MenuID'), cRec.value('OptionNumber'))
        dbTbl.setFilter(f'MenuGroup_id={mGrp} AND MenuID={mID} AND OptionNumber={Opt}')
        dbTbl.select()
        cRec = dbTbl.record(0)
        
        pk = cRec.value(pkFldName)
                    
        self.btnMoveCopy.setEnabled(pk is not None)
        self.btnRemove.setEnabled(pk is not None)
        
        self.setFormDirty(self, False)
    # writeRecord


    ##########################################
    ########    Delete

    def rmvMenuOption(self):
        cRec = self.currRec
        mGrp, mnu, mOpt = (cRec.value('MenuGroup_id'), cRec.value('MenuID'), cRec.value('OptionNumber'))
        # verify delete
        
        really = areYouSure(self, 
            title="Remove Menu Option?",
            areYouSureQuestion=f'Really remove menu option {mGrp}, {mnu}, {mOpt} ({cRec.value('OptionText')}) ?'
            )
        
        if really != QMessageBox.StandardButton.Yes:
            return
        
        # remove from db
        # if self.currRec.pk:
        #     self.currRec.delete()
        dbTbl = menuItems()
        pkTblName = f'{dbTbl.primaryKey().field(0).tableName()}'
        pkFldName = f'{dbTbl.primaryKey().field(0).name()}'
        pkFullName = f'{pkTblName}.{pkFldName}'
        pk = cRec.value(pkFldName)
        
        if pk:
            dbTbl.setFilter(f'{pkFullName}={pk}')
            dbTbl.select()
            for row in range(dbTbl.rowCount()): # row should be 0
                if dbTbl.record(row).value(pkFldName) == pk:
                    dbTbl.removeRow(row)
                    break
            #endfor
        #endif pk

        if not dbTbl.submitAll():
            print("Failed to submit changes:", dbTbl.lastError().text())
            
        self.makeCurrecEmpty(mGrp, mnu, mOpt)
        
        self.requestMenuReload.emit()   # let listeners know we need a menu reload

    def makeCurrecEmpty(self, mGrp, mnu, mOpt):
        # replace with an empty record
        cRec = menuItems().record()
        cRec.setValue('MenuGroup_id', mGrp)
        cRec.setValue('MenuID', mnu)
        cRec.setValue('OptionNumber', mOpt)

        self.currRec = cRec

    ##########################################
    ########    CRUD support

    @Slot()
    def setFormDirty(self, wdgt:cQFmFldWidg, dirty:bool = True):
        if wdgt.property('noedit'):
            return
        
        wdgt.setProperty('dirty', dirty)
        # if wdgt === self, set all children dirty
        if wdgt is not self:
            if dirty: self.setProperty('dirty',True)
        else:
            for W in self.children():
                if any([W.inherits(tp) for tp in ['QLineEdit', 'QTextEdit', 'QCheckBox', 'QComboBox', 'QDateEdit', ]]):
                    W.setProperty('dirty', dirty)
        
        # enable btnCommit if anything dirty
        self.btnCommit.setEnabled(self.property('dirty'))
    
    def isFormDirty(self) -> bool:
        return self.property('dirty')


    ##########################################
    ########    Widget-responding procs

    def copyMenuOption(self):
        cRec = self.currRec
        mnuGrp, mnuID, optNum = (cRec.value('MenuGroup_id'), cRec.value('MenuID'), cRec.value('OptionNumber'))

        dlg = self.cEdtMnuItmDlg_CopyMove_MenuItm(mnuGrp, mnuID, optNum, self)
        retval, CMChoiceCopy, newMnuID = dlg.exec()
        if retval:
            dbTbl = menuItems()
            pkTblName = f'{dbTbl.primaryKey().field(0).tableName()}'
            pkFldName = f'{dbTbl.primaryKey().field(0).name()}'
            pkFullName = f'{pkTblName}.{pkFldName}'
            newrec = QSqlRecord(cRec)
            newrec.setNull(pkFldName)
            newrec.setValue('MenuGroup_id', newMnuID[0])
            newrec.setValue('MenuID', newMnuID[1])
            newrec.setValue('OptionNumber', newMnuID[2])
            dbTbl.select()
            row = dbTbl.rowCount()
            dbTbl.insertRecord(row,newrec)
            if not dbTbl.submitAll():
                print("Failed to submit changes:", dbTbl.lastError().text())

            if CMChoiceCopy:
                ... # we've done everything we need to do
            else:
                pk = cRec.value(pkFldName)
                if pk:
                    dbTbl.setFilter(f'{pkFullName}={pk}')
                    dbTbl.select()
                    dbTbl.removeRow(0)
                    # do I need to submitAll ?
                self.makeCurrecEmpty(mnuGrp, mnuID, optNum)
            #endif CMChoiceCopy
            
            self.requestMenuReload.emit()   # let listeners know we need a menu reload
        # #endif retval

        return

class cEditMenu(QWidget):
    # more class constants
    _DFLT_menuGroup: int = -1
    _DFLT_menuID: int = -1
    intmenuGroup:int = _DFLT_menuGroup
    intmenuID:int = _DFLT_menuID
    formFields:Dict[str, QWidget] = {}
    

    class wdgtmenuITEM(cWidgetMenuItem):
        def __init__(self, menuitmRec, parent = None):
            super().__init__(menuitmRec, parent)
            
    class cEdtMnuDlgGetNewMenuGroupInfo(QDialog):
        def __init__(self, parent:QWidget = None):
            super().__init__(parent)
            
            self.setWindowModality(Qt.WindowModality.WindowModal)
            self.setWindowTitle(parent.windowTitle() if parent else 'New Menu Group')

            layoutGroupName = QHBoxLayout()
            lblGroupName = QLabel(self.tr('Group Name'))
            self.lnedtGroupName = QLineEdit('New Group', self)
            layoutGroupName.addWidget(lblGroupName)
            layoutGroupName.addWidget(self.lnedtGroupName)

            layoutGroupInfo = QHBoxLayout()
            lblGroupInfo = QLabel(self.tr('Group Info'))
            self.txtedtGroupInfo = QTextEdit(self)
            layoutGroupInfo.addWidget(lblGroupInfo)
            layoutGroupInfo.addWidget(self.txtedtGroupInfo)

            dlgButtons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel,
                Qt.Orientation.Horizontal,
                )
            dlgButtons.accepted.connect(self.accept)
            dlgButtons.rejected.connect(self.reject)            

            layoutMine = QVBoxLayout()
            layoutMine.addLayout(layoutGroupName)
            layoutMine.addLayout(layoutGroupInfo)
            layoutMine.addWidget(dlgButtons)
            
            self.setLayout(layoutMine)
            
        def exec(self):
            ret = super().exec()
            # later - prevent lvng if lnedtGroupName blank
            return (
                ret, 
                self.lnedtGroupName.text()         if ret==self.DialogCode.Accepted else None,
                self.txtedtGroupInfo.toPlainText() if ret==self.DialogCode.Accepted else None,
                )
    
    class cEdtMnuDlgCopyMoveMenu(QDialog):
        intCMChoiceCopy:int = 10
        intCMChoiceMove:int = 20
        
        def __init__(self, mnuGrp:int, menuID:int, parent:QWidget = None):
            super().__init__(parent)
            
            self.setWindowModality(Qt.WindowModality.WindowModal)
            self.setWindowTitle(parent.windowTitle() if parent else 'Copy/Move Menu')

            lblDlgTitle = QLabel(self.tr(f' Copy or Move Menu {menuID}'))
            
            layoutMenuID = QHBoxLayout()
            lblMenuID = QLabel(self.tr('Menu ID'))
            self.combobxMenuID = QComboBox(self)
            #  definedMenus = menuItems.objects.filter(MenuGroup=mnuGrp, OptionNumber=0).values_list('MenuID', flat=True)
            dictDefinedMenus = menuItems().recordsetList(['MenuID'], filter=f'MenuGroup_id={mnuGrp} AND OptionNumber=0')   # .objects.filter(MenuGroup=mnuGrp, OptionNumber=0).values_list('MenuID', flat=True)
            definedMenus = [mDict['MenuID'] for mDict in dictDefinedMenus]
            self.combobxMenuID.addItems([str(n) for n in range(256) if n not in definedMenus])
            layoutMenuID.addWidget(lblMenuID)
            layoutMenuID.addWidget(self.combobxMenuID)
            
            visualgrpboxCopyMove = QGroupBox(self.tr("Copy / Move"))
            layoutgrpCopyMove = QHBoxLayout()
            # Create radio buttons
            radioCopy = QRadioButton(self.tr("Copy"))
            radioMove = QRadioButton(self.tr("Move"))
            # Add radio buttons to the layout
            layoutgrpCopyMove.addWidget(radioCopy)
            layoutgrpCopyMove.addWidget(radioMove)
            visualgrpboxCopyMove.setLayout(layoutgrpCopyMove)
            # Create a QButtonGroup for logical grouping
            self.lgclbtngrpCopyMove = QButtonGroup()
            self.lgclbtngrpCopyMove.addButton(radioCopy, id=self.intCMChoiceCopy)
            self.lgclbtngrpCopyMove.addButton(radioMove, id=self.intCMChoiceMove)
            # Add the QGroupBox to the main layout

            dlgButtons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel,
                Qt.Orientation.Horizontal,
                )
            dlgButtons.accepted.connect(self.accept)
            dlgButtons.rejected.connect(self.reject)            

            layoutMine = QVBoxLayout()
            layoutMine.addWidget(lblDlgTitle)
            layoutMine.addWidget(visualgrpboxCopyMove)
            layoutMine.addLayout(layoutMenuID)
            layoutMine.addWidget(dlgButtons)
            
            self.setLayout(layoutMine)
            
        def exec(self):
            ret = super().exec()
            copymove = self.lgclbtngrpCopyMove.checkedId()
            return (
                ret, 
                copymove != self.intCMChoiceMove,   # True unless Move checked
                int(self.combobxMenuID.currentText()) if ret==self.DialogCode.Accepted else None,
                )
    
    def __init__(self, parent:QWidget = None):
        super().__init__(parent)
        
        self.layoutmainMenu: QGridLayout = QGridLayout()
        self.WmenuItm: Dict[int, cEditMenu.wdgtmenuITEM] = {}
        self.layoutmenuHdr: QHBoxLayout = QHBoxLayout()
        self.layoutmenuHdrLeft: QVBoxLayout = QVBoxLayout()
        self.layoutmenuHdrRight: QVBoxLayout = QVBoxLayout()
        self._menuSOURCE = MenuRecords()
        # self.currentMenu:cQSqlTableModel = None
        self.currentMenu:Dict[int, QSqlRecord] = None
        self.currRec:QSqlRecord = None
        
        self.layoutmainMenu.setColumnStretch(0,1)
        self.layoutmainMenu.setColumnStretch(1,0)
        self.layoutmainMenu.setColumnStretch(2,1)
        
        self.layoutMenuHdrLn1 = QHBoxLayout()
        self.layoutMenuHdrLn2 = QHBoxLayout()

        modlFld='MenuGroup'
        wdgt:cQFmFldWidg = cQFmFldWidg(cComboBoxFromDict, lblText='Menu Group', modlFld=modlFld, 
            choices=self.dictmenuGroup(), parent= self)
        self.formFields[modlFld] = wdgt
        self.fldmenuGroup:cQFmFldWidg = wdgt
        wdgt.signalFldChanged.connect(lambda idx: self.loadMenu(menuGroup=self.fldmenuGroup.Value())) 

        modlFld='GroupName'
        wdgt:cQFmFldWidg = cQFmFldWidg(QLineEdit, lblText='Group Name', modlFld=modlFld, parent=self)
        self.formFields[modlFld] = wdgt
        self.fldmenuGroupName:cQFmFldWidg = wdgt
        wdgt.signalFldChanged.connect(lambda: self.changeField(self.fldmenuGroupName))

        self.btnNewMenuGroup:QPushButton = QPushButton(self.tr('New Menu\nGroup'), self)
        self.btnNewMenuGroup.clicked.connect(self.createNewMenuGroup)

        modlFld='MenuID'
        wdgt:cQFmFldWidg = cQFmFldWidg(cComboBoxFromDict, lblText='menu', modlFld=modlFld, 
            parent=self)
        self.formFields[modlFld] = wdgt
        self.fldmenuID:cQFmFldWidg = wdgt
        wdgt.signalFldChanged.connect(lambda idx: self.loadMenu(menuGroup=self.intmenuGroup, menuID=self.fldmenuID.Value()))

        modlFld='OptionText'
        wdgt:cQFmFldWidg = cQFmFldWidg(QLineEdit, lblText='Menu Name', modlFld='OptionText', parent=self)
        self.formFields[modlFld] = wdgt
        self.fldmenuName:cQFmFldWidg = wdgt
        self.fldmenuName.signalFldChanged.connect(lambda: self.changeField(self.fldmenuName))
        
        self.lblnummenuGroupID:  QLCDNumber = QLCDNumber(3)
        self.lblnummenuGroupID.setMaximumSize(20,20)
        self.lblnummenuID:  QLCDNumber = QLCDNumber(3)
        self.lblnummenuID.setMaximumSize(20,20)

        self.btnRmvMenu:QPushButton = QPushButton(self.tr('Remove Menu'), self)
        self.btnRmvMenu.clicked.connect(self.rmvMenu)
        self.btnCopyMenu:QPushButton = QPushButton(self.tr('Copy/Move\nMenu'), self)
        self.btnCopyMenu.clicked.connect(self.copyMenu)
        
        self.layoutMenuHdrLn1.addWidget(self.fldmenuGroup)
        self.layoutMenuHdrLn1.addWidget(self.lblnummenuGroupID)
        self.layoutMenuHdrLn1.addWidget(self.fldmenuGroupName)
        self.layoutMenuHdrLn1.addWidget(self.btnNewMenuGroup)
        
        self.layoutMenuHdrLn2.addWidget(self.fldmenuID)
        self.layoutMenuHdrLn2.addWidget(self.lblnummenuID)
        self.layoutMenuHdrLn2.addWidget(self.fldmenuName)
        self.layoutMenuHdrLn2.addWidget(self.btnRmvMenu)
        self.layoutMenuHdrLn2.addWidget(self.btnCopyMenu)
        
        self.btnCommit:QPushButton = QPushButton(self.tr('\nSave\nChanges\n'), self)
        self.btnCommit.clicked.connect(self.writeRecord)

        self.layoutmenuHdrLeft.addLayout(self.layoutMenuHdrLn1)
        self.layoutmenuHdrLeft.addLayout(self.layoutMenuHdrLn2)
        self.layoutmenuHdrRight.addWidget(self.btnCommit)
        self.layoutmenuHdrRight.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.layoutmenuHdr.addLayout(self.layoutmenuHdrLeft)
        self.layoutmenuHdr.addLayout(self.layoutmenuHdrRight)
        
        self.layoutmainMenu.addLayout(self.layoutmenuHdr,0,0,1,3)
    ####
        self.bxFrame:List[QFrame] = [QFrame() for _ in range(_NUM_menuBUTTONS)]
        for bNum in range(_NUM_menuBUTTONS):
            self.bxFrame[bNum].setLineWidth(1)
            self.bxFrame[bNum].setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
            y, x = ((bNum % _NUM_menuBTNperCOL)+1, 0 if bNum < _NUM_menuBTNperCOL else 2)
            self.layoutmainMenu.addWidget(self.bxFrame[bNum],y,x)
            
            self.WmenuItm[bNum] = None      # later - build WmenuItm before this loop?

        self.setWindowTitle(self.tr('Edit Menu'))
                    
        self.setLayout(self.layoutmainMenu)
        self.loadMenu()
    # __init__

    def dictmenuGroup(self) -> Dict[str, int]:
        rs = menuGroups().recordsetList(['id', 'GroupName'])
        retDict = {d['GroupName']:d['id'] for d in rs}
        return retDict
    def dictmenus(self, mnuGrp:int) -> Dict[str, int]:
        tbl = menuItems()
        # tbl = MenuRecords()
        tbl.setFilter(f'MenuGroup_id = {mnuGrp} AND OptionNumber = 0')
        rs = tbl.recordsetList(['MenuID', 'OptionText'])
        retDict = Nochoice | {f"{d['OptionText']} ({d['MenuID']})":d['MenuID'] for d in rs}
        return retDict

    ##########################################
    ########    Create

    def createNewMenuGroup(self):
        dlg = self.cEdtMnuDlgGetNewMenuGroupInfo(self)
        retval, grpName, grpInfo = dlg.exec()
        if retval:
            # new menuGroups record
            newrec = menuGroups().record()
            newrec.setValue('GroupName', grpName)
            newrec.setValue('GroupInfo', grpInfo)

            #TODO: generic into newrec.save()            
            dbTbl = menuGroups()
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
                newmenurec = menuItems().record()
                newmenurec.setNull('id')
                newmenurec.setValue('MenuGroup_id', grppk)
                newmenurec.setValue('MenuID', 0)
                for fldNm, vlu in rec.items():
                    newmenurec.setValue(fldNm, vlu)
                dbTbl.insertRecord(0, newmenurec)
            if not dbTbl.submitAll():
                print("Failed to submit changes:", dbTbl.lastError().text())

            self.loadMenu(grppk, 0)
        return

    def copyMenu(self):
        mnuGrp = self.intmenuGroup
        mnuID = self.intmenuID

        dlg = self.cEdtMnuDlgCopyMoveMenu(mnuGrp, mnuID, self)
        retval, CMChoiceCopy, newMnuID = dlg.exec()
        if retval:
            qsFrom = self.currentMenu
            dbTbl = menuItems()
            dbTbl.setFilter('FALSE')
            dbTbl.select()
            insAt = dbTbl.rowCount()
            if CMChoiceCopy:
                for record in qsFrom.values():
                    record.setNull('id')
                    record.setValue('MenuID', newMnuID)
                    dbTbl.insertRecord(insAt, record)
                    insAt += 1
                if not dbTbl.submitAll():
                    print("Failed to submit changes:", dbTbl.lastError().text())
                #endwhile not record.isEmpty()
            else:
                updtstmnt = f'UPDATE {dbTbl.tableName()} SET MenuID = {newMnuID} WHERE MenuGroup_id = {mnuGrp} AND MenuID = {mnuID}'
                query:QSqlQuery = QSqlQuery(updtstmnt, cMenuDatabase)
                query.exec()
            #endif CMChoiceCopy
            self.loadMenu(mnuGrp, newMnuID)
        #endif retval

        return

        
    ##########################################
    ########    Read

    def movetoutil_findrecwithvalue(self, tblModel:Dict[int, QSqlRecord], fld:str, trgtValue) -> QSqlRecord | None:
        # for n in range(tblModel.rowCount()):
        for testrec in tblModel.values():
            # testrec = tblModel.record(n)
            if testrec.value(fld) == trgtValue:
                return testrec
            #endif testrec.value(fld) == trgtValue:
        #endwhile not testrec.isEmpty():
        
        return None
    def displayMenu(self):
        menuGroup = self.intmenuGroup
        menuID = self.intmenuID
        menuItemRecs = self.currentMenu
        # menuItemRecs.setFilter('OptionNumber=0')
        # menuHdrRec:QSqlRecord = self.movetoutil_findrecwithvalue(menuItemRecs,'OptionNumber',0)
        menuHdrRec:QSqlRecord = menuItemRecs[0]
        
        # set header elements
        self.lblnummenuGroupID.display(menuGroup)
        self.fldmenuGroup.setValue(str(menuGroup))
        self.fldmenuGroupName.setValue(menuHdrRec.value('GroupName'))
        self.lblnummenuID.display(menuID)
        d = self.dictmenus(menuGroup)
        self.fldmenuID.replaceDict(d)
        self.fldmenuID.setValue(menuID)
        self.fldmenuName.setValue(menuHdrRec.value('OptionText'))

        for bNum in range(_NUM_menuBUTTONS):
            y, x = ((bNum % _NUM_menuBTNperCOL)+1, 0 if bNum < _NUM_menuBTNperCOL else 2)
            bIndx = bNum+1
            mnuItmRc = self.movetoutil_findrecwithvalue(menuItemRecs, 'OptionNumber', bIndx)
            if not mnuItmRc:
                mnuItmRc = menuItems().record()
                mnuItmRc.setValue('MenuGroup_id', menuGroup)
                mnuItmRc.setValue('MenuID', menuID)
                mnuItmRc.setValue('OptionNumber', bIndx)
            oldWdg = self.WmenuItm[bNum]
            if oldWdg:
                # remove old widget
                self.layoutmainMenu.removeWidget(oldWdg)
                oldWdg.hide()
                del oldWdg

            self.WmenuItm[bNum] = self.wdgtmenuITEM(mnuItmRc)
            self.WmenuItm[bNum].requestMenuReload.connect(lambda: self.loadMenu(self.intmenuGroup, self.intmenuID))
            self.layoutmainMenu.addWidget(self.WmenuItm[bNum],y,x) 
        # endfor
     
    # displayMenu

    def loadMenu(self, menuGroup: int = _DFLT_menuGroup, menuID: int = _DFLT_menuID):
        SRC = self._menuSOURCE
        if menuGroup==self._DFLT_menuGroup:
            menuGroup = SRC.dfltMenuGroup()
        if menuID==self._DFLT_menuID:
            menuID = SRC.dfltMenuID_forGroup(menuGroup)
    
        self.intmenuGroup = menuGroup
        self.intmenuID = menuID
        
        if SRC.menuExist(menuGroup, menuID):
            self.currentMenu = SRC.menuDBRecs(menuGroup, menuID)
            # self.currRec = self.movetoutil_findrecwithvalue(self.currentMenu, 'OptionNumber', 0)
            self.currRec = self.currentMenu[0]  # am I safe in assuming existence?
            self.setFormDirty(self, False)       # should this be in displayMenu ?
            self.displayMenu()
        else:
            # menu doesn't exist; say so
            msg = QMessageBox(self)
            msg.setWindowTitle('Menu Doesn\'t Exist')
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.setText(f'Menu {menuID} doesn\'t exist!')
            msg.open()
    # loadMenu


    ##########################################
    ########    Update

    @Slot()
    def changeField(self, wdgt:cQFmFldWidg) -> bool:
        # move to class var?
        forgnKeys = {   
            'MenuGroup',
            }
        # move to class var?
        valu_transform_flds = {
            'GroupName',
            }
        cRec:QSqlRecord = self.currRec
        dbField = wdgt.modelField()

        wdgt_value = wdgt.Value()

        if dbField in forgnKeys:
            dbField += '_id'
        if dbField in valu_transform_flds:
            # wdgt_value = valu_transform_flds[dbField][1](wdgt_value)
            pass

        if wdgt_value or isinstance(wdgt_value,bool):
            if dbField != 'GroupName':  # GroupName belongs to cRec.MenuGroup; persist only at final write
                cRec.setValue(dbField, wdgt_value)
            self.setFormDirty(wdgt, True)
        
            return True
        else:
            return False
        # endif wdgt_value
    # changeField
    
    @Slot()
    def writeRecord(self):
        if not self.isFormDirty():
            return
        
        cRec:QSqlRecord = self.currRec
        
        # check other traps later
        
        if self.isWdgtDirty(self.fldmenuGroupName):
            groupTbl = menuGroups()
            gpkTblName = f'{groupTbl.primaryKey().field(0).tableName()}'
            gpkFldName = f'{groupTbl.primaryKey().field(0).name()}'
            gpkFullName = f'{gpkTblName}.{gpkFldName}'
            groupTbl.setFilter(f'{gpkFullName}={self.intmenuGroup}')
            groupTbl.record(0).setValue('GroupName', self.fldmenuGroupName.Value())
            if not groupTbl.submitAll():
                print("Failed to submit changes:", groupTbl.lastError().text())

        mnuTbl = menuItems()
        mpkTblName = f'{mnuTbl.primaryKey().field(0).tableName()}'
        mpkFldName = f'{mnuTbl.primaryKey().field(0).name()}'
        mpkFullName = f'{mpkTblName}.{mpkFldName}'
        mnuTbl.setFilter(f"{mpkFullName}={cRec.value('id')}")
        mnuTbl.setRecord(0,cRec)
        if not mnuTbl.submitAll():
            print("Failed to submit changes:", mnuTbl.lastError().text())
        
        self.setFormDirty(self, False)
    # writeRecord


    ##########################################
    ########    Delete

    @Slot()
    def rmvMenu(self):
        
        pleaseWriteMe(self, 'Remove Menu')
        return
        
        (mGrp, mnu, mOpt) = (self.currRec.MenuGroup, self.currRec.MenuID, self.currRec.OptionNumber)
        
        # verify delete
        
        # remove from db
        if self.currRec.pk:
            self.currRec.delete()
        
        # replace with an "next" record
        self.currRec = menuItems(
            MenuGroup = mGrp,
            MenuID = mnu,
            OptionNumber = mOpt,
            )


    ##########################################
    ########    CRUD support

    @Slot()
    def setFormDirty(self, wdgt:QWidget, dirty:bool = True):
        if wdgt.property('noedit'):
            return
        
        wdgt.setProperty('dirty', dirty)
        # if wdgt === self, set all children dirty
        if wdgt is not self:
            if dirty: self.setProperty('dirty',True)
        else:
            for W in self.children():
                if any([W.inherits(tp) for tp in ['QLineEdit', 'QTextEdit', 'QCheckBox', 'QComboBox', 'QDateEdit', ]]):
                    W.setProperty('dirty', dirty)
        
        # enable btnCommit if anything dirty
        self.btnCommit.setEnabled(self.property('dirty'))
    
    def isFormDirty(self) -> bool:
        return self.property('dirty')

    def isWdgtDirty(self, wdgt:QWidget) -> bool:
        return wdgt.property('dirty')


    ##########################################
    ########    Widget-responding procs
# class EditMenu


#############################################
#############################################
#############################################


from app.database import appDatabase
class OpenTable(QWidget):
    _tableListSQL:str = 'PRAGMA table_list;'
    
    def __init__(self, tbl:str = None, parent:QWidget = None):
        super().__init__(parent)
        
        # font = QFont()
        # font.setPointSize(12)
        # self.setFont(font)
        
        db = appDatabase
        if not tbl:
            # get tbl name
                # use self._tableListSQL
            # read all table names
            # present and select
            ...
        
        # for testing ...
        tbl = 'incShip_hbl'
        
        # read into model
        # verify tbl exists
        # error, rows, colNames = self.getTable(tbl)
        error, rows, colNames = (None, [], [])
        if error:
            raise error
        
        # tblWidget = self.tableWidget(rows, colNames)
        tblWidget = self.tableWidget(tbl, db)
        # bring all rows in so rowCount will be correct
        while tblWidget.model().canFetchMore():
            tblWidget.model().fetchMore()
        rows = tblWidget.model().rowCount()
        colNames = [tblWidget.model().headerData(n, Qt.Orientation.Horizontal) for n in range(tblWidget.model().columnCount())]
        # present TableView

        # save incoming for future use if needed
        self.rows = rows
        self.colNames = colNames

        self.layoutForm = QVBoxLayout(self)
        
        # Form Header Layout
        self.layoutFormHdr = QVBoxLayout()
        self.lblFormName = cQFmNameLabel()
        self.lblFormName.setText(self.tr('Table'))
        self.setWindowTitle(self.tr('Table'))
        self.layoutFormHdr.addWidget(self.lblFormName)
        
        self.layoutFormTableDescription = QFormLayout()
        lblnRecs = QLabel()
        lblnRecs.setText(f'{rows}')
        lblcolNames = QLabel()
        lblcolNames.setText(str(colNames))
        self.layoutFormTableDescription.addRow('rows:', lblnRecs)
        self.layoutFormTableDescription.addRow('cols:', lblcolNames)

        # main area for displaying SQL
        self.layoutFormMain = QVBoxLayout()
        self.layoutFormMain.addWidget(tblWidget)
        
        self.layoutForm.addLayout(self.layoutFormHdr)
        self.layoutForm.addLayout(self.layoutFormTableDescription)
        self.layoutForm.addLayout(self.layoutFormMain)
        
    def getTable(self, tblName:str) -> Tuple[Exception|None, List[Dict[str, Any]], List[str]|str]:
        pleaseWriteMe(self, 'fix getTable in class OpenTable')
        # inputSQL:str = f'SELECT * FROM {tblName}'
        # # inputSQL:str = f'SELECT * FROM %(tblName)s'
        # sqlerr = None
        # with db.connection.cursor() as djngocursor:
        #     try:
        #         djngocursor.execute(inputSQL)
        #         # djngocursor.execute(inputSQL, [tblName])
        #     except Exception as err:
        #         sqlerr = err
        #     colNames = []
        #     rows = []
        #     if not sqlerr:
        #         if djngocursor.description:
        #             colNames = [col[0] for col in djngocursor.description]
        #             rows = dictfetchall(djngocursor)
        #         else:
        #             colNames = 'NO RECORDS RETURNED; ' + str(djngocursor.rowcount) + ' records affected'
        #             rows = []
        #         #endif cursor.description
        #     else:  
        #         # nothing to do
        #         ...
        #     #endif not sqlerr
        # #end with
        
        # return (sqlerr, rows, colNames)

    # def tableWidget(self, rows:List[Dict[str, Any]], colNames:str|List[str]) -> QTableView:
    def tableWidget(self, tbl, db) -> QTableView:
        resultModel = cQSqlTableModel(tbl, db, self.parent())
        resultTable = QTableView()
        # resultTable.verticalHeader().setHidden(True)
        header = resultTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        # Apply stylesheet to control text wrapping
        resultTable.setStyleSheet("""
        QHeaderView::section {
            padding: 5px;
            font-size: 12px;
            text-align: center;
            white-space: normal;  /* Allow text to wrap */
        }
        """)
        resultTable.setModel(resultModel)
        
        return resultTable
        

#############################################
#############################################
#############################################


class _internalForms:
    EditMenu = '.-EDT-menu.-'
    OpenTable = '-.OPN-tbL.-'
    # RunCode = ''
    RunSQLStatement = '.-ruN-sql.-'
    # ConstructSQLStatement = ''
    # LoadExtWebPage = ''
    # ChangePW = ''
    # EditParameters = ''
    # EditGreetings = ''
# FormNameToURL_Maps for internal use only
# FormNameToURL_Map['menu Argument'.lower()] = (url, view)
FormNameToURL_Map[_internalForms.EditMenu] = (None, cEditMenu)
FormNameToURL_Map[_internalForms.OpenTable] = (None, OpenTable)
FormNameToURL_Map[_internalForms.RunSQLStatement] = (None, cMRunSQL)

