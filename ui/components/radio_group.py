from PyQt6.QtWidgets import QWidget, QVBoxLayout, QButtonGroup, QRadioButton


class RadioGroup(QWidget):
    """
        Builds a group of N radio buttons

        usage:
            group = RadioGroup(3, "apples", "bananas", "oranges")
            group = RadioGroup(3, "apples", "bananas", "oranges", default_index=1)
    """
    def __init__(self, count, *labels, default_index=0):
        super().__init__()

        if len(labels) != count:
            raise ValueError(f"Expected {count} labels, got {len(labels)}")
        if not (0 <= default_index < count):
            raise ValueError(f"Default index {default_index} out of range")

        self.labels = labels
        self.default_index = default_index
        self.button_group = None
        self.buttons = []

        self._build_ui()
        self._load_styles()

    def _load_styles(self):
        pass

    def _build_ui(self):
        layout = QVBoxLayout(self)
        self.button_group = QButtonGroup(self)

        for i, label in enumerate(self.labels):
            rb = QRadioButton(label)
            if i == self.default_index:
                rb.setChecked(True)
            layout.addWidget(rb)
            self.button_group.addButton(rb)
            self.buttons.append(rb)


    # returns the label of the selected radio btn
    def get_selected(self):
        selected = self.button_group.checkedButton()
        return selected.text() if selected else None