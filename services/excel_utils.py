# shared excel funcs across all modules
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter


# formats the Excel sheet: adding width of columns and percent/number formatting
# should be performed last, after cells are filled with data
# currency & percent cols: list of column letters needing the formatting
# col_widths: dictionary with key = col letter & value = length
def format_sheet(sheet, col_count, currency_cols, percent_cols):

    # for col, width in col_widths.items():
    #     sheet.column_dimensions[col].width = width

    autosize_columns(sheet, col_count)

    for col in currency_cols:
        for row in range(4, sheet.max_row + 1):
            cell = sheet[f"{col}{row}"]
            cell.number_format = '$#,##0.00'

    for col in percent_cols:
        for row in range(4, sheet.max_row + 1):
            cell = sheet[f"{col}{row}"]
            cell.number_format = '0.0%'


def autosize_columns(sheet, columns):
    # autosize columns
    for col_index in range(1, columns + 1):
        col_letter = get_column_letter(col_index)
        max_len = 0
        for row in sheet.iter_rows(min_row=3,max_col=col_index,min_col=col_index): #skips over first 3 rows when calculating width
            for cell in row:
                try:
                    if cell.value:
                        max_len = max(max_len, len(str(cell.value)))
                except:
                    pass
        sheet.column_dimensions[col_letter].width = max_len + 2
    return sheet

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
    subtitle_cell.alignment = Alignment(horizontal='center', shrink_to_fit=True)

    # write the headers (start on row 3)
    for col, header in enumerate(headers, start=1):
        cell = sheet.cell(row=3, column=col)
        cell.value = header
        cell.font = Font(bold=True, size=12)
        cell.alignment = Alignment(horizontal='center')

    return sheet