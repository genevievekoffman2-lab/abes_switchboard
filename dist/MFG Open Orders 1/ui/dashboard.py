# each UI file has a class that extends QWidget and a func to launch it
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QApplication, QGridLayout
)

from db.queries import get_all_cust
from ui.sales_open_orders import MFGReportWindow
from ui.sales_report_module import SalesReportWindow


class Dashboard(QWidget):
    def __init__(self, con):
        super().__init__()
        self.sales_window = None
        self.con = con
        self.setWindowTitle("Switchboard")
        self.setMinimumWidth(500)
        self.setMinimumHeight(500)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Switchboard")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("dashboard_title")
        layout.addWidget(title)

        subtitle = QLabel("Select a module to get started")
        subtitle.setObjectName("dashboard_subtitle")
        layout.addWidget(subtitle)

        # cards grid
        grid = QGridLayout()
        grid.setSpacing(16)

        grid.addWidget(self._make_card("Sales Report", "Rankings by customer & date", "#dbeafe", self.open_sales_report), 0, 0)
        grid.addWidget(self._make_card("Open Orders", "Open orders & total sales ", "#dcfce7", self.open_open_orders), 0, 1)
        grid.addWidget(self._make_card("Module 3", "Coming soon", "#fce7f3", None), 0, 2)

        layout.addLayout(grid)
        layout.addStretch()
        self.setLayout(layout)

    def _make_card(self, title, subtitle, color, on_click):
        card = QPushButton()
        card.setObjectName("dashboard_card")
        card.setMinimumHeight(120)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel(title)
        title_label.setObjectName("card_title")
        card_layout.addWidget(title_label)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("card_subtitle")
        card_layout.addWidget(subtitle_label)

        card.setLayout(card_layout)

        if on_click:
            card.clicked.connect(on_click)

        return card


    # logic when 'sales report' button is clicked
    def open_sales_report(self):
        rows = get_all_cust(self.con)
        customer_names = []  # will hold the names of each customer
        for row in rows:
            customer_names.append(row[0])

        customer_names_sorted = sorted(customer_names)
        self.sales_window = SalesReportWindow(customer_names_sorted, self.con)
        self.sales_window.show()

    def open_open_orders(self):
        self.sales_window = MFGReportWindow(self.con)
        self.sales_window.show()

def run_dashboard(con):
    app = QApplication(sys.argv)

    with open("ui/styles/dashboard.qss", "r") as f:
        app.setStyleSheet(f.read())

    window = Dashboard(con)  # call init
    window.show()
    sys.exit(app.exec())

def closeEvent(self, event):
    event.accept()