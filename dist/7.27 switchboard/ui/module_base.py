# each UI file has a class that extends QWidget and a func to launch it
from PyQt6.QtWidgets import QWidget, QVBoxLayout

class ModuleBase(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("module name")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        # add widgets here
        self.setLayout(layout)
