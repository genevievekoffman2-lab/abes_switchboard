import openpyxl
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox

from db.queries import get_sales_and_cost
from services.excel_profit_margins import load_excel
from services.excel_sales_report import open_excel
from ui.components.date_range_selector import DateRangeSelector
from ui.components.radio_group import RadioGroup


class ProfitMargin(QWidget):
    def __init__(self, con):
        super().__init__()
        self.con = con
        self.setWindowTitle("Profit Margin")
        self._load_styles()
        self._build_ui()

    def _load_styles(self):
        with open("ui/styles/sales_report.qss", "r") as f:
            self.setStyleSheet(f.read())

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

        #check which radio btn is selected
        selected = self.radio_trio.get_selected()
        # fetch data from firebird
        rows = self.fetch_data(from_date, to_date, selected)
        self.generate_excel(from_date, to_date, rows)

    def fetch_data(self, from_date, to_date, category):
        if category == "All":
            rows = get_sales_and_cost(self.con, from_date, to_date)
        elif category == "Distr Only":
            rows = get_sales_and_cost(self.con, from_date, to_date, "Distributed")
        elif category == "Mfg Only":
            rows = get_sales_and_cost(self.con, from_date, to_date, "Mfg")
        return rows

    def generate_excel(self, from_date, to_date, rows):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        title = "Profit Margin Ranked By Item"
        subtitle = f"From {from_date} to {to_date}"
        headers = ["size", "cat", "Item ID", "Description", "Total Sales", "Total Cost", "Gross Contribution", "PM%",
                   "", "% of C Sales", "% of C Mar", "", "% of T Sales", "% of T Mar"]

        load_excel(sheet, headers, title, subtitle, rows)
        open_excel(workbook)