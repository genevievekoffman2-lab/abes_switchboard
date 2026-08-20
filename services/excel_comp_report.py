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
import pprint
from asyncio.windows_events import NULL

import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

from services.excel_utils import format_sheet

category_names = {
    '1' : 'Cheesecake',
    '2' : 'Vegan WNR',
    '3' : 'Vegan TD',
    '7' : 'Distributed'
}

def load_excel(sheet, headers, title, subtitle, data):
    add_titles_and_headers(sheet, title, subtitle, headers)
    rows = flatten_data(data)
    loadRows(sheet, rows)
    format_sheet(sheet, len(headers),["G", "H", "I"],["K", "L", "M", "O", "P", "Q"])

def loadRows(sheet, rows):
    row_num = 5
    for row in rows:
        r = []
        if row["type"] == "record":
            flatten(row["data"], r)
            write_row(sheet, row_num, r)
        elif row["type"] == "ttl size":
            total_row = ["", "", row["total qty"], "", row["total sales"]]
            flatten(total_row, r)
            add_total_rows(sheet, r, row_num)
            row_num += 1
            pass
        elif row["type"] == "total cat" or row["type"] == "total core" or row["type"] == "grand total":
            total_row = ["", f"{row["label"]}", row["total qty"], "", row["total sales"], "", row.get("sales_ratios", []), "", row.get("core_ratios", [])]
            flatten(total_row, r)
            add_total_rows(sheet, r, row_num)
            row_num += 1
        else:
            write_row(sheet, row_num, row)
        row_num += 1

# breaking a nested list into a flat list
def flatten(value, row):
    if isinstance(value, list):
        for v in value:
            flatten(v, row)
    else:
        row.append(value)


def write_row(sheet, row_index, row):
    for col, value in enumerate(row, start=1):
        sheet.cell(row=row_index, column=col).value = value


# make all the data into a list of records prepared to print
# adds total rows
# outputs a list of [print format, data]
def flatten_data(data):
    rows = []
    grand_total_qty = [0, 0, 0]
    grand_total_sales = [0, 0, 0]
    sorted_cat = sorted(data.keys())

    for cat in sorted_cat:
        sizes = data.get(cat)
        # tracks category totals
        cat_total_qty, cat_total_sales = [0, 0, 0], [0, 0, 0]

        # cont as long as there's rec in the category
        for size, items in sizes.items():
            # tracks size totals (sub category)
            sz_total_qty, sz_total_sales = [0,0,0], [0,0,0]

            # records
            for refid, (description, qtys, sales) in items.items():
                rec = {
                    "type" : "record",
                    "category": cat,
                    "size": size,
                    "data" : [refid, description, qtys, "", sales] #qtys & sales is form: [x,x,x] "" is empty col
                }
                rows.append(rec)
                # compute total of size (sub cat)
                sz_total_qty = [a + b for a,b in zip(sz_total_qty, qtys)]
                sz_total_sales = [a + b for a,b in zip(sz_total_sales, sales)]

            # add the sub cat (size) total row
            rows.append({
                "type": "ttl size",
                "category": cat,
                "size": size,
                "total qty": sz_total_qty,
                "total sales": sz_total_sales
            })
            cat_total_qty = [a+b for a,b in zip(cat_total_qty, sz_total_qty)]
            cat_total_sales = [a+b for a,b in zip(cat_total_sales, sz_total_sales)]

        # add the category totals
        rows.append({
            "type": "total cat",
            "label": f"Total {category_names.get(cat, 'Other')}",
            "total qty": cat_total_qty,
            "total sales": cat_total_sales
        })
        grand_total_qty = [a+b for a,b in zip(grand_total_qty, cat_total_qty)]
        grand_total_sales = [a+b for a,b in zip(grand_total_sales, cat_total_sales)]

        # add a total core row after category 3
        if cat == '3':
            rows.append({
                "type" : "total core",
                "label" : "Total Core",
                "total qty": grand_total_qty,
                "total sales": grand_total_sales
            })
            # compute '% of Core Sales'
            compute_percents(rows, grand_total_sales, "core_ratios")

    # add the grand category totals
    rows.append({
        "type": "grand total",
        "label": "Grand Total",
        "total qty": grand_total_qty,
        "total sales": grand_total_sales
    })

    compute_percents(rows, grand_total_sales, "sales_ratios")
    return rows

# adds percentage of sales to a total row; key_name: [x,x,x]
def compute_percents(rows, ttl_sales, key_name):
    for row in rows:
        if "total" in row["type"]:
            row[key_name] = get_sales_ratio(row["total sales"], ttl_sales)

# given the sales and grand sales, computes the ratio and returns it [x,x,x]
def get_sales_ratio(total_sales, grand_total_sales):
    return [
            sales / grand if grand else None
            for sales, grand in zip(total_sales, grand_total_sales)
        ]

def add_total_rows(sheet, row, row_index):
    top_border_indices = [3,4,5,7,8,9] # columns that have bold top border
    for col_index, value in enumerate(row, start=1):
        cell = sheet.cell(row=row_index, column=col_index)
        cell.value = value
        cell.font = Font(bold=True)
        if col_index in top_border_indices:
            cell.border = Border(top=Side(style='medium'))  # top border

def add_titles_and_headers(sheet, title, subtitle, headers):
    # title row
    sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
    title_cell = sheet.cell(row=1, column=1)
    title_cell.value = title
    title_cell.font = Font(bold=True, size=14)
    title_cell.alignment = Alignment(horizontal="center")

    # subtitle
    sheet.merge_cells(start_row=2, start_column=1, end_row=2, end_column=5)
    title_cell = sheet.cell(row=2, column=1)
    title_cell.value = subtitle
    title_cell.font = Font(size=12)
    title_cell.alignment = Alignment(horizontal="center", wrap_text=True)

    # added % labels into subtitle row
    sheet.merge_cells(start_row=2, start_column=11, end_row=2, end_column=13)
    percent_label = sheet.cell(row=2, column=11)
    percent_label.value = "% of Sales"
    percent_label.alignment = Alignment(horizontal="center", wrap_text=True)
    sheet.merge_cells(start_row=2, start_column=15, end_row=2, end_column=18)
    percent_label2 = sheet.cell(row=2, column=15)
    percent_label2.value = "% of Core Sales"
    percent_label2.alignment = Alignment(horizontal="center", wrap_text=True)

    # write the headers (start on row 3)
    for col, header in enumerate(headers, start=1):
        cell = sheet.cell(row=3, column=col)
        cell.value = header
        cell.font = Font(bold=True,size=12)
