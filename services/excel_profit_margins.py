from collections import defaultdict
from openpyxl.styles import Alignment, Font

from services.excel_utils import add_titles_and_headers, format_sheet


def load_excel(sheet, headers, title, subtitle, rows):
    add_titles_and_headers(sheet, title, subtitle, headers)

    #group data (puts into dictionary by ADFIELD2 and ADFIELD1
    data = group_data(rows)
    write_dict_into_sheet(sheet, data)
    compute_additional_values(sheet)
    currency_cols = ["E", "F", "G"]  # columns we want to formate as currency
    percent_cols = ["H"]

    format_sheet(sheet, len(headers), currency_cols, percent_cols)

# computes gross contribution and pm % columns
def compute_additional_values(sheet):
    for row in range(5, sheet.max_row + 1):
        e_val = sheet[f"E{row}"].value
        if e_val is not None:
            sheet[f"G{row}"] = f"=E{row}-F{row}"
            sheet[f"H{row}"] = f"=(E{row}-F{row})/E{row}"

# dict: nested dict with key = type and 2nd key = cat
def write_dict_into_sheet(sheet, dict):
    #as we iterate, we also track the subtotals
    sheet.append([])
    grand_ttl_sales, grand_ttl_cost = 0, 0
    for adfield1 in sorted(dict.keys(), key=int):
        inner = dict[adfield1]
        type_ttl_sales, type_ttl_cost = 0, 0
        for adfield2 in sorted(inner.keys(), key=int):
            records_list = inner[adfield2]
            subttl_sales, subttl_cost = 0, 0
            for data in records_list:
                row = (adfield1, adfield2, *data)
                # the * before data unpacks the nested tuple
                sheet.append(row)
                subttl_sales += data[2]
                subttl_cost += data[3]
            sheet.append(["",f"{adfield2} total", "", "", subttl_sales, subttl_cost])
            row_num = sheet.max_row # the row that was just written^
            sheet.cell(row=row_num, column=2).font = Font(bold=True)
            type_ttl_sales += subttl_sales
            type_ttl_cost += subttl_cost

        sheet.append([f"{adfield1} total", "", "", "", type_ttl_sales, type_ttl_cost])
        row_num = sheet.max_row  # the row that was just written^
        sheet.cell(row=row_num, column=1).font = Font(bold=True)
        grand_ttl_sales += type_ttl_sales
        grand_ttl_cost += type_ttl_cost

    sheet.append(["Grand Total", "", "", "", grand_ttl_sales, grand_ttl_cost])
    row_num = sheet.max_row  # the row that was just written^
    sheet.cell(row=row_num, column=1).font = Font(bold=True)

# breaks data into a nested dictionary with key = adfield1 (type) and then key = adfield2 (cat)
def group_data(rows):
    grouped = defaultdict(lambda: defaultdict(list))

    for row in rows:
        adfield2, adfield1, *rest = row
        grouped[adfield1][adfield2].append(tuple(rest))

    group = {k: dict(v) for k, v in grouped.items()}
    return group