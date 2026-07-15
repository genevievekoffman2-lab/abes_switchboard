import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel,
    QListWidget, QVBoxLayout, QAbstractItemView,
    QDateEdit, QHBoxLayout, QPushButton, QMessageBox,
    QRadioButton, QButtonGroup
)
from PyQt6.QtCore import QDate, Qt

from db.queries import get_invoices
from models.invoice_record import InvoiceRecord
from services.aggregators import aggregate_by_customer, aggregate_by_item
from services.generate_excel import open_excel, gen_excel, autosize_columns, format_units
from services.mappers import cast_to_invoice_records
from ui.components.date_range_selector import DateRangeSelector


class SalesReportWindow(QWidget):
    def __init__(self, customers, con):
        super().__init__()
        self.customers = customers
        self.con = con
        self.setMinimumWidth(500)
        self.setWindowTitle("Sales Report")
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

        label = QLabel("Select customers:")
        layout.addWidget(label)

        # customer list
        self.customer_list = QListWidget()
        self.customer_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.customer_list.addItems(self.customers)
        layout.addWidget(self.customer_list)

        # select all button
        self.select_all_btn = QPushButton("☐ Select All")
        self.select_all_btn.setObjectName("select_all_btn")
        self.select_all_btn.setFixedWidth(100)
        layout.addWidget(self.select_all_btn)
        self.select_all_btn.clicked.connect(self.select_all_customers)

        # date range
        date_label = QLabel("Date range")
        layout.addWidget(date_label)

        self.date_selector = DateRangeSelector()
        self.date_selector.setFixedWidth(500)
        layout.addWidget(self.date_selector)

        # by item or by customer button
        self.by_item_btn, self.by_customer_btn, self.btn_group = self.make_radio_pair("View by ", "By Item", "By Customer", layout)

        # include or exclude distributors
        self.include_distr, self.exclude_distr, self.btn_group2 = self.make_radio_pair("Distributors ", "Include Distributors", "Exclude Distributors", layout)

        # generate button
        self.generate_btn = QPushButton("Generate Excel Report")
        self.generate_btn.clicked.connect(self.generate_report)
        layout.addWidget(self.generate_btn)

        self.setLayout(layout)



    # logic when generate report button is pressed
    def generate_report(self):
        selected_customers = [item.text() for item in self.customer_list.selectedItems()]
        from_date, to_date = self.date_selector.get_dates()

        # at least one customer must be selected
        if not selected_customers:
            QMessageBox.warning(self, "Warning", "Please select at least one customer.")
            return

        if from_date > to_date:
            QMessageBox.warning(self, "Warning", "From date must be before To date.")
            return

        # fetch data from Firebird
        fetched_data = get_invoices(self.con, selected_customers, from_date, to_date)
        # cast each sql record to invoiceRecord data type
        invoices = cast_to_invoice_records(fetched_data)

        # if 'exclude distributors' is selected -> remove all records with Distributor flag from invoices
        if self.exclude_distr.isChecked():
            invoices = [r for r in invoices if not r.is_distributor]


        if self.select_all_btn.text() == "☑ Select All":
            customers_str = "All Customers"
        else:
            customers_str = ", ".join(selected_customers)


        if self.by_item_btn.isChecked(): # aggregate the sales by item
            ranked_invoices = aggregate_by_item(invoices)
            excel_headers = ["Product", "Description", "Cat", "Cases", "Sales", "Rank", "%", "% Cumulative"]
            attribute_names = ["product_id", "description", "category", "cases", "sales", "rank", "percent", "cumulative" ]
            sales_col=5
            percent_cols=[7,8]

        else: # aggregate by customer sales
            ranked_invoices = aggregate_by_customer(invoices)
            excel_headers = ["Customer Name", "Cases", "Sales", "Rank", "%", "% Cumulative"]
            attribute_names = ["customer_name", "cases", "sales", "rank", "percent", "cumulative" ]
            sales_col=3
            percent_cols=[5, 6]

        excel_title = f"Sales for the period {from_date} to {to_date}"
        subtitle = f"Ranked by sales from customers: {customers_str}"
        if self.exclude_distr.isChecked(): subtitle += " | Excluding distributors "
        workbook = gen_excel(ranked_invoices, excel_headers, attribute_names, excel_title, subtitle)
        workbook = autosize_columns(workbook, excel_headers)
        workbook = format_units(workbook, sales_col, percent_cols)

        open_excel(workbook)


    def select_all_customers(self):
        all_selected = all(
            self.customer_list.item(i).isSelected()
            for i in range(self.customer_list.count())
        )
        if all_selected:
            #deselect all
            self.customer_list.clearSelection()
            self.select_all_btn.setText("☐ Select All")
        else:
            #select all
            for i in range(self.customer_list.count()):
                self.customer_list.item(i).setSelected(True)
            self.select_all_btn.setText("☑ Select All")

    # creates a radio button pair & returns btn1, btn2, group
    def make_radio_pair(self,label, btn1label, btn2label, layout):
        label = QLabel(label)
        layout.addWidget(label)

        btn1 = QRadioButton(btn1label)
        btn2 = QRadioButton(btn2label)
        btn1.setChecked(True)  # default to firs option

        group = QButtonGroup()
        group.addButton(btn1)
        group.addButton(btn2)

        row = QHBoxLayout()
        row.addWidget(btn1)
        row.addWidget(btn2)
        layout.addLayout(row)

        return btn1, btn2, group

def run_sales_report(customers, con):
    app = QApplication(sys.argv)
    window = SalesReportWindow(customers, con)
    window.show()
    sys.exit(app.exec())


def closeEvent(self, event):
    event.accept()