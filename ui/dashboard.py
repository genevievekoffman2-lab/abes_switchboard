# each UI file has a class that extends QWidget and a func to launch it
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QApplication, QGridLayout
)

from db.queries import get_all_cust
from ui.modules.comparative_report_module import ComparativeReportWindow
from ui.modules.epr_plastic_tax import EPRWindow
from ui.modules.profit_margin import ProfitMargin
from ui.sales_open_orders import MFGReportWindow
from ui.sales_report_module import SalesReportWindow


class Dashboard(QWidget):
    def __init__(self, con):
        super().__init__()
        self.sales_window = None
        self.con = con
        self.setWindowTitle("Switchboard")
        # window size is 3/4 screen size
        screen = QApplication.primaryScreen().geometry()
        self.resize(int(screen.width() * 0.75), int(screen.height() * 0.75))
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

        grid.addWidget(self._make_card("Sales by Ranking", "Rankings by customer & date", "#dbeafe", self.open_sales_report), 0, 0)
        grid.addWidget(self._make_card("Open Orders", "Open orders & total sales ", "#dcfce7", self.open_open_orders), 0, 1)
        grid.addWidget(self._make_card("Comparative Report", "Sales by item for past 3 years", "dbeafe", self.open_comparative_report), 0, 2)
        grid.addWidget(self._make_card("Profit Margin", "Profit Margin Ranked By Item", "dbeafe", self.open_profit_margin), 0, 3)
        grid.addWidget(self._make_card("EPR", "EPR Sales for plastic tax in 7 states", "dcfce7", self.open_epr_report), 1, 0)
        grid.addWidget(self._make_card("Purchases by Item Ranking", "Coming soon", "#fce7f3", None), 1, 1)
        grid.addWidget(self._make_card("Module 5", "Coming Soon", "#dbeafe", None), 1, 2)

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
        customer_names = fetch_customers(self.con)
        self.sales_window = SalesReportWindow(customer_names, self.con)
        self.sales_window.show()

    def open_open_orders(self):
        self.sales_window = MFGReportWindow(self.con)
        self.sales_window.show()

    def open_comparative_report(self):
        customer_names = fetch_customers(self.con)
        self.sales_window = ComparativeReportWindow(customer_names, self.con)
        self.sales_window.show()

    def open_epr_report(self):
        self.sales_window = EPRWindow(self.con)
        self.sales_window.show()

    def open_profit_margin(self):
        self.sales_window = ProfitMargin(self.con)
        self.sales_window.show()

# grabs list of all customers from DB; sorts them alphabetically
def fetch_customers(con):
    rows = get_all_cust(con)
    customer_names = []
    for row in rows:
        customer_names.append(row[0])

    return sorted(customer_names)

def run_dashboard(con):
    app = QApplication(sys.argv)

    with open("ui/styles/dashboard.qss", "r") as f:
        app.setStyleSheet(f.read())

    window = Dashboard(con)  # call init
    window.show()
    sys.exit(app.exec())

def closeEvent(self, event):
    event.accept()