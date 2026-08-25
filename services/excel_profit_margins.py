import bisect
from collections import defaultdict
from openpyxl.styles import Alignment, Font

from services.excel_utils import add_titles_and_headers, format_sheet
import pandas as pd

def load_excel(sheet, headers, title, subtitle, rows):
    add_titles_and_headers(sheet, title, subtitle, headers)

    # pandas approach:
    # records_df, loc_ttls, size_ttls = pandas_group_data(rows)
    # write_df_into_excel(sheet, loc_ttls, size_ttls, records_df)

    data = group_data(rows)
    totals_row_numbers = write_dict_into_sheet(sheet, data)
    compute_additional_values(sheet, totals_row_numbers)

    currency_cols = ["E", "F", "G"]  # columns we want to formate as currency
    percent_cols = ["H","J", "K", "M", "N"]

    format_sheet(sheet, len(headers), currency_cols, percent_cols)


# computes gross contribution and pm % columns
# also computes 4 additional columns according to Bobs formulas
# ttl_row_numbers is a list of row indices where the subtotal for each location is (ex: 51, 108, 189)
def compute_additional_values(sheet, total_row_numbers):
    # grand total is last row (grab this index)
    last_row = sheet.max_row

    for row in range(5, sheet.max_row + 1):
        e_val = sheet[f"E{row}"].value
        if e_val is not None:
            sheet[f"G{row}"] = f"=E{row}-F{row}"
            sheet[f"H{row}"] = f"=(E{row}-F{row})/E{row}"
        # compute % of C Sales, C Mar, T Sales and T Mar percentages

        a_val = sheet[f"A{row}"].value
        if a_val == "" or "total" in a_val: #subtotal (size) row or location subtotal row
            loc_ttl_row = bisect.bisect_left(total_row_numbers, row)
            sheet[f"J{row}"] = f"=E{row}/E{total_row_numbers[loc_ttl_row]}"
            sheet[f"K{row}"] = f"=G{row}/G{total_row_numbers[loc_ttl_row]}"
            sheet[f"M{row}"] = f"=E{row}/E{last_row}"
            sheet[f"N{row}"] = f"=G{row}/G{last_row}"



# breaks data into a nested dictionary with key = adfield2 (location) and then key = adfield3 (size)
def group_data(rows):
    grouped = defaultdict(lambda: defaultdict(list))

    for row in rows:
        adfield2, adfield3, *rest = row
        grouped[adfield2][adfield3].append(tuple(rest))

    group = {k: dict(v) for k, v in grouped.items()}
    return group


# dict: nested dict with key = type and 2nd key = cat
def write_dict_into_sheet(sheet, dict):
    loc_ttl_row_numbers = [] # used in computing additional columns/percents
    #as we iterate, we also track the subtotals
    sheet.append([])
    grand_ttl_sales, grand_ttl_cost = 0, 0
    for location in sorted(dict.keys(), key=int):
        inner = dict[location]
        type_ttl_sales, type_ttl_cost = 0, 0
        for size in sorted(inner.keys(), key=int):
            records_list = inner[size]
            subttl_sales, subttl_cost = 0, 0
            for data in records_list:
                row = (location, size, *data)
                # the * before data unpacks the nested tuple
                sheet.append(row)
                subttl_sales += data[2]
                subttl_cost += data[3]
            sheet.append(["",f"{size} total", "", "", subttl_sales, subttl_cost])
            row_num = sheet.max_row # the row that was just written^
            sheet.cell(row=row_num, column=2).font = Font(bold=True)
            type_ttl_sales += subttl_sales
            type_ttl_cost += subttl_cost

        sheet.append([f"{location} total", "", "", "", type_ttl_sales, type_ttl_cost])
        row_num = sheet.max_row  # the row that was just written^
        loc_ttl_row_numbers.append(row_num)
        sheet.cell(row=row_num, column=1).font = Font(bold=True)
        grand_ttl_sales += type_ttl_sales
        grand_ttl_cost += type_ttl_cost

    sheet.append(["Grand Total", "", "", "", grand_ttl_sales, grand_ttl_cost])
    row_num = sheet.max_row  # the row that was just written^
    sheet.cell(row=row_num, column=1).font = Font(bold=True)
    return loc_ttl_row_numbers


def pandas_group_data(rows):
    dataframe = pd.DataFrame(rows, columns=["location", "size", "refid", "description", "sales", "cost"])
    dataframe["location"] = dataframe["location"].astype(int) # converts all entries in column to integers
    dataframe["size"] = dataframe["size"].astype(int)

    # add the gross contribution and profit margin % columns
    dataframe["gross_contribution"] = dataframe["sales"] - dataframe["cost"]
    dataframe["profit_margin"] = dataframe["gross_contribution"] / dataframe["sales"]

    # subtotals (size and locations)
    location_totals = dataframe.groupby("location")[["sales", "cost"]].sum().reset_index()
    size_totals = dataframe.groupby(["location", "size"])[["sales", "cost"]].sum().reset_index()

    size_totals["gross_contribution"] = size_totals["sales"] - size_totals["cost"]
    size_totals["profit_margin"] = size_totals["gross_contribution"] / size_totals["sales"]

    location_totals["gross_contribution"] = location_totals["sales"] - location_totals["cost"]
    location_totals["profit_margin"] = location_totals["gross_contribution"] / location_totals["sales"]
    return dataframe, location_totals, size_totals

# writes pandas data frame into Excel sheet
# location_ttls and size_ttls should be panda dataframe containing the subtotals for each section
# records_df is the dataframe containing all records from database
def write_df_into_excel(sheet, location_ttls, size_ttls, records_df):
    grand_sales, grand_cost = records_df["sales"].sum(), records_df["cost"].sum()

    for location in sorted(location_ttls["location"].unique()): # for each location #
        location_ttl_row = location_ttls[location_ttls["location"] == location]
        # TODO go over the code below (claude helped to generate)
        # compares loc column to value of location & only keeps the matching records; then it grabs the size column
        # ie only looking at rows that = location, pull out its size, sort & remove duplicates
        size_vals = sorted(records_df[records_df["location"] == location]["size"].unique())
        for size in size_vals:
            record_rows = records_df[
                (records_df["location"] == location) &
                (records_df["size"] == size)]
            #write each row
            for _, r in record_rows.iterrows():
                sheet.append((r["location"], r["size"], r["refid"], r["description"], r["sales"], r["cost"],
                              r["gross_contribution"], r["profit_margin"]))
            #write the subtotal for the size group
            sub_row = size_ttls[
                (size_ttls["location"] == location) &
                (size_ttls["size"] == size)
                ]
            sheet.append(["", f"{size} total", "", "", sub_row["sales"].values[0], sub_row["cost"].values[0],
                          sub_row["gross_contribution"].values[0], sub_row["profit_margin"].values[0]])
            sheet.cell(row=sheet.max_row, column=2).font = Font(bold=True)

        #write the total row for the location grouping
        sheet.append([f"{location} total", "", "", "", location_ttl_row["sales"].values[0], location_ttl_row["cost"].values[0],
                      location_ttl_row["gross_contribution"].values[0], location_ttl_row["profit_margin"].values[0]])
        row_num = sheet.max_row
        for col in range(1, 9):  # bold every column in this row
            sheet.cell(row=row_num, column=col).font = Font(bold=True)

    # grand total
    sheet.append(["Grand Total", "", "", "", grand_sales, grand_cost])
    sheet.cell(row=sheet.max_row, column=1).font = Font(bold=True)

