import os
import tempfile

import openpyxl
from openpyxl.utils import get_column_letter

from models.invoice_record import InvoiceRecord
from models.ranked_invoice_record import RankedInvoiceRecord
from services.aggregators import group_by_category
from services.excel_utils import add_titles_and_headers, format_sheet
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


    currency_cols = ["E"]  # columns we want to formate as currency
    percent_cols = ["G", "H"]
    # add formatting
    format_sheet(sheet, len(headers), currency_cols, percent_cols)
    return workbook


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



def open_excel(workbook):
    # save to a temp file
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp:
        tmp_path = temp.name
    workbook.save(tmp_path)
    os.startfile(tmp_path)

