from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QAbstractItemView, QPushButton

from ui.components.date_range_selector import DateRangeSelector


class ComparativeReportWindow(QWidget):
    def __init__(self, customers, con):
        super().__init__()
        self.customers = customers
        self.con = con
        self.setWindowTitle("Comparative Report")
        self._load_styles()
        self._build_ui()

    def _load_styles(self):
        with open("ui/styles/comparative_report.qss", "r") as f:
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


        cust_label = QLabel("Select customers:")
        cust_label.setObjectName("h1")
        layout.addWidget(cust_label)

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
        # self.select_all_btn.clicked.connect(self.select_all_customers)


        self.setLayout(layout)