# module for MFG/Sales/Open orders
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QHeaderView, QTableWidgetItem, \
    QSizePolicy, QApplication

from db.queries import get_total_sales_mfg, get_open_orders_mfg, get_sales_adjustments
from ui.components.date_range_selector import DateRangeSelector


class MFGReportWindow(QWidget):
    def __init__(self, con):
        super().__init__()
        self.con = con
        self.setWindowTitle("MFG open orders")
        # window size is 3/4 screen size
        screen = QApplication.primaryScreen().geometry()
        self.resize(int(screen.width() *0.75),int(screen.height()*0.75))
        self._load_styles()
        self._build_ui()

    def _load_styles(self):
        with open("ui/styles/sales_open_orders.qss", "r") as f:
            self.setStyleSheet(f.read())

    def _build_ui(self):
        layout = QVBoxLayout()

        # date range
        date_label = QLabel("Date range")
        layout.addWidget(date_label)

        self.date_selector = DateRangeSelector()
        self.date_selector.setFixedWidth(300)
        layout.addWidget(self.date_selector)

        # load button
        self.load_btn = QPushButton("Load")
        self.load_btn.setObjectName("load_btn")
        self.load_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.load_btn.adjustSize() # UI for adjusting btn proportionally
        self.load_btn.clicked.connect(self.load_orders)
        layout.addWidget(self.load_btn)

        current_year_h1 = QLabel("Current Year")
        layout.addWidget(current_year_h1)
        self.table = self.build_table()
        layout.addWidget(self.table)

        #previous_year_h1 = QLabel("Previous Year")
        #layout.addWidget(previous_year_h1)
        #self.table = self.build_table()
        #layout.addWidget(self.table)

        self.setLayout(layout)

    def build_table(self):
        SUBMARKETS = [
            "Cheesecake TD",
            "Vegan WNR",
            "Vegan TD",
            "Total Vegan",
            "Total Manufactured",
            "Distributed",
            "Grand Total"
        ]

        # table
        table = QTableWidget()
        # UI resizing proportionally
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        table.setFont(self.font())
        table.setColumnCount(5)
        table.setRowCount(len(SUBMARKETS))
        table.setHorizontalHeaderLabels(["", "Total Sales", "Total Open Orders", "Total Sales Including Open Orders", "Open Orders after to-be shipped date"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # read only
        table.verticalHeader().setVisible(False)  # hide row numbers
        table.setAlternatingRowColors(True)

        # populate first column
        for row_index, market in enumerate(SUBMARKETS):
            table.setItem(row_index, 0, QTableWidgetItem(market))

        return table

    # logic when load button is pressed
    def load_orders(self):
        from_date, to_date = self.date_selector.get_dates()
        print("loading orders")

        #TODO make sure the dates are selected

        # structure to fill before writing into table
        market_data = {
            "Cheesecake TD": [0, 0, 0, 0],
            "Vegan WNR": [0, 0, 0, 0],
            "Vegan TD": [0, 0, 0, 0],
            "Total Vegan": [0, 0, 0, 0],
            "Total Manufactured": [0, 0, 0, 0],
            "Distributed": [0, 0, 0, 0],
            "Grand Total": [0, 0, 0, 0]
        }

        # lookup dictionary (we get cat back from DB)
        cat_to_market = {
            '1' : 'Cheesecake TD',
            '2' : 'Vegan WNR',
            '3' : 'Vegan TD',
            '7' : 'Distributed'
        }

        # fetch data from Firebird
        fetched_sales = get_total_sales_mfg(self.con, from_date, to_date)
        for cat, sales in fetched_sales:
            market_name = cat_to_market.get(cat)
            if market_name:
                market_data[market_name][0] = sales

        fetched_open_orders = get_open_orders_mfg(self.con, from_date, to_date, False)
        for cat, open_orders in fetched_open_orders:
            market_name = cat_to_market.get(cat)
            if market_name:
                market_data[market_name][1] = open_orders

        fetched_future_open_orders = get_open_orders_mfg(self.con, from_date, to_date, True)
        for cat, future_open_orders in fetched_future_open_orders:
            market_name = cat_to_market.get(cat)
            if market_name:
                market_data[market_name][3] = future_open_orders

        # check for any accounting adjustments
        adjustments = get_sales_adjustments(self.con, from_date, to_date)
        self.update_with_adjustments(market_data, adjustments)

        # after filled, fill the totals
        self.calculate_totals(market_data)
        self.fill_table(market_data)

    # fills in the total vegan, total manufactured, & grand total
    def calculate_totals(self, market_data):
        # sum the first two values for each market to get 'total sales + open orders'
        for market, values in market_data.items():
            values[2] = values[0] + values[1]

        # total vegan = vegan WNR + vegan TD
        for i in range(4):
            market_data["Total Vegan"][i] = (market_data["Vegan TD"][i] + market_data["Vegan WNR"][i])

        # total manufactured = total vegan + cheesecake TD
        for i in range(4):
            market_data["Total Manufactured"][i] = (market_data["Total Vegan"][i] + market_data["Cheesecake TD"][i])

        # grand total = total manufactured + distributed
        for i in range(4):
            market_data["Grand Total"][i] = (market_data["Total Manufactured"][i] + market_data["Distributed"][i])

        return market_data

    # fills the cells in the UI table using market_data
    def fill_table(self, market_data):
        for row_index, (market, values) in enumerate(market_data.items()):
            for col_index, value in enumerate(values, start=1):
                item = QTableWidgetItem(f"${value:,.2f}")
                # self.set_cell(f"${value:,.2f}", row_index, col_index)

                # adds UI highlighting for grand total row TODO: fix this; row is not being highlighted
                if row_index == self.table.rowCount() - 1:
                    item.setBackground(QColor("#dbeafe"))
                    item.setForeground(QColor("#1d4ed8"))
                self.table.setItem(row_index, col_index, item)

    # accounting adjustments will update the Total Sales column for Vegan WNR
    def update_with_adjustments(self, market_data, adjustments):
        # tuples from DB come in form (debit, credit)
        total = 0
        # calculate the total sum of numbers (debit is negative, credit is positive)
        for debit, credit in adjustments:
            total += credit - debit

        # update the value for Total Sales and vegan WNR
        market_data["Vegan WNR"][0] += total