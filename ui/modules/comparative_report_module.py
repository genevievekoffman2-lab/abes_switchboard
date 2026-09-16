import openpyxl
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QApplication
from dateutil.relativedelta import relativedelta
import pprint

from db.queries import get_sales_by_item_cr
from services.excel_comp_report import load_excel
from services.excel_sales_report import open_excel
from ui.components.customer_selection import CustomerSelection
from ui.components.date_range_selector import DateRangeSelector
from ui.components.loading_spinner import LoadingSpinner
from ui.components.worker import Worker


class ComparativeReportWindow(QWidget):
    def __init__(self, customers, con):
        super().__init__()
        self.customers = customers
        self.con = con
        self.setWindowTitle("Comparative Report")
        # window size is 3/4 screen size
        screen = QApplication.primaryScreen().geometry()
        self.resize(int(screen.width() * 0.5), int(screen.height() * 0.75))
        self._load_styles()
        self._build_ui()

    def _load_styles(self):
        with open("ui/styles/sales_report.qss", "r") as f:
            self.setStyleSheet(f.read())

    def _build_ui(self):
        layout = QVBoxLayout()

        # date range
        date_label = QLabel("Date range")
        date_label.setObjectName("h1")
        layout.addWidget(date_label)

        self.date_selector = DateRangeSelector()
        self.date_selector.setFixedWidth(500)
        layout.addWidget(self.date_selector)

        self.customer_selector = CustomerSelection(self.customers)
        layout.addWidget(self.customer_selector)

        self.generate_btn = QPushButton("Load Excel Report")
        self.generate_btn.setObjectName("LoadBtn")
        self.generate_btn.clicked.connect(self.generate_report)
        layout.addWidget(self.generate_btn)
        # load spinner
        self.spinner = LoadingSpinner(parent=self, size=28)

        self.setLayout(layout)


    # logic when load button is clicked
    def generate_report(self):
        selected_customers = self.customer_selector.get_selected_customers()
        from_date, to_date = self.date_selector.get_dates()

        # at least one customer must be selected
        if not selected_customers:
            QMessageBox.warning(self, "Warning", "Please select at least one customer.")
            return

        if from_date > to_date:
            QMessageBox.warning(self, "Warning", "From date must be before To date.")
            return

        # begin the spinner
        self.spinner.start()
        self.worker = Worker(self.fetch_data, from_date, to_date, selected_customers)
        self.worker.finished.connect(
            lambda result: self.on_done(result, from_date, to_date, selected_customers)
        ) # done fetching data
        self.worker.error.connect(self.on_error)
        self.worker.start()

    # when fetch_data is done running - thread returns here
    def on_done(self, ds, from_date, to_date, selected_customers):
        # generate excel
        excel_title = f"Sales by Category {from_date} - {to_date}"
        subtitle = f"For Customer(s): {selected_customers}"
        excel_headers = ["Item No", "Description", "QTY 2024", "QTY 2025", "QTY 2026", "", "Sales 2024", "Sales 2025",
                         "Sales 2026", "", "2024", "2025", "2026", "", "2024", "2025", "2026"]

        self.load_excel(ds, excel_title, subtitle, excel_headers)
        self.close() # closes comp report window

    def fetch_data(self, from_date, to_date, selected_customers):
        # fetch data from Firebird
        fetched_data_26 = get_sales_by_item_cr(self.con, selected_customers, from_date, to_date)
        fetched_data_25 = get_sales_by_item_cr(self.con, selected_customers, (from_date - relativedelta(years=1)),
                                               (to_date - relativedelta(years=1)))
        fetched_data_24 = get_sales_by_item_cr(self.con, selected_customers, (from_date - relativedelta(years=2)),
                                               (to_date - relativedelta(years=2)))
        ds = self.organize_by_category(fetched_data_24, fetched_data_25, fetched_data_26)

        return ds

    def load_excel(self, data, title, subtitle, headers):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Comparative Report"

        load_excel(sheet, headers, title, subtitle, data)
        open_excel(workbook)

    # builds a nested dictionary from the fetched data
    # a dictionary of key = category (adfield2) & value = another dic
    # sub dict is key = size (adfield3)
    # (item no, descript, qty24, '25, '26, sales24, '25, 26, % of total sales, % oc core sales, % incr in sales)
    def organize_by_category(self, data24, data25, data26):
        temp = {}
        # category(adfield2) : { size(adfield3) : { refid: [descript, [0,0,0], [0,0,0] } }
        def add_rows(rows, year_index):
            for refid, descr, cat, size, qty, sales in rows:
                if cat not in temp:
                    temp[cat] = {}
                if size not in temp[cat]:
                    temp[cat][size] = {}
                if refid not in temp[cat][size]:
                    temp[cat][size][refid] = [descr, [0,0,0], [0,0,0]]
                        #first tuple of 0s is quantity '24 '25 '26
                        #2nd tuple of 0s is sales '24 '25 '26
                temp[cat][size][refid][1][year_index] = qty
                temp[cat][size][refid][2][year_index] = sales

        add_rows(data24, 0)
        add_rows(data25, 1)
        add_rows(data26, 2)

        # sort categories ascending numerically and sizes within each cat
        sorted_temp = {
            cat: {
                size: temp[cat][size]
                for size in sorted(temp[cat], key=int)
            }
            for cat in sorted(temp, key=int)
        }

        return sorted_temp

    def on_error(self, e):
        self.spinner.stop()
        self.generate_btn.setEnabled(True)
        print(f"Load failed: {e}")