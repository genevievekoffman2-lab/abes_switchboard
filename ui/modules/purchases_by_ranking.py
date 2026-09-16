from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

from ui.components.date_range_selector import DateRangeSelector
from ui.components.radio_group import RadioGroup


class PurchasesByRanking(QWidget):
    def __init__(self, con):
        super().__init__()
        self.con = con
        self.setWindowTitle("Purchases by Ranking")
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

        # radio buttons
        self.radio_trio = RadioGroup(3, "Ingredients", "Packaging", "All")
        layout.addWidget(self.radio_trio)

        # load button
        self.load_btn = QPushButton("Load")
        self.load_btn.clicked.connect(self.load_clicked)
        layout.addWidget(self.load_btn)

        self.setLayout(layout)


    # logic when load btn is clicked
    def load_clicked(self):
        pass