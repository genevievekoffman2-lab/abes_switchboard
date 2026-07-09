import openpyxl
from openpyxl.styles import Font, Alignment
import os
import tempfile

from models.invoice_record import InvoiceRecord
from models.ranked_invoice_record import RankedInvoiceRecord
from services.aggregators import group_by_category
from services.mappers import transform_invoiceRecord_rankedInvoiceRecord


# ranked records: list of rankedInvoiceRecord objects
# headers: the name of each column
# attribute_names: must match the size of headers; used to access each value in record obj
def gen_excel(ranked_records, headers, attribute_names, title, subtitle):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet = add_titles_and_headers(sheet, title, subtitle, headers)

    # group records by category
    categories = group_by_category(ranked_records)
    processed_data = process_each_category(categories)

    # write all the data rows (begins on 4th row)
    # we loop over attribute_names for every InvoiceRecord in processed_data
    row_index = 4
    for rec in processed_data:
        if rec is None:
            row_index += 1
            continue

        for col_index, attr_name in enumerate(attribute_names, start = 1):
            value = rec.get_attribute(attr_name)
            sheet.cell(row=row_index, column=col_index).value = value

        row_index += 1

    return workbook

# writes the title on 1st row
# writes the subtitle on 2nd row
# writes the headers for each column on 3rd row
def add_titles_and_headers(sheet, title, subtitle, headers):
    sheet.title = "Sales Report"
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


def open_excel(workbook):
    # save to a temp file
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp:
        tmp_path = temp.name
    workbook.save(tmp_path)
    os.startfile(tmp_path)


# computes the total cases, sales and percents of each category & adds the total row
def process_each_category(categories):
    sorted_records = []
    grand_total_cases = 0
    grand_total_sales = 0

    for category in sorted(categories.keys()): # for each category
        records = categories[category]
        ranked_records = cast_and_sort_rankedInvoices(records) #cast to RankedInvoiceRecords
        sorted_records.extend(ranked_records)

        # add row with totals
        total_cases = sum(r.record.cases for r in ranked_records)
        total_sales = sum(r.record.sales for r in ranked_records)
        total_percent = sum(r.percent for r in ranked_records)
        grand_total_cases += total_cases
        grand_total_sales += total_sales

        total_invoice = InvoiceRecord(
            customer_name="Total",
            cases=total_cases,
            sales=total_sales,
            description="Total"
        )
        total_row = RankedInvoiceRecord(
            record=total_invoice,
            rank=None,
            percent=round(total_percent, 2), #should round to 100%
            cumulative=None
        )
        sorted_records.append(total_row)
        sorted_records.append(None)  # empty cells for spacing
        sorted_records.append(None)

    # add the grand total row
    grand_total_row = RankedInvoiceRecord(
        record=InvoiceRecord("Grand Total", grand_total_cases, grand_total_sales, "Grand Total"),
        rank=None,
        percent=None,
        cumulative=None
    )

    sorted_records.append(grand_total_row)
    return sorted_records

# input: a list of InvoiceRecord objects
# outputs: a list of RankedInvoiceRecord objects
# Sorts by sales and calculates: rank, %, % cumulative
def cast_and_sort_rankedInvoices(records):
    # sort by sales
    sorted_records = sorted(records, key=lambda r: r.sales, reverse=True)
    total_sales = sum(r.sales for r in sorted_records)

    # add rank, percent and cumulative percent
    ranked_invoices = []
    cumulative = 0
    for i, record in enumerate(sorted_records):
        percent = (record.sales / total_sales) if total_sales else 0
        cumulative += percent
        ranked_invoices.append(
            transform_invoiceRecord_rankedInvoiceRecord(
                record,
                i + 1,
                round(percent, 4),
                round(cumulative, 4)
            )
        )
    return ranked_invoices

def autosize_columns(workbook, headers):
    sheet = workbook.active
    from openpyxl.utils import get_column_letter

    # autosize columns
    for col_index in range(1, len(headers) + 1):
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
    return workbook

# formats cells to have % or $ accordingly
def format_units(workbook, sales_col, percent_cols, start_row=3):
    sheet = workbook.active
    max_col = max(sales_col, *percent_cols)

    for row in sheet.iter_rows(min_row=start_row, max_row=sheet.max_row, min_col=1, max_col=max_col):
        sales_cell = row[sales_col - 1]
        if sales_cell.value is not None:
            sales_cell.number_format = '$#,##0.00'
        for col in percent_cols:
            percent_cell = row[col - 1]
            if percent_cell.value is not None:
                percent_cell.number_format = '0.00%'

    return workbook
