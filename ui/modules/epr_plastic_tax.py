# each UI file has a class that extends QWidget and a func to launch it
import os

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication, QPushButton
from openpyxl.reader.excel import load_workbook

from services.excel_sales_report import open_excel


class EPRWindow(QWidget):
    def __init__(self, con):
        super().__init__()
        self.con = con
        self.setWindowTitle("EPR Sales Plastic Tax")
        self._load_styles()
        self._build_ui()

    def _load_styles(self):
        with open("ui/styles/epr_sales.qss", "r") as f:
            self.setStyleSheet(f.read())

    def _build_ui(self):
        layout = QVBoxLayout()
        # add widgets here
        description = QLabel("EPR Sales Report | 2025")
        description.setObjectName("description")
        layout.addWidget(description)

        self.load_btn = QPushButton("Load for 2025")
        self.load_btn.clicked.connect(self.load_report)

        layout.addWidget(self.load_btn)
        self.setLayout(layout)

    def load_report(self):
        os.startfile("Y:/Genevieve/EPR Reporting/2025.xlsx")