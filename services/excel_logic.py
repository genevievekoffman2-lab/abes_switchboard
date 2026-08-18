from collections import defaultdict
from openpyxl.styles import Alignment, Font


def load_excel(sheet, headers, title, subtitle, rows):
    add_titles_and_headers(sheet, title, subtitle, headers)

    #group data (puts into dictionary by ADFIELD2 and ADFIELD1
    data = group_data(rows)
    write_dict_into_sheet(sheet, data)
    compute_additional_values(sheet)
    format_sheet(sheet)

# computes gross contribution and pm % columns
def compute_additional_values(sheet):
    for row in range(5, sheet.max_row + 1):
        e_val = sheet[f"E{row}"].value
        if e_val is not None:
            sheet[f"G{row}"] = f"=E{row}-F{row}"
            sheet[f"H{row}"] = f"=(E{row}-F{row})/E{row}"

#TODO: make format sheet take col_widths and currency_cols etc to use in every module
def format_sheet(sheet):
    col_widths = {
        "A": 10,
        "B": 10,
        "C": 10,
        "D": 30,
        "E": 20,
        "F": 20,
        "G": 20
    }

    currency_cols = ["E", "F", "G"] # columns we want to formate as currency
    percent_cols = ["H"]

    for col, width in col_widths.items():
        sheet.column_dimensions[col].width = width

    for col in currency_cols:
        for row in range(4, sheet.max_row + 1):
            cell = sheet[f"{col}{row}"]
            cell.number_format = '$#,##0.00'

    for col in percent_cols:
        for row in range(4, sheet.max_row + 1):
            cell = sheet[f"{col}{row}"]
            cell.number_format = '0.0%'

# dict: nested dict with key = type and 2nd key = cat
def write_dict_into_sheet(sheet, dict):
    row_num = 5 #start on row 5
    for adfield1 in sorted(dict.keys()):
        inner = dict[adfield1]
        for adfield2 in sorted(inner.keys()):
            records_list = inner[adfield2]
            for data in records_list:
                row = (adfield1, adfield2, *data)
                # the * before data unpacks the nested tuple
                sheet.append(row)
            sheet.append([])

# writes the contents of row into the row at index row_index
# row: flat list
def write_row(sheet, row_index, row):
    for col, value in enumerate(row, start=1):
        sheet.cell(row=row_index, column=col).value = value

# writes the title on 1st row
# writes the subtitle on 2nd row
# writes the headers for each column on 3rd row
def add_titles_and_headers(sheet, title, subtitle, headers):
    sheet.title = title
    sheet.row_dimensions[1].height = 40

    # add title row
    sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
    title_cell = sheet.cell(row=1, column=1)
    title_cell.value = f"{title}"
    title_cell.font = Font(bold=True, size=14)
    title_cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    # add subtitle row
    sheet.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(headers))
    subtitle_cell = sheet.cell(row=2, column=1)
    subtitle_cell.value = f"{subtitle}"
    subtitle_cell.font = Font(size=12)
    subtitle_cell.alignment = Alignment(horizontal='center', wrap_text=True)

    # write the headers (start on row 3)
    for col, header in enumerate(headers, start=1):
        cell = sheet.cell(row=3, column=col)
        cell.value = header
        cell.font = Font(bold=True, size=12)
        cell.alignment = Alignment(horizontal='center')

    return sheet

# breaks data into a nested dictionary with key = adfield1 (type) and then key = adfield2 (cat)
def group_data(rows):
    grouped = defaultdict(lambda: defaultdict(list))

    for row in rows:
        adfield2, adfield1, *rest = row
        grouped[adfield1][adfield2].append(tuple(rest))

    group = {k: dict(v) for k, v in grouped.items()}
    return group