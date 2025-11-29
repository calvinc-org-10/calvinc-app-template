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

from cMenu.database import cMenu_Session
from cMenu.dbmenulist import MenuRecords
from cMenu.models import (menuGroups, menuItems, 
    newgroupnewmenu_menulist, )
from cMenu.menucommand_constants import MENUCOMMANDS, COMMANDNUMBER
from cMenu.utils import (
    recordsetList, 
    cQFmConstants, 
    cComboBoxFromDict, cstdTabWidget,
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
class cWidgetMenuItem(cSimpleRecordForm_Base):
    """
    cWidgetMenuItem_tst
    -------------------
    A specialized form widget for viewing and editing a single menu item record (menuItems).
    This widget is intended to be used inside a QWidget-based application using PyQt/PySide
    and SQLAlchemy for persistence. It builds a compact edit form from the `fieldDefs`
    mapping and provides common CRUD-related actions appropriate for a menu item:
    - Save changes (commit)
    - Remove the current option
    - Copy or Move the current option to another menu/position
    Notes
    -----
    - This widget expects an SQLAlchemy mapped ORM model `menuItems` and a sessionmaker
        callable `cMenu_Session` to be available and assigned to the class attributes
        `_ORMmodel` and `_ssnmaker` respectively.
    - The widget does not create brand-new menu items in the sense of offering a primary
        "new" flow; it operates on an existing `menuItems` instance supplied at construction.
    - Copy semantics use `copy.deepcopy` followed by `sqlalchemy.orm.session.make_transient`
        to detach the copy before inserting it as a new row. Move semantics create a copy
        and then remove the original row from the database.
    - The widget emits the `requestMenuReload` Signal() whenever a change is made that
        requires other components to refresh their cached menu structures.
    Public attributes (class-level)
    -------------------------------
    - _ORMmodel: ORM model class for menu items (expected: menuItems)
    - _ssnmaker: sessionmaker factory for database transactions (expected: cMenu_Session)
    - fieldDefs: dict mapping field names to widget configuration for form construction
    - requestMenuReload: Qt Signal emitted when a menu reload is required by listeners
    Inner class: cEdtMnuItmDlg_CopyMove_MenuItm
    ------------------------------------------
    A modal QDialog used to prompt the user for a destination Menu Group, Menu ID,
    and Option Number when copying or moving a menu option. It encapsulates all UI and
    validation required to choose a valid destination (e.g., preventing collisions with
    already-defined option numbers):
    Key behaviors / API:
    - __init__(menuGrp:int, menuID:int, optionNumber:int, parent:QWidget|None)
        Constructs the dialog initializing comboboxes for menu groups, menus, and options.
    - dictmenuGroup() -> Dict[str,int]
        Returns mapping of menu group names to ids using the cMenu_Session.
    - dictmenus(mnuGrp:int) -> Mapping[str, int|None]
        Returns mapping of main-menu OptionText -> MenuID for menus in the supplied group.
    - dictmenuOptions(mnuID:int) -> Mapping[str, int|None]
        Returns the set of available option numbers (as strings) for a target menu id,
        excluding option numbers already defined in that menu.
    - loadMenuIDs(idx:int), loadMenuOptions(idx:int), menuOptionChosen(idx:int)
        Slots used to cascade the combobox population and enable/disable the Ok button.
    - enableOKButton()
        Enables the Ok button only when a Group, Menu and Option are all selected.
    - exec_CM_MItm() -> Tuple[int|bool, bool, Tuple[int,int,int]]
        Executes the dialog (modal) and returns a tuple:
            (exec_result, is_copy_bool, (chosenGroup, chosenMenu, chosenOption))
        where exec_result is the QDialog exec() return, and is_copy_bool is True for Copy,
        False for Move.
    Public instance methods (high-level)
    ------------------------------------
    - __init__(menuitmRec: menuItems, parent: QWidget|None = None)
        Initialize the widget to operate on the provided menu item ORM instance. The
        supplied record is considered the "current record" for subsequent operations.
    - _buildFormLayout() -> tuple[QBoxLayout, QTabWidget, QBoxLayout|None]
        Internal layout builder that returns tuple of left tab widget and right layout
        containers used by the base form assembly.
    - _addActionButtons()
        Constructs and wires action buttons (Save Changes, Copy / Move, Remove) and places
        them into the widget's button layout. Buttons are connected to on_save_clicked,
        copyMenuOption, and on_delete_clicked respectively.
    - _handleActionButton(action: str) -> None
        Overridden no-op; action routing is handled locally.
    - _finalizeMainLayout()
        Assembles form, action buttons, and other parts into the main layout.
    - fillFormFromcurrRec()
        Populate the form widgets from the currently-bound record. Also updates button
        enablement: Copy/Move and Remove are disabled for new (unsaved) records.
    - initialdisplay()
        Convenience method that calls fillFormFromcurrRec() to prime the UI.
    - on_delete_clicked() -> None
        Slot executed when the Remove button is clicked. Behavior:
            - Confirms deletion with the user (via areYouSure).
            - Loads the persistent record by primary key and deletes it in a session, then commits.
            - Reinitializes the current record object kept by the widget and restores the
                MenuGroup/MenuID/OptionNumber values so the user can create or reassign a new
                option in the same slot if desired.
            - Emits requestMenuReload to inform listeners that menu data changed.
        Preconditions:
            - self._ssnmaker (class attribute) must be available.
            - self._ORMmodel must refer to the mapped ORM model.
    - copyMenuOption() -> None
        Slot launched by the Copy / Move button. Behavior:
            - Opens the inner cEdtMnuItmDlg_CopyMove_MenuItm dialog to request a destination.
            - If the user accepts:
                    * Creates a deep-copy of the in-memory record, detaches it (make_transient),
                        resets primary keys and target MenuGroup/MenuID/OptionNumber, and inserts it
                        into the database (session.add + commit).
                    * If the Move option was selected, deletes the original persistent record and
                        refreshes the widget's current record to a fresh, unpersisted instance bound
                        to the same original MenuGroup/MenuID/OptionNumber (so the UI remains stable).
            - Emits requestMenuReload when a move occurs (or when appropriate after copy).
        Implementation details:
            - The copy preserves relationships where deepcopy copies them; using make_transient
                is necessary to convert the copy into a state suitable for insertion.
            - The code ensures the sessionmaker and ORMmodel exist before performing DB actions.
    Signals
    -------
    - requestMenuReload: emitted after operations that require other UI components to
        reload/rebuild menus (e.g., delete, move).
    Error handling and assumptions
    ------------------------------
    - The widget assumes a working SQLAlchemy environment and valid ORM mappings for
        menuGroups and menuItems.
    - Database operations are transactional and use the provided cMenu_Session context.
    - UI routines assume typical Qt widget behavior and that combobox widgets expose
        .currentData(), .currentIndex(), .replaceDict(), .setCurrentIndex(), .clear() etc.
        (cComboBoxFromDict is expected to implement replaceDict and to use the data role
        for stored ids).
    - The widget will do nothing (no exception) if invoked when there is no current record,
        or if required class attributes (sessionmaker/ORM model) are not set; assertions are
        used in some code paths to surface incorrect configuration early.
    Example use
    -----------
    Create an instance of the widget bound to a loaded menuItems ORM instance and add it
    to a parent container. Wire to requestMenuReload to update surrounding UI:
            w = cWidgetMenuItem_tst(my_menuitem_record, parent=some_parent_widget)
            w.requestMenuReload.connect(on_reload_needed)
    This docstring documents the public behaviors and expectations of cWidgetMenuItem_tst.
    """
    _ORMmodel = menuItems
    _ssnmaker = cMenu_Session
    fieldDefs = {
        'OptionNumber': {'label': 'Option Number', 'widgetType': QLineEdit, 'position': (0,0), 'noedit': True, 'readonly': True, 'frame': False, 'maximumWidth': 25, 'focusPolicy': Qt.FocusPolicy.NoFocus, 'focusable': Qt.FocusPolicy.NoFocus, },
        'OptionText': {'label': 'OptionText', 'widgetType': QLineEdit, 'position': (0,1,1,2)},
        'TopLine': {'label': 'Top Line', 'widgetType': QCheckBox, 'position': (0,3,1,2), 'lblChkBxYesNo': {True:'YES', False:'NO'}, },
        'BottomLine': {'label': 'Btm Line', 'widgetType': QCheckBox, 'position': (0,5), 'lblChkBxYesNo': {True:'YES', False:'NO'}, },
        'Command': {'label': 'Command', 'widgetType': cComboBoxFromDict, 'choices': vars(COMMANDNUMBER), 'position': (1,0,1,2)},
        'Argument': {'label': 'Argument', 'widgetType': QLineEdit, 'position': (1,2,1,2), },
        'PWord': {'label': 'Password', 'widgetType': QLineEdit, 'position': (1,4,1,2), },
    }

    # formFields:Dict[str, QWidget] = {}

    requestMenuReload:Signal = Signal()

    class cEdtMnuItmDlg_CopyMove_MenuItm(QDialog):

        intCMChoiceCopy:int = 10
        intCMChoiceMove:int = 20

        def __init__(self, menuGrp:int, menuID:int, optionNumber:int, parent = None):   # parent:QWidget = None
            super().__init__(parent)

            self.setWindowModality(Qt.WindowModality.WindowModal)
            self.setWindowTitle(parent.windowTitle() if parent else 'Copy/Move Menu Item')

            self.dlgButtons = None # self.dlgButtons:QDialogButtonBoxto be defined later, but must exist now

            lblDlgTitle = QLabel(self.tr(f' Copy or Move Menu Item {menuID}, {optionNumber}'))

            ##################################################
            # set up menuGroup, menuID, menuOption comboboxes
            layoutNewItemID = QGridLayout()

            lblMenuGroupID = QLabel(self.tr('Menu Group'))
            self.combobxMenuGroupID = cComboBoxFromDict(self.dictmenuGroup(), parent=self)
            self.combobxMenuGroupID.activated.connect(self.loadMenuIDs)

            lblMenuID = QLabel(self.tr('Menu'))
            self.combobxMenuID = cComboBoxFromDict(dict(self.dictmenus(menuGrp)), parent=self)
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
        # __init__
        
        ##########################################
        ########    execute this dialog

        def exec_CM_MItm(self) -> Tuple[int|bool, bool, Tuple[int, int, int]]:
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
        # exec_CM_MItm

        ##########################################
        ########    menu and Group dicts

        def dictmenuGroup(self) -> Dict[str, int]:
            # # TODO: generalize this to work with any table (return a dict of {id:record})
            # listmenuGroups = recordsetList(menuGroups, retFlds=['GroupName', 'id'], ssnmaker=cMenu_Session, orderby='GroupName')
            # # stmt = select(menuGroups.GroupName, menuGroups.id).select_from(menuGroups).order_by(menuGroups.GroupName)
            # # with cMenu_Session() as session:
            # #     retDict = {row.GroupName: row.id for row in session.execute(stmt).all()}
            # retDict = {row['GroupName']: row['id'] for row in listmenuGroups}
            # return retDict
            return MenuRecords.menuGroupDict()
        # dictmenuGroup
            
        def dictmenus(self, mnuGrp:int) -> Mapping[str, int|None]:
            retDict = Nochoice | MenuRecords.menuListDict(mnuGrp)
            return retDict      # type: ignore
        # dictmenus
        
        def dictmenuOptions(self, mnuID:int) -> Mapping[str, int|None]:
            mnuGrp:int = self.combobxMenuGroupID.currentData()
            listmenuItems = recordsetList(menuItems, retFlds=['OptionNumber'], where=f'MenuID={mnuID} AND MenuGroup_id={mnuGrp}', ssnmaker=cMenu_Session)
            # stmt = select(menuItems.OptionNumber).select_from(menuItems).where(
            #     menuItems.MenuID == mnuID,
            #     menuItems.MenuGroup_id == mnuGrp,
            # )
            # with cMenu_Session() as session:
            #     rs = session.execute(stmt).all()
            #     definedOptions = [rec.OptionNumber for rec in rs]
            definedOptions = [rec['OptionNumber'] for rec in listmenuItems]
            # Nochoice = {'---': None}  # only needed for combo boxes, not datalists
            return Nochoice | { str(n+1): n+1 for n in range(_NUM_menuBUTTONS) if n+1 not in definedOptions }
            # MenuRecords.menuDict(mnuGrp, mnuID)
        # dictmenuOptions

        ##########################################
        ########    getters/setters

        ##########################################
        ########    Create

        ##########################################
        ########    Read

        @Slot(int)  #type: ignore
        def loadMenuIDs(self, idx:int):
            mnuGrp:int = self.combobxMenuGroupID.currentData()
            # if self.combobxMenuGroupID.currentIndex() != -1:
            if mnuGrp is not None:
                self.combobxMenuID.replaceDict(dict(self.dictmenus(mnuGrp)))
            self.combobxMenuID.setCurrentIndex(-1)
            self.combobxMenuOption.clear()
            self.enableOKButton()
        # loadMenuIDs
        
        @Slot(int) #type: ignore
        def loadMenuOptions(self, idx:int):
            mnuID:int = self.combobxMenuID.currentData()
            #if self.combobxMenuID.currentIndex() != -1:
            if mnuID is not None:
                self.combobxMenuOption.replaceDict(dict(self.dictmenuOptions(mnuID)))
            self.combobxMenuOption.setCurrentIndex(-1)
            self.enableOKButton()
        # loadMenuOptions
        
        ##########################################
        ########    Update

        ##########################################
        ########    Delete

        ##########################################
        ########    object status

        ##########################################
        ########    widget-responding procs

        @Slot(int)  #type: ignore
        def menuOptionChosen(self, idx:int):
            self.enableOKButton()
        # menuOptionChosen
        def enableOKButton(self):
            if not self.dlgButtons:
                return
            all_GrpIdOption_chosen = all([
                self.combobxMenuGroupID.currentIndex() != -1,
                self.combobxMenuID.currentIndex() != -1,
                self.combobxMenuOption.currentIndex() != -1,
            ])
            self.dlgButtons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(all_GrpIdOption_chosen)
        # enableOKButton


    def __init__(self, menuitmRec:menuItems, parent:QWidget = None):   # type: ignore

        self.setcurrRec(menuitmRec)
        super().__init__(parent=parent)

        font = QFont()
        font.setPointSize(7)
        self.setFont(font)

        self.setObjectName('cWidgetMenuItem')

    # __init__

    ##########################################
    ########    Layout

    # def _buildFormLayout(self) -> tuple[QBoxLayout, QTabWidget, QBoxLayout | None]:
    def _buildFormLayout(self) -> Dict[str, QWidget|QLayout|None]:
        
        rtnDict: Dict[str, QWidget|QLayout|None] = {}

        layoutMain = QVBoxLayout(self)
        layoutMain.setContentsMargins(0,0,0,0)
        layoutMain.setSpacing(0)

        layoutFormMain = QHBoxLayout()
        layoutFormMain.setContentsMargins(0,0,0,0)
        layoutFormMain.setSpacing(0)

        layoutFormMainLeft = cstdTabWidget()
        layoutFormMainLeft.setContentsMargins(0,0,0,0)

        layoutFormMainRight = QVBoxLayout()
        layoutFormMainRight.setContentsMargins(0,0,0,0)
        layoutFormMainRight.setSpacing(0)

        layoutFormMain.addWidget(layoutFormMainLeft)
        layoutFormMain.addLayout(layoutFormMainRight)
        
        rtnDict['layoutMain'] = layoutMain
        rtnDict['layoutForm'] = layoutFormMain
        rtnDict['layoutFormPages'] = layoutFormMainLeft
        rtnDict['layoutButtons'] = layoutFormMainRight
        
        return rtnDict
    # _buildFormLayout
    def _finalizeMainLayout(self, layoutMain: QVBoxLayout, items: List | Tuple) -> None:
        items = [self.dictFormLayouts.get('layoutForm', None)]
        return super()._finalizeMainLayout(layoutMain, items)

    def _addActionButtons(self, 
            layoutButtons:QBoxLayout|None = None,
            layoutHorizontal: bool = True, 
            NavActions: list[tuple[str, QIcon]]|None = None,
            CRUDActions: list[tuple[str, QIcon]]|None = None,
            ) -> None:
        self.btnCommit = QPushButton(self.tr('Save\nChanges'), self)
        self.btnCommit.clicked.connect(self.on_save_clicked)
        # self.btnCommit.setFixedSize(60, 30)  # Adjust width and height
        self.btnCommit.setStyleSheet("padding: 2px; margin: 0;")  # Remove extra padding

        self.btnMoveCopy = QPushButton(self.tr('Copy / Move'), self)
        self.btnMoveCopy.clicked.connect(self.copyMenuOption)
        # self.btnMoveCopy.setFixedSize(60, 30)  # Adjust width and height
        self.btnMoveCopy.setStyleSheet("padding: 2px; margin: 0;")  # Remove extra padding

        self.btnRemove = QPushButton(self.tr('Remove'), self)
        self.btnRemove.clicked.connect(self.on_delete_clicked)
        # self.btnRemove.setFixedSize(60, 30)  # Adjust width and height
        self.btnRemove.setStyleSheet("padding: 2px; margin: 0;")  # Remove extra padding

        assert isinstance(layoutButtons, QBoxLayout), 'layoutButtons must be a Box Layout'
        layoutButtons.addWidget(self.btnMoveCopy)
        layoutButtons.addWidget(self.btnRemove)
        layoutButtons.addWidget(self.btnCommit)
    def _handleActionButton(self, action: str) -> None:
        # we have our own handlers, so no need to handle anything here
        return
    # _addActionButtons, _handleActionButton    

    # not needed 0 super() already does this
    # def _finalizeMainLayout(self):
    #     assert isinstance(self.layoutMain, QBoxLayout), 'layoutMain must be a Box Layout'

    #     # lyout = getattr(self, 'layoutFormHdr', None)
    #     # if isinstance(lyout, QLayout):
    #     #     self.layoutMain.addLayout(lyout)
    #     lyout = getattr(self, 'layoutForm', None)
    #     if isinstance(lyout, QWidget):
    #         self.layoutMain.addWidget(lyout)
    #     lyout = getattr(self, 'layoutButtons', None)
    #     if isinstance(lyout, QLayout):
    #         self.layoutMain.addLayout(lyout)
    #     # lyout = getattr(self, '_statusBar', None)
    #     # if isinstance(lyout, QLayout):
    #     #     self.layoutMain.addLayout(lyout)            #TODO: more flexibility in where status bar is placed
    # # _finalizeMainLayout


    ######################################################
    ########    Display 

    def fillFormFromcurrRec(self):
        super().fillFormFromcurrRec()

        self.btnMoveCopy.setEnabled(not self.isNewRecord())
        self.btnRemove.setEnabled(not self.isNewRecord())
    # fillFormFromRec

    def initialdisplay(self):
        self.fillFormFromcurrRec()
    # initialdisplay()



    ##########################################
    ########    Create

    # this widget doesn't create new records

    ##########################################
    ########    Read


    ##########################################
    ########    Update

    @Slot()     #type: ignore
    # def changeField(self):
    def changeField(self, wdgt, dbField, wdgt_value, force=False):
        super().changeField(wdgt, dbField, wdgt_value, force=False)
    # changeField

    @Slot()
    def on_save_clicked(self):
        super().on_save_clicked()
        self.requestMenuReload.emit()   # let listeners know we need a menu reload
    # on_save_clicked

    ##########################################
    ########    Delete

    @Slot()
    def on_delete_clicked(self):
        currRec = self.currRec()
        if not currRec:
            return

        mGrp, mnu, mOpt = (currRec.MenuGroup_id, currRec.MenuID, currRec.OptionNumber)

        pKey = self.primary_key()
        keyID = getattr(currRec, pKey.key)

        really = areYouSure(self,
            title="Remove Menu Option?",
            areYouSureQuestion=f'Really remove menu option {mGrp}, {mnu}, {mOpt} ({currRec.OptionText}) ?'
            )
        if really != QMessageBox.StandardButton.Yes:
            return

        # Actually delete
        ssnmkr = self.ssnmaker()
        assert ssnmkr is not None, "Sessionmaker must be set before touching the database"
        modl = self.ORMmodel()
        assert modl is not None, "ORMmodel must be set before deleting record"
        with ssnmkr() as session:
            rec = session.get(modl, keyID)
            if rec:
                session.delete(rec)
                session.commit()

        self.initializeRec()
        # preserve MenuGroup, MenuID, OptionNumber
        currRec = self.currRec()
        currRec.MenuGroup_id, currRec.MenuID, currRec.OptionNumber = mGrp, mnu, mOpt

        self.fillFormFromcurrRec()

        self.requestMenuReload.emit()   # let listeners know we need a menu reload
    # on_delete_clicked

    # ##########################################
    # ########    Record Status


    ##########################################
    ########    Widget-responding procs

    def copyMenuOption(self):
        cRec = self.currRec()
        mnuGrp, mnuID, optNum = (cRec.MenuGroup_id, cRec.MenuID, cRec.OptionNumber)

        dlg = self.cEdtMnuItmDlg_CopyMove_MenuItm(mnuGrp, mnuID, optNum, self)
        retval, CMChoiceCopy, newMnuID = dlg.exec_CM_MItm()
        if retval:
            # Create a copy (including relationships)
            new_rec = copy.deepcopy(cRec)

            # Detach the copy from the session
            make_transient(new_rec)

            # Reset primary keys
            new_rec.id = None                       # type: ignore
            new_rec.MenuGroup_id = newMnuID[0]      # type: ignore
            new_rec.MenuID = newMnuID[1]            # type: ignore
            new_rec.OptionNumber = newMnuID[2]      # type: ignore

            with cMenu_Session() as session:
                session.add(new_rec)
                session.commit()

            if CMChoiceCopy:
                ... # we've done everything we need to do
            else:
                pk = cRec.id
                rslt = "No record to delete"
                if pk:
                    with cMenu_Session() as session:
                        session.delete(cRec)
                        session.commit()
                #endif pk

                self.initializeRec()
                # preserve MenuGroup, MenuID, OptionNumber
                currRec = self.currRec()
                currRec.MenuGroup_id, currRec.MenuID, currRec.OptionNumber = mnuGrp, mnuID, optNum
            #endif CMChoiceCopy

            self.fillFormFromcurrRec()

            self.requestMenuReload.emit()   # let listeners know we need a menu reload
            
            # announce success
            copyword = 'copied' if CMChoiceCopy else 'moved'
            QMessageBox.information(self,
                self.tr(f"Menu Option {copyword}"),
                self.tr(f"Menu option {mnuGrp}, {mnuID}, {optNum} successfully {copyword} to {newMnuID[0]}, {newMnuID[1]}, {newMnuID[2]}.")
                )

        # #endif retval
        return
    # copyMenuOption
    
# class cWidgetMenuItem
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


class EditMenuTest(cSimpleRecordForm):
    _ORMmodel = menuItems
    _ssnmaker = cMenu_Session
    _formname = 'Edit Menu Test'
    fieldDefs = {
        '@MenuGroup_id': {'widgetType': cComboBoxFromDict, 'label': 'Menu Group', 'lookupHandler': 'loadMenuWithGroupID', 
            # 'choices': lambda: self.dictmenuGroup(), 
            'page': cQFmConstants.pageFixedTop.value, 'position': (0,0), },
        '@MenuID': {'widgetType': cComboBoxFromDict, 'label': 'Menu ID',  'lookupHandler': 'loadMenuWithMenuID', 
            # 'choices': lambda self: self.dictmenus(self.intmenuGroup), 
            'page': cQFmConstants.pageFixedTop.value, 'position': (1,0), },
        '+GroupName': {'widgetType': QLineEdit, 'label': 'Menu Group Name', 
            'page': cQFmConstants.pageFixedTop.value, 'position': (0,2,1,2), },
        'OptionText': {'widgetType': QLineEdit, 'label': 'Menu Name', 
            'page': cQFmConstants.pageFixedTop.value, 'position': (1,2), },
        '+RmvMenu': {'widgetType': QPushButton, 'label': 'Remove Menu', 'clickedHandler': 'rmvMenu', 
            'page': cQFmConstants.pageFixedTop.value, 'position': (1,3), },
        '+NewMenuGroup': {'widgetType': QPushButton, 'label': 'New Menu Group', 'clickedHandler': 'createNewMenuGroup', 
            'page': cQFmConstants.pageFixedTop.value, 'position': (0,4), },
        '+CopyMenu': {'widgetType': QPushButton, 'label': 'Copy/Move Menu', 'clickedHandler': 'copyMenu', 
            'page': cQFmConstants.pageFixedTop.value, 'position': (1,4), },
        '+Commit': {'widgetType': QPushButton, 'label': '\nSave\nChanges\n', 'clickedHandler': 'writeRecord', 
            'page': cQFmConstants.pageFixedTop.value, 'position': (0,5,2,1), },
    }

    # more class constants
    _DFLT_menuGroup: int = -1
    _DFLT_menuID: int = -1
    intmenuGroup:int = _DFLT_menuGroup
    intmenuID:int = _DFLT_menuID
    
    class wdgtmenuITEM(cWidgetMenuItem):
        def __init__(self, menuitmRec, parent = None):
            super().__init__(menuitmRec, parent)
            
    class cEdtMnuDlgGetNewMenuGroupInfo(QDialog):
        def __init__(self, parent:QWidget|None = None):
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
            
        def exec_NewMGInfo(self):
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
        
        def __init__(self, mnuGrp:int, menuID:int, parent:QWidget|None = None):
            super().__init__(parent)
            
            self.setWindowModality(Qt.WindowModality.WindowModal)
            self.setWindowTitle(parent.windowTitle() if parent else 'Copy/Move Menu')

            lblDlgTitle = QLabel(self.tr(f' Copy or Move Menu {menuID}'))
            
            layoutMenuID = QHBoxLayout()
            lblMenuID = QLabel(self.tr('Menu ID'))
            self.combobxMenuID = QComboBox(self)
            #  definedMenus = menuItems.objects.filter(MenuGroup=mnuGrp, OptionNumber=0).values_list('MenuID', flat=True)
            
            dictDefinedMenus = MenuRecords().recordsetList(['MenuID'], filter=f'MenuGroup_id={mnuGrp} AND OptionNumber=0')   # .objects.filter(MenuGroup=mnuGrp, OptionNumber=0).values_list('MenuID', flat=True)
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
            
        def exec_CMMnu(self):
            ret = super().exec()
            copymove = self.lgclbtngrpCopyMove.checkedId()
            return (
                ret, 
                copymove != self.intCMChoiceMove,   # True unless Move checked
                int(self.combobxMenuID.currentText()) if ret==self.DialogCode.Accepted else None,
                )
    # cEdtMnuDlgCopyMoveMenu

    def __init__(self, parent:QWidget|None = None, MainMenuWindow:QWidget|None = None):

        self.MainMenuWindow = MainMenuWindow
        
        # variables unique to this class
        self._menuSOURCE = MenuRecords()
        self.currentMenu: Dict[int, menuItems] = {}
        self.WmenuItm: Any = [None for bNum in range(_NUM_menuBUTTONS)]    # later - build WmenuItm before this loop?

        super().__init__(parent=parent)
        
        # self.fldmenuGroup = self.fieldDefs['@MenuGroup_id'].get('widget') 
        self.fldmenuGroup = self._lookupFrmElements['@MenuGroup_id']
        self.fldmenuGroup.replaceDict(self.dictmenuGroup())    # type: ignore
        self.fldmenuGroupName = self._formWidgets.get('+GroupName') 
        
        self.loadMenu()
    # __init__

    def _addActionButtons(self, layoutButtons: QBoxLayout | None = None, layoutHorizontal: bool = True, NavActions: List[Tuple[str, QIcon]] | None = None, CRUDActions: List[Tuple[str, QIcon]] | None = None) -> None:
        # there is no button line on this form
        self.btnCommit = self.fieldDefs['+Commit'].get('widget')
        return
    # _addActionButtons
    
    def _finalizeMainLayout(self, layoutMain: QVBoxLayout, items: List | tuple) -> None:
        self._menuSOURCE = MenuRecords()
        
        self.lblnummenuGroupID:  QLCDNumber = QLCDNumber(3)
        self.lblnummenuGroupID.setMaximumSize(20,20)
        self.lblnummenuID:  QLCDNumber = QLCDNumber(3)
        self.lblnummenuID.setMaximumSize(20,20)
        layout = self.FormPage(cQFmConstants.pageFixedTop.value)
        assert layout is not None, "Layout is None"
        layout.addWidget(self.lblnummenuGroupID, 0,1)
        layout.addWidget(self.lblnummenuID, 1,1)

        layoutmainMenu = self.FormPage(0)  # main page
        assert isinstance(layoutmainMenu, QGridLayout), "layoutmainMenu is not a QGridLayout"
        layoutmainMenu.setColumnStretch(0,1)
        layoutmainMenu.setColumnStretch(1,0)
        layoutmainMenu.setColumnStretch(2,1)
        self.layoutmainMenu = layoutmainMenu
        
        bxFrame:List[QFrame] = [QFrame() for _ in range(_NUM_menuBUTTONS)]
        for bNum in range(_NUM_menuBUTTONS):
            bxFrame[bNum].setLineWidth(1)
            bxFrame[bNum].setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
            y, x = ((bNum % _NUM_menuBTNperCOL)+1, 0 if bNum < _NUM_menuBTNperCOL else 2)
            self.layoutmainMenu.addWidget(bxFrame[bNum],y,x)
            
            self.WmenuItm[bNum] = None      # type: ignore  # later - build WmenuItm before this loop?
        
        return super()._finalizeMainLayout(layoutMain, items)
    
    def dictmenuGroup(self) -> Dict[str, int]:
        rs = MenuRecords().recordsetList(['id', 'GroupName'])
        retDict = {d['GroupName']:d['id'] for d in rs}
        return retDict
    def dictmenus(self, mnuGrp:int) -> Mapping[str, int|None]:
        tbl = MenuRecords()
        rs = tbl.recordsetList(['MenuID', 'OptionText'], f'MenuGroup_id = {mnuGrp} AND OptionNumber = 0')
        retDict = Nochoice | {f"{d['OptionText']} ({d['MenuID']})":d['MenuID'] for d in rs}
        return retDict

    ##########################################
    ########    Create

    def createNewMenuGroup(self):
        dlg = self.cEdtMnuDlgGetNewMenuGroupInfo(self)
        retval, grpName, grpInfo = dlg.exec_NewMGInfo()
        if retval:
            # new menuGroups record
            # create a new menu group
            newrec = menuGroups(
                GroupName=grpName,
                GroupInfo=grpInfo,
            )
            with cMenu_Session() as session:
                session.add(newrec)
                session.commit()
                # get the primary key of the new record
                grppk = newrec.id            

            # create a default menu
            # newgroupnewmenu_menulist to menuItems
            for rec in newgroupnewmenu_menulist:
                # rec is a dict with keys: OptionNumber, OptionText, Command, Argument, PWord, TopLine, BottomLine
                # create a new record in menuItems
                newmenurec = menuItems(
                    MenuGroup_id=grppk,
                    MenuID=0,  # default menu ID
                    OptionNumber=rec['OptionNumber'],
                    OptionText=rec['OptionText'],
                    Command=rec['Command'],
                    Argument=rec['Argument'],
                    PWord=rec['PWord'],
                    TopLine=rec['TopLine'],
                    BottomLine=rec['BottomLine'],
                )
                # save the new record
                with cMenu_Session() as session:
                    session.add(newmenurec)
                    session.commit()
                # add the new record to the menuItems table

            self.loadMenu(grppk, 0)
        return

    def copyMenu(self):
        mnuGrp = self.intmenuGroup
        mnuID = self.intmenuID

        dlg = self.cEdtMnuDlgCopyMoveMenu(mnuGrp, mnuID, self)
        retval, CMChoiceCopy, newMnuID = dlg.exec_CMMnu()
        if retval:
            assert isinstance(newMnuID, int) and newMnuID >= 0, "New Menu ID must be a non-negative integer"
            qsFrom = self.currentMenu
            with cMenu_Session() as session:         
                if CMChoiceCopy:
                    qsTo: Dict[int, menuItems] = {}     # qsTo is technically not used, but being built JIC its needed later
                    for i, orig_rec in qsFrom.items():
                        new_rec = menuItems()
                        for col in menuItems.__table__.columns:
                            name = col.name
                            if name != "id":
                                setattr(new_rec, name, getattr(orig_rec, name))
                        #endfor col in menuItems.__table__.columns

                        new_rec.MenuID = newMnuID
                        session.add(new_rec)
                        qsTo[i] = new_rec     # qsTo is technically not used, but being built JIC its needed later
                    #endfor i, orig_rec in qsFrom.items()
                else:
                    # Move the menu items to the new menu ID
                    for i, orig_rec in qsFrom.items():
                        # Update the MenuID of the original record
                        orig_rec.MenuID = newMnuID
                        session.merge(orig_rec)
                    #endfor i, orig_rec in qsFrom.items()
                #endif CMChoiceCopy
                
                session.commit()                # commit the changes
                
                self.loadMenu(mnuGrp, newMnuID)
                
            #endwith cMenu_Session() as session:
        #endif retval

        return
    # copyMenu
        
    def displayMenu(self):
        from cMenu.cMenu import cMenu as cMenuClass

        menuGroup = self.intmenuGroup
        menuID = self.intmenuID
        menuItemRecs = self.currentMenu
        # menuItemRecs.setFilter('OptionNumber=0')
        # menuHdrRec:QSqlRecord = self.movetoutil_findrecwithvalue(menuItemRecs,'OptionNumber',0)
        menuHdrRec:menuItems = menuItemRecs[0]
        
        # set header elements
        self.lblnummenuGroupID.display(menuGroup)
        self.fldmenuGroup.setValue(str(menuGroup)) # type: ignore

        stmt = select(menuGroups.GroupName).where(menuGroups.id == menuGroup)
        with cMenu_Session() as session:
            result = session.execute(stmt)
            group_name = result.scalar_one_or_none()
        GpName = group_name if group_name else ""

        self.fldmenuGroupName.setValue(GpName) # type: ignore
        self.lblnummenuID.display(menuID)
        d = self.dictmenus(menuGroup)
        fldmenuID = self.fieldDefs['@MenuID'].get('widget')        
        fldmenuID.replaceDict(self.dictmenus(menuGroup))  # type: ignore
        fldmenuID.setValue(menuID) # type: ignore
        fldmenuName = self.fieldDefs['OptionText'].get('widget')  # self.fldmenuID.replaceDict(dict(d))
        fldmenuName.setValue(menuHdrRec.OptionText) # type: ignore

        for bNum in range(_NUM_menuBUTTONS):
            y, x = ((bNum % _NUM_menuBTNperCOL)+1, 0 if bNum < _NUM_menuBTNperCOL else 2)
            bIndx = bNum+1
            # mnuItmRc = self.movetoutil_findrecwithvalue(menuItemRecs, 'OptionNumber', bIndx)  # this is safer, but the line below is faster and is same in this case
            mnuItmRc = menuItemRecs.get(bIndx)
            if not mnuItmRc:
                mnuItmRc = menuItems(
                    MenuGroup_id=menuGroup,
                    MenuID=menuID,
                    OptionNumber=bIndx,
                    OptionText = '',
                    Argument = '',
                    PWord = ''
                )
            oldWdg = self.WmenuItm[bNum]
            if oldWdg:
                # remove old widget
                self.layoutmainMenu.removeWidget(oldWdg)
                oldWdg.hide()
                del oldWdg

            self.WmenuItm[bNum] = self.wdgtmenuITEM(mnuItmRc)
            self.WmenuItm[bNum].requestMenuReload.connect(lambda: self.loadMenu(self.intmenuGroup, self.intmenuID))
            if isinstance(self.MainMenuWindow, cMenuClass):
                self.WmenuItm[bNum].requestMenuReload.connect(self.MainMenuWindow.refreshMenu)
            self.layoutmainMenu.addWidget(self.WmenuItm[bNum],y,x) 
        # endfor

        mItmH = self.WmenuItm[0].height()
        mItmW = self.WmenuItm[0].width()
        # self.layoutManinMenu_scrollerWidget.setMinimumSize(mItmW*2+10, mItmH)
        
    # displayMenu

    @Slot()
    def loadMenuWithGroupID(self, menuGroup:int):
        # menuGroup = self.fldmenuGroup.Value()  # type: ignore
        menuID = self.fldmenuID.Value()        # type: ignore
        if menuGroup is None or menuID is None:
            return
        self.loadMenu(int(menuGroup), int(menuID))
    # loadMenuWithGroupID
    @Slot()
    def loadMenuWithMenuID(self, menuID:int):
        # menuID = self.fldmenuID.Value()        # type: ignore
        if menuID is None:
            return
        self.loadMenu(self.intmenuGroup, int(menuID))
    # loadMenuWithMenuID
    @Slot(int, int)
    def loadMenu(self, menuGroup: int = _DFLT_menuGroup, menuID: int = _DFLT_menuID):
        SRC = self._menuSOURCE
        if menuGroup==self._DFLT_menuGroup:
            dfltMenuGroup = SRC.dfltMenuGroup()
            if dfltMenuGroup is None:
                raise ValueError("Default menu group not found.")
            menuGroup = dfltMenuGroup
        if menuID==self._DFLT_menuID:
            dfltMenuID = SRC.dfltMenuID_forGroup(menuGroup)
            if dfltMenuID is None:
                raise ValueError(f"Default menu ID for group {menuGroup} not found.")
            menuID = dfltMenuID

        self.intmenuGroup = menuGroup
        self.intmenuID = menuID
        
        if SRC.menuExist(menuGroup, menuID):
            self.currentMenu = SRC.menuDBRecs(menuGroup, menuID)
            # self.currRec = self.movetoutil_findrecwithvalue(self.currentMenu, 'OptionNumber', 0)
            self.setcurrRec(self.currentMenu[0])  # am I safe in assuming existence?
            self.setDirty(False)       # should this be in displayMenu ?
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

    @Slot(Any)   #type: ignore
    # def changeField(self, wdgt:cQFmFldWidg) -> bool:
    def changeField(self, wdgt, dbField, wdgt_value):

        cRec = self.currRec()

        super().changeField(wdgt, dbField, wdgt_value)
        
        if wdgt_value or isinstance(wdgt_value,bool):
            if dbField != '+GroupName':  # GroupName belongs to cRec.MenuGroup; persist only at final write
                assert cRec is not None, "Current record is None"
                cRec.setValue(str(dbField), wdgt_value)
            wdgt.setDirty(True)
        
            return True
        else:
            return False
        # endif wdgt_value
    # changeField
    
    @Slot()
    def writeRecord(self):
        if not self.isDirty():
            return
        
        cRec = self.currRec()
        
        # check other traps later
        
        # fldmenuGroupName = self.fieldDefs['+GroupName'].get('widget')  # type: ignore
        fldmenuGroupName = self._formWidgets['+GroupName']
        
        if fldmenuGroupName.isDirty():  # type: ignore
            grpstmt = select(menuGroups).where(menuGroups.id == self.intmenuGroup)
            with cMenu_Session() as session:
                groupRec = session.execute(grpstmt).scalar_one_or_none()
                if groupRec is None:
                    print("Menu group not found:", self.intmenuGroup)
                    return
                # update the group name
                groupRec.GroupName = str(fldmenuGroupName.Value())  # type: ignore
                session.merge(groupRec)
                session.commit()
            #endwith cMenu_Session() as session:
        #endif self.isWdgtDirty(self.fldmenuGroupName)

        if cRec is not None:
            with cMenu_Session() as session:
                session.merge(cRec)
                session.commit()

        self.setDirty(False)
    # writeRecord


    ##########################################
    ########    Delete

    @Slot()
    def rmvMenu(self):
        
        pleaseWriteMe('Remove Menu', parent=self)
        return
        
        (mGrp, mnu, mOpt) = (self.currRec().MenuGroup, self.currRec().MenuID, self.currRec().OptionNumber)
        
        # verify delete
        
        # remove from db
        if self.currRec().pk:
            self.currRec().delete()
        
        # replace with an "next" record
        self.setcurrRec(menuItems_QT(
            MenuGroup = mGrp,
            MenuID = mnu,
            OptionNumber = mOpt,
            ))


    ##########################################
    ########    CRUD support

    # @Slot(QWidget, bool)   #type: ignore
    # def setFormDirty(self, wdgt:QWidget, dirty:bool = True):
    #     if wdgt.property('noedit'):
    #         return
        
    #     wdgt.setProperty('dirty', dirty)
    #     # if wdgt === self, set all children dirty
    #     if wdgt is not self:
    #         if dirty: self.setProperty('dirty',True)
    #     else:
    #         for W in self.children():
    #             if isinstance(W, (QLineEdit, QTextEdit, QCheckBox, QComboBox, QDateEdit, )):
    #                 W.setProperty('dirty', dirty)
        
    #     # enable btnCommit if anything dirty
    #     if isinstance(self.btnCommit, QPushButton):
    #         self.btnCommit.setEnabled(self.property('dirty'))
    
    # def isFormDirty(self) -> bool:
    #     return self.property('dirty')

    # def isWdgtDirty(self, wdgt:QWidget) -> bool:
    #     return wdgt.property('dirty')


    ##########################################
    ########    Widget-responding procs

    # def changeInternalVarField(self, wdgt):
    def changeInternalVarField(self, wdgt, intVarField, wdgt_value):
        # '+RmvMenu': {'widgetType': QPushButton, 'label': 'Remove Menu', 'clickedHandler': 'rmvMenu', 
        #     'page': cQFmConstants.pageFixedTop.value, 'position': (1,3), },
        # '+NewMenuGroup': {'widgetType': QPushButton, 'label': 'New Menu Group', 'clickedHandler': 'createNewMenuGroup', 
        #     'page': cQFmConstants.pageFixedTop.value, 'position': (0,4), },
        # '+CopyMenu': {'widgetType': QPushButton, 'label': 'Copy/Move Menu', 'clickedHandler': 'copyMenu', 
        #     'page': cQFmConstants.pageFixedTop.value, 'position': (1,4), },
        # '+Commit': {'widgetType': QPushButton, 'label': 'Save Changes', 'clickedHandler': 'writeRecord', 
        #     'page': cQFmConstants.pageFixedTop.value, 'position': (1,5,2,1), },
        # assert isinstance(wdgt, cQFmFldWidg), "wdgt is not a cQFmFldWidg"
        # intVarField = wdgt.modelField()
        _internalVarFields = {
            '+RmvMenu': self.rmvMenu, 
            '+NewMenuGroup': self.createNewMenuGroup, 
            '+CopyMenu': self.copyMenu, 
            '+Commit': self.writeRecord,
            '+GroupName': lambda: None,  # GroupName belongs to cRec.MenuGroup; persist only at final write
            }
                
        if intVarField in _internalVarFields:
            _internalVarFields[intVarField]()
        # else:
        #     no need to raise error
        #     raise ValueError(f"Unknown internal variable field: {intVarField}")
        # endif
    # changeInternalVarField

# class cWidgetMenuItem
