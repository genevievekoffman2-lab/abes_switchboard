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


    Excel should have sections s.t.
        total cheesecake
        total vegan WNR
        total Vegan TD
        total other
        grand total
'''

import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter


category_names = {
    '1' : 'Cheesecake',
    '2' : 'Vegan WNR',
    '3' : 'Vegan TD',
    '7' : 'Distributed'
}

def load_excel(sheet, headers, title, subtitle, data):
    add_titles_and_headers(sheet, title, subtitle, headers)
    add_data(data, sheet, headers)
    format_sheet(sheet)

def add_data(data, sheet, headers):
    row_index = 4
    grand_total_qty = [0, 0, 0]
    grand_total_sales = [0, 0, 0]
    sales_indices = [7,8,9] # adds $ formatting

    order = ['1','2','3','7'] # the order we are outputting in excel sheet
    for cat in order:
        sizes = data[cat]
        # tracks category totals
        cat_total_qty = [0, 0, 0]
        cat_total_sales = [0, 0, 0]

        for size, items in sizes.items():
            # tracks size totals (sub category)
            sz_total_qty = [0,0,0]
            sz_total_sales = [0,0,0]

            # size header row
            sheet.merge_cells(start_row=row_index, start_column=1, end_row=row_index, end_column=len(headers))
            row_index += 1

            # records
            for refid, record in items.items():
                description, qtys, sales = record
                values = [refid, description, qtys[0], qtys[1], qtys[2], "", sales[0], sales[1], sales[2]]
                for col_index, value in enumerate(values, start=1):
                    cell = sheet.cell(row=row_index, column=col_index)
                    cell.value = value
                    if col_index in sales_indices:
                        cell.number_format = "$#,##0"
                row_index += 1


                # calc totals
                for i in range(3):
                    sz_total_qty[i] += qtys[i]
                    sz_total_sales[i] += sales[i]
                    cat_total_qty[i] += qtys[i]
                    cat_total_sales[i] += sales[i]

            # size total row
            sz_total_values = ["", "", sz_total_qty[0], sz_total_qty[1], sz_total_qty[2], "", sz_total_sales[0], sz_total_sales[1], sz_total_sales[2]]
            add_total_rows(sheet, sz_total_values, row_index)
            row_index += 1

        # empty row between sizes
        row_index += 1

        # total of each category
        cat_total_values = ["", f"Total {category_names.get(cat, 'Other')}", cat_total_qty[0], cat_total_qty[1], cat_total_qty[2], "", cat_total_sales[0], cat_total_sales[1], cat_total_sales[2]]
        add_total_rows(sheet, cat_total_values, row_index)

        for i in range(3):
            grand_total_qty[i] += cat_total_qty[i]
            grand_total_sales[i] += cat_total_sales[i]

        # two empty rows between categories
        row_index += 2

        # if we just finished category 3 (Total Vegan TD) -> print the total so far -> this is Total Core
        if cat == '3':
            core_totals = ["", "Total Core", grand_total_qty[0], grand_total_qty[1], grand_total_qty[2], "",
                           grand_total_sales[0], grand_total_sales[1], grand_total_sales[2]]
            add_total_rows(sheet, core_totals, row_index)
            row_index += 2

        #grand totals row
        grand_total_values = ["", "Grand Total", grand_total_qty[0], grand_total_qty[1], grand_total_qty[2], "", grand_total_sales[0], grand_total_sales[1], grand_total_sales[2]]
        add_total_rows(sheet, grand_total_values, row_index)

def add_total_rows(sheet, row, row_index):
    top_border_indices = [3,4,5,7,8,9] # columns that have bold top border
    for col_index, value in enumerate(row, start=1):
        cell = sheet.cell(row=row_index, column=col_index)
        cell.value = value
        cell.font = Font(bold=True)
        if col_index in top_border_indices:
            cell.border = Border(top=Side(style='medium'))  # top border
        if col_index in [7,8,9]: #sales columns
            cell.number_format = "$#,##0"

def format_sheet(sheet):
    col_widths = {
        1: 15,  # item NO
        2: 40,  # description
        3: 10,  # qty2024
        4: 10,  # qty2025
        5: 10,  # qty2026
        6: 12,  # sales2024
        7: 12,  # sales2025
        8: 12,  # sales2026
    }

    for col, width in col_widths.items():
        sheet.column_dimensions[get_column_letter(col)].width = width


def add_titles_and_headers(sheet, title, subtitle, headers):
    # title row
    sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
    title_cell = sheet.cell(row=1, column=1)
    title_cell.value = title
    title_cell.font = Font(bold=True, size=14)
    title_cell.alignment = Alignment(horizontal="center")

    # subtitle
    sheet.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(headers))
    title_cell = sheet.cell(row=2, column=1)
    title_cell.value = subtitle
    title_cell.font = Font(size=12)
    title_cell.alignment = Alignment(horizontal="center", wrap_text=True)

    # write the headers (start on row 3)
    for col, header in enumerate(headers, start=1):
        cell = sheet.cell(row=3, column=col)
        cell.value = header
        cell.font = Font(bold=True,size=12)
