from datetime import date

from PySide6.QtWidgets import (QWidget, 
    QVBoxLayout, 
    QPushButton, QLabel, QProgressBar, 
    )

from calvincTools.utils import cExcelFile

from database import get_app_sessionmaker
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
        excel_file = cExcelFile()
        excel_file.load_from_file(self.tstFile)
        r = excel_file.save_to_SQLAlchemyModel(
            ssnmaker=self.ssnmakr,
            TargetModel=self.ORMModel,
            WksheetName=self.sheet,
            SprdsheetFlds=self.sprsht_flds(),
            required_columns=["PartNumber", "PKNumber", "intQty"],
            progress_interval=30,
            progress_callback=self.update_progress,
            )
        self.conclusion.setText("Import completed successfully." if r else "Import failed.")
    
    def sprsht_flds(self) -> dict[str, cExcelFile.SprdsheetFldDescriptor]:
        SSFD = cExcelFile.SprdsheetFldDescriptor
        return {
            "Status": SSFD("status"),
            "Priority": SSFD("finishDate", AllowedTypes=[date, None]), 
            "Part Number": SSFD("PartNumber"), 
            "PK/RP/RF": SSFD("PKNumber"), 
            "WO/MR": SSFD("WONumber", AllowedTypes=[str, None]), 
            "REQUESTOR": SSFD("Requestor", AllowedTypes=[str, None]), 
            "init qty": SSFD("intQty", AllowedTypes=[int]), 
            "remain qty": SSFD("remainQty", AllowedTypes=[int, None]), 
            "Sales Order #": SSFD("salesOrder"), 
            "Owner": SSFD("owner"), 
            "NOTES": SSFD("notes"),
            }
    
    def update_progress(self, nPct, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(nPct)
    
    def end_of_class(self):
        pass
                
                
######################
