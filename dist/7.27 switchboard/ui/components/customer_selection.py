from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QAbstractItemView, QPushButton


class CustomerSelection(QWidget):
    def __init__(self, customers: list):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        cust_label = QLabel("Select customers:")
        cust_label.setObjectName("h1")
        layout.addWidget(cust_label)

        # customer list
        self.customer_list = QListWidget()
        self.customer_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.customer_list.addItems(customers)
        layout.addWidget(self.customer_list)

        # select all button
        self.select_all_btn = QPushButton("☐ Select All")
        self.select_all_btn.setObjectName("select_all_btn")
        self.select_all_btn.setFixedWidth(100)
        layout.addWidget(self.select_all_btn)
        self.select_all_btn.clicked.connect(self.select_all_customers)

        self.setLayout(layout)

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

    def get_selected_customers(self):
        return [item.text() for item in self.customer_list.selectedItems()]

    # returns True if all customers are selected
    def is_select_all(self):
        return self.select_all_btn.text() == "☑ Select All"