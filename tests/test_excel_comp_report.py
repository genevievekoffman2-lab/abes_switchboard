import os

import openpyxl

from services.excel_comp_report import add_titles_and_headers, add_data, format_sheet, load_excel

data = {
    '1': {
        '6': {'SF194DB': ['Cheesecake - Vanilla Bean 2"',
                           [398, 532, 880],
                           [28385, 40672, 68585]]},
        '19': {'MIDI190': ['Flourless - Chocolate MIDI',
                            [588, 561, 758],
                            [24631, 25148, 34722]],
               'MIDI194': ['Cheesecake - Vanilla Bean MIDI',
                            [777, 754, 942],
                            [32549, 33796, 43144]],
               'ZSF202D': ['DO NOT USE Explosion - Chocolate 3"',
                            [206, 98, 0],
                            [12570, 6386, 0]]},
        '3': {'SF184D': ['Mousse - Triple Chocolate 3"',
                          [180, 228, 210],
                          [11502, 15567, 14670]],
              'SF189D': ['Layer - Carrot 3"',
                          [170, 142, 144],
                          [10863, 9214, 9565]]},
    },
    '2': {
        '350': {'ABE350': ["Vegan Square Cake - ABE'S Corn Bread",
                            [60, 110, 140],
                            [1154, 2194, 2930]]},
    },
}

def test_excel_comp_report():
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Comparative Report"
    headers = ["Item No", "Description", "QTY 2024", "QTY 2025", "QTY 2026", "", "Sales 2024", "Sales 2025", "Sales 2026"]
    load_excel(sheet, headers, "Comparative Report", data)
    workbook.save("tmp.xlsx")
    os.startfile("tmp.xlsx")
