"""
 CLAUDE AI HAS FULLY GENERATED THIS FILE:

Builds a categorized Sales-by-Category report from a nested data structure:
    { category: { size: { refid: [description, [qty2024, qty2025, qty2026],
                                                  [sales2024, sales2025, sales2026]] } } }

Layout mimics the target report:
  - one row per item
  - blank row, then a subtotal row per "size" group (with % increase vs prior year)
  - a "Total <Category>" row after all size groups in a category
  - 2 blank rows between categories
  - a Grand Total row at the very end
  - % of Total Sales computed on category-total / grand-total rows
  - % of Core Sales left BLANK for now (no definition provided yet)
"""

import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ---- Inputs you can change ----
REPORT_TITLE = "Sales By Category  01/01/26 to 07/21/26"
CUSTOMER_LINE = "For Customer(s) Dairyland to Dairyland"

arial = 'Arial'
bold = Font(name=arial, bold=True)
regular = Font(name=arial)
center = Alignment(horizontal='center')
top_border = Border(top=Side(style='thin'))

def generate_excel_report(data):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sales by Category"

    add_title_and_headers(ws)


    header_row = 3
    headers = {
        'C': 'Item No', 'D': 'Descript',
        'E': 'Qty2024', 'F': 'Qty2025', 'G': 'Qty2026',
        'I': 'Sales2024', 'J': 'Sales2025', 'K': 'Sales2026',
        'M': '2024', 'N': '2025', 'O': '2026',
        'Q': '2024', 'R': '2025', 'S': '2026',
        'V': '2025', 'W': '2026',
    }
    for col, label in headers.items():
        cell = ws[f'{col}{header_row}']
        cell.value = label
        cell.font = bold
        if col not in ('C', 'D'):
            cell.alignment = center

    # ---- Column widths ----
    widths = {'A': 2, 'B': 2, 'C': 12, 'D': 32, 'E': 9, 'F': 9, 'G': 9, 'H': 3,
              'I': 11, 'J': 11, 'K': 11, 'L': 3, 'M': 8, 'N': 8, 'O': 8, 'P': 3,
              'Q': 8, 'R': 8, 'S': 8, 'T': 3, 'U': 3, 'V': 9, 'W': 9}
    for col, width in widths.items():
        ws.column_dimensions[col].width = width

    return wb

def add_title_and_headers(sheet):
    # ---- Header rows ----
    sheet['C1'] = REPORT_TITLE
    sheet['C1'].font = bold

    sheet['C2'] = CUSTOMER_LINE
    sheet['C2'].font = regular
    sheet.merge_cells('M2:O2');
    sheet['M2'] = '% of Total Sales'
    sheet.merge_cells('Q2:S2');
    sheet['Q2'] = '% of Core Sales'
    sheet.merge_cells('V2:W2');
    sheet['V2'] = '% Increase Sales'
    for cell in ('M2', 'Q2', 'V2'):
        sheet[cell].font = bold
        sheet[cell].alignment = center

def fill_records(sheet):
    pass

# CATEGORY_NAMES = {
#     '1': 'Total Cheesecake',
#     '2': 'Total Cheesecake',  # placeholder label per source report
# }

