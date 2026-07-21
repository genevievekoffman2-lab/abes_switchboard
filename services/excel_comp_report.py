'''
    Builds the excel report for Comparative Report module from this data structure:
        { category:
            { size :
                { refid : [description, [qty2024,qty2025, qty2026], [sales2024, sales2025, sales2026] ] }
            }
        }

    - one row per item
    - 2 blank rows between categories
    - a grand total row at the very end
    -
'''

import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

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

CATEGORY_NAMES = {
    '1': 'Total Cheesecake',
    '2': 'Total Cheesecake',   # placeholder label per source report
}


def add_titles_and_headers(sheet, title, headers):
    sheet.title = "Comparative Report"


    # write the headers
    for col, header in enumerate(headers, start=1):
        cell = sheet.cell(row=1, column=col)
        cell.value = header

    return sheet

