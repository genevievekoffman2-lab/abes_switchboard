from PyQt6.QtCore import QDate, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QDateEdit, QLabel, QSizePolicy


class DateRangeSelector(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self._load_styles()

    def _load_styles(self):
        with open("ui/styles/date_range_selector.qss", "r") as f:
            self.setStyleSheet(f.read())

    def _build_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate(2026, 7, 1))

        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())

        layout.addWidget(QLabel("From"))
        layout.addWidget(self.from_date)
        layout.addWidget(QLabel("To"))
        layout.addWidget(self.to_date)
        self.setLayout(layout)

    def get_dates(self):
        return self.from_date.date().toPyDate(), self.to_date.date().toPyDate()