# row = header_row + 1
# category_total_rows = []
#
# cat_items = list(data.items())
# for cat_idx, (category, sizes) in enumerate(cat_items):
#     size_items = list(sizes.items())
#     category_item_rows = []  # every item row in this category, for the category total
#
#     for size_idx, (size, items) in enumerate(size_items):
#         item_start = row
#         for refid, (descr, qty, sales) in items.items():
#             ws[f"{COL['item']}{row}"] = refid
#             ws[f"{COL['descr']}{row}"] = descr
#             ws[f"{COL['qty2024']}{row}"] = qty[0]
#             ws[f"{COL['qty2025']}{row}"] = qty[1]
#             ws[f"{COL['qty2026']}{row}"] = qty[2]
#             ws[f"{COL['sales2024']}{row}"] = sales[0]
#             ws[f"{COL['sales2025']}{row}"] = sales[1]
#             ws[f"{COL['sales2026']}{row}"] = sales[2]
#             for col in ('qty2024', 'qty2025', 'qty2026'):
#                 ws[f"{COL[col]}{row}"].number_format = QTY_FMT
#             for col in ('sales2024', 'sales2025', 'sales2026'):
#                 ws[f"{COL[col]}{row}"].number_format = SALES_FMT
#             for c in ws[row]:
#                 c.font = regular
#             category_item_rows.append(row)
#             row += 1
#         item_end = row - 1
#
#         row += 1  # blank separator row before subtotal
#
#         # ---- size subtotal row ----
#         subtotal_row = row
#         for key, col in (('qty2024', 'E'), ('qty2025', 'F'), ('qty2026', 'G'),
#                           ('sales2024', 'I'), ('sales2025', 'J'), ('sales2026', 'K')):
#             letter = COL[key]
#             ws[f"{letter}{subtotal_row}"] = f"=SUM({letter}{item_start}:{letter}{item_end})"
#             fmt = QTY_FMT if key.startswith('qty') else SALES_FMT
#             ws[f"{letter}{subtotal_row}"].number_format = fmt
#
#         s24, s25, s26 = COL['sales2024'], COL['sales2025'], COL['sales2026']
#         ws[f"{COL['pctInc2025']}{subtotal_row}"] = (
#             f'=IF({s24}{subtotal_row}=0,"",({s25}{subtotal_row}-{s24}{subtotal_row})/{s24}{subtotal_row})'
#         )
#         ws[f"{COL['pctInc2026']}{subtotal_row}"] = (
#             f'=IF({s25}{subtotal_row}=0,"",({s26}{subtotal_row}-{s25}{subtotal_row})/{s25}{subtotal_row})'
#         )
#         ws[f"{COL['pctInc2025']}{subtotal_row}"].number_format = PCT_FMT
#         ws[f"{COL['pctInc2026']}{subtotal_row}"].number_format = PCT_FMT
#
#         for c in ws[subtotal_row]:
#             c.font = bold
#             c.border = top_border
#
#         row += 1
#         if size_idx < len(size_items) - 1:
#             row += 1  # blank row before next size group's items
#
#     # ---- category total row ----
#     cat_total_row = row
#     category_total_rows.append(cat_total_row)
#     ws[f"{COL['descr']}{cat_total_row}"] = CATEGORY_NAMES.get(category, f'Total Category {category}')
#
#     for key, letter in COL.items():
#         if key.startswith('qty') or key.startswith('sales'):
#             item_refs = "+".join(f"{letter}{r}" for r in category_item_rows) if False else None
#     # Sum straight from the item rows collected for this category (robust even with multiple size groups)
#     for key in ('qty2024', 'qty2025', 'qty2026', 'sales2024', 'sales2025', 'sales2026'):
#         letter = COL[key]
#         refs = ",".join(f"{letter}{r}" for r in category_item_rows)
#         ws[f"{letter}{cat_total_row}"] = f"=SUM({refs})"
#         ws[f"{letter}{cat_total_row}"].number_format = QTY_FMT if key.startswith('qty') else SALES_FMT
#
#     ws[f"{COL['pctInc2025']}{cat_total_row}"] = (
#         f"=IF({s24}{cat_total_row}=0,\"\",({s25}{cat_total_row}-{s24}{cat_total_row})/{s24}{cat_total_row})"
#     )
#     ws[f"{COL['pctInc2026']}{cat_total_row}"] = (
#         f"=IF({s25}{cat_total_row}=0,\"\",({s26}{cat_total_row}-{s25}{cat_total_row})/{s25}{cat_total_row})"
#     )
#     ws[f"{COL['pctInc2025']}{cat_total_row}"].number_format = PCT_FMT
#     ws[f"{COL['pctInc2026']}{cat_total_row}"].number_format = PCT_FMT
#
#     for c in ws[cat_total_row]:
#         c.font = bold
#         c.border = top_border
#
#     row += 1
#     if cat_idx < len(cat_items) - 1:
#         row += 2  # blank rows between categories
#
# # ---- Grand total row ----
# grand_row = row
# ws[f"{COL['descr']}{grand_row}"] = 'Grand Total All Categories'
# for key in ('qty2024', 'qty2025', 'qty2026', 'sales2024', 'sales2025', 'sales2026'):
#     letter = COL[key]
#     refs = ",".join(f"{letter}{r}" for r in category_total_rows)
#     ws[f"{letter}{grand_row}"] = f"=SUM({refs})"
#     ws[f"{letter}{grand_row}"].number_format = QTY_FMT if key.startswith('qty') else SALES_FMT
#
# ws[f"{COL['pctInc2025']}{grand_row}"] = (
#     f"=IF({s24}{grand_row}=0,\"\",({s25}{grand_row}-{s24}{grand_row})/{s24}{grand_row})"
# )
# ws[f"{COL['pctInc2026']}{grand_row}"] = (
#     f"=IF({s25}{grand_row}=0,\"\",({s26}{grand_row}-{s25}{grand_row})/{s25}{grand_row})"
# )
# ws[f"{COL['pctInc2025']}{grand_row}"].number_format = PCT_FMT
# ws[f"{COL['pctInc2026']}{grand_row}"].number_format = PCT_FMT
#
# # ---- % of Total Sales, on category total rows + grand total ----
# for cat_total_row in category_total_rows:
#     for key, pct_col in (('sales2024', 'pctT2024'), ('sales2025', 'pctT2025'), ('sales2026', 'pctT2026')):
#         letter = COL[key]
#         pct_letter = COL[pct_col]
#         ws[f"{pct_letter}{cat_total_row}"] = f"={letter}{cat_total_row}/{letter}${grand_row}"
#         ws[f"{pct_letter}{cat_total_row}"].number_format = PCT_FMT
#
# for key, pct_col in (('sales2024', 'pctT2024'), ('sales2025', 'pctT2025'), ('sales2026', 'pctT2026')):
#     letter = COL[key]
#     pct_letter = COL[pct_col]
#     ws[f"{pct_letter}{grand_row}"] = f"={letter}{grand_row}/{letter}{grand_row}"
#     ws[f"{pct_letter}{grand_row}"].number_format = PCT_FMT
#
# # NOTE: % of Core Sales (Q:S) intentionally left blank — no core/non-core
# # definition provided yet. Let me know the rule and I'll wire it in.
#
# for c in ws[grand_row]:
#     c.font = bold
#     c.border = top_border

