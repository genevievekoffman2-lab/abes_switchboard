import openpyxl
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox

from db.queries import get_sales_and_cost
from services.excel_logic import load_excel
from services.generate_excel import open_excel
from ui.components.date_range_selector import DateRangeSelector
from ui.components.radio_group import RadioGroup


class ProfitMargin(QWidget):
    def __init__(self, con):
        super().__init__()
        self.con = con
        self.setWindowTitle("Profit Margin")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        # date range
        date_label = QLabel("Date range")
        layout.addWidget(date_label)

        self.date_selector = DateRangeSelector()
        self.date_selector.setFixedWidth(500)
        layout.addWidget(self.date_selector)

        # radio btns
        self.radio_trio = RadioGroup(3, "Mfg Only", "Distr Only", "All")
        layout.addWidget(self.radio_trio)

        #load btn
        self.load_btn = QPushButton("Load")
        self.load_btn.clicked.connect(self.load_clicked)
        layout.addWidget(self.load_btn)

        self.setLayout(layout)


    #logic when load button is clicked
    def load_clicked(self):
        from_date, to_date = self.date_selector.get_dates()

        if from_date > to_date:
            QMessageBox.warning(self, "Warning", "From date must be before To date.")
            return

        #fetch data from firebird
        rows = self.fetch_data(from_date, to_date)
        #TODO: should i group (build the dict here) or in excel logic
        self.generate_excel(rows)

    def fetch_data(self, from_date, to_date):
        rows = get_sales_and_cost(self.con, from_date, to_date)
        return rows

    def generate_excel(self, rows):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        title = "Profit Margin"
        subtitle = "From date to date"
        headers = ["type", "cat","Item ID", "Description", "total sales", "total cost", "Gross Contribution", "PM%"]

        load_excel(sheet, headers, title, subtitle, rows)
        open_excel(workbook)