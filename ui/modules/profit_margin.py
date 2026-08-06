from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QButtonGroup, QRadioButton
from openpyxl.chart import layout
from openpyxl.descriptors import container

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
        # add widgets here

        # date range
        date_label = QLabel("Date range")
        layout.addWidget(date_label)

        self.date_selector = DateRangeSelector()
        self.date_selector.setFixedWidth(500)
        layout.addWidget(self.date_selector)

        # radio btns
        self.radio_trio = RadioGroup(3, "Mfg Only", "Distr Only", "All")
        layout.addWidget(self.radio_trio)

        self.setLayout(layout)

