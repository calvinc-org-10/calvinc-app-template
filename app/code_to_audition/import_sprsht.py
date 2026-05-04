from datetime import date

from PySide6.QtWidgets import (QWidget, 
    QVBoxLayout, 
    QPushButton, QLabel, QProgressBar, 
    )

from calvincTools.utils import (cExcelFile, str2,)

from database import (get_app_sessionmaker, Repository, )
from models import picklist


class test_spr_import(QWidget):
    tstFile = "D:/tmp0/schedule - Calvin.xlsx"
    sheet = "archive"
    ORMModel = picklist
    ssnmakr = get_app_sessionmaker()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Test SPR Import")

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        layout.addWidget(QLabel(f"Test file: {self.tstFile} - Sheet: {self.sheet}"))
        layout.addSpacing(20)
        
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        layout.addSpacing(20)
        
        self.import_button = QPushButton("Import Spreadsheet")
        self.import_button.clicked.connect(self.import_spreadsheet)
        layout.addWidget(self.import_button)
        
        layout.addSpacing(20)
        
        self.conclusion = QLabel("")
        layout.addWidget(self.conclusion)

    def import_spreadsheet(self):
        excel_file = cExcelFile.load_from_file(self.tstFile)
        if excel_file is None:
            self.conclusion.setText("Import failed: could not load spreadsheet.")
            return
        r = excel_file.save_to_SQLAlchemyModel(
            ssnmaker=self.ssnmakr,
            TargetModel=self.ORMModel,
            WksheetName=self.sheet,
            SprdsheetFlds=self.sprsht_flds(),
            required_columns=["PartNumber", "PKNumber", "intQty"],
            progress_interval=30,
            progress_callback=self.update_progress,
            validation_callback=self.validate_record,
            )
        self.conclusion.setText("Import completed successfully." if r else "Import failed.")
    
    def sprsht_flds(self) -> dict[str, cExcelFile.SprdsheetFldDescriptor]:
        SSFD = cExcelFile.SprdsheetFldDescriptor
        return {
            "Status": SSFD("status"),
            "Priority": SSFD("finishDate", AllowedTypes=(date, type(None))),
            "Part Number": SSFD("PartNumber"), 
            "PK/RP/RF": SSFD("PKNumber"), 
            "WO/MR": SSFD("WONumber", AllowedTypes=(str, type(None)), CleanProc=self.none_to_str,), 
            "REQUESTOR": SSFD("Requestor", AllowedTypes=(str, type(None))), 
            "init qty": SSFD("intQty", AllowedTypes=(int, )), 
            "remain qty": SSFD("remainQty", AllowedTypes=(int, type(None))), 
            "Sales Order #": SSFD("salesOrder"), 
            "Owner": SSFD("owner"), 
            "NOTES": SSFD("notes"),
            }
    
    def none_to_str(self, val) -> tuple[bool, str]:
        return (True, str2(val))
    
    def validate_record(self, record_data) -> bool:
        GPN = record_data.get("PartNumber")
        PK = record_data.get("PKNumber")
        qty = record_data.get("intQty")
        
        # sometimes an expression will come in for qty, so it won't get written to record_data; reject (clean?) those records
        if qty is None:
            return False
            # later, we could try to evaluate the expression and if it resolves to an int, allow the record with that int value for qty
        
        if GPN is None or PK is None:
            return False  # Let other validation rules handle missing required fields
        whereclause = (self.ORMModel.PartNumber == GPN) & (self.ORMModel.PKNumber == PK)
        existing_rec = Repository(self.ssnmakr, self.ORMModel).get_all(whereclause)
        return len(existing_rec) == 0  # Valid if no existing record matches the PartNumber and PKNumber
    
    def update_progress(self, nPct, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(nPct)
    
    def end_of_class(self):
        pass
                
                
######################
