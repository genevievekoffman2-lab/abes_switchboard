# file contains all SQL queries to the Firebird database

from datetime import date

# gets a list of all the customers
def get_all_cust(con):
    cursor = con.cursor()
    cursor.execute("SELECT * FROM cust")
    rows = cursor.fetchall()
    cursor.close()
    return rows

# grabs all open orders in the time range
# if after_ship_date is true; its the future open orders
def get_open_orders_mfg(con, from_date: date, to_date: date, after_ship_date: bool):
    if after_ship_date:
        date_filter = "AND CAST(j.NEEDDATE AS DATE) > ?"
        params = [to_date]
    else:
        date_filter = "AND CAST(j.NEEDDATE AS DATE) BETWEEN ? AND ?"
        params = [from_date, to_date]

    query = f"""
        SELECT 
            item.ADFIELD2, 
            SUM(det.EXTPRICE)
        FROM JOBS j 
        JOIN JOBDETL det ON j.JOBNO = det.JOBNO 
        JOIN ITEM item ON det.REFID = item.ITEMCODE 
        WHERE j.JOBSTATS = 'ORDERED'
            {date_filter}
        GROUP BY item.ADFIELD2 
        ORDER BY item.ADFIELD2
    """
    cursor = con.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    return rows


# used for MFG Open Orders Module
# gets a list such that
#       INVDATE is between from and to dates
# list returned is the total sales per ADFIELD2 (category)
def get_total_sales_mfg(con, from_date: date, to_date: date):
    query = """
        SELECT 
            item.ADFIELD2,
            SUM(det.EXTPRICE)
        FROM INVOICE inv
        JOIN INVDETL det ON inv.JOBNO = det.JOBNO 
        JOIN ITEM item ON det.REFID = item.ITEMCODE 
        WHERE CAST(inv.INVDATE AS DATE) BETWEEN ? AND ?
        AND item.CATEGORY != 'Z-CUSTOM'
        GROUP BY item.ADFIELD2
        ORDER BY item.ADFIELD2 
    """
    cursor = con.cursor()
    cursor.execute(query, [from_date, to_date])
    rows = cursor.fetchall()
    cursor.close()
    return rows

# gets accounting adjustments (credit/debit)
def get_sales_adjustments(con, from_date: date, to_date: date):
    query = """
        SELECT 
            DEBIT,
            CREDIT
        FROM GLFILE
        WHERE ACCOTNO = '40200-00'
        AND CAST(DATECREATE AS DATE) BETWEEN ? AND ? 
    """
    cursor = con.cursor()
    cursor.execute(query, [from_date, to_date])
    rows = cursor.fetchall()
    cursor.close()
    return rows

# gets a list of invoices such that:
#       CUSTNAME is in our list
#       INVDATE is between from and to dates
#   list returned of form (product id, description, category, customer name, distributor field, cases, sales)
def get_invoices(con, customer_names: list, from_date: date, to_date: date):
    placeholders = ",".join(["?" for _ in customer_names]) #creates a list filled with ? same len as customer names
    query = f"""
        SELECT 
            invdtl_table.REFID,
            invdtl_table.DESCRIPT, 
            item_table.ADFIELD2,
            invoice_table.CUSTNAME,
            item_table.ADFIELD5,
            SUM(invdtl_table.QTY),
            SUM(invdtl_table.EXTPRICE)
        FROM INVOICE invoice_table 
        JOIN INVDETL invdtl_table ON invoice_table.JOBNO = invdtl_table.JOBNO         
        JOIN ITEM item_table ON invdtl_table.REFID = item_table.ITEMCODE
        WHERE invoice_table.CUSTNAME IN ({placeholders})
        AND INVDATE BETWEEN ? AND ?
        GROUP BY invdtl_table.REFID, invdtl_table.DESCRIPT, item_table.ADFIELD2, invoice_table.CUSTNAME, item_table.ADFIELD5 
    """

    params = customer_names + [from_date, to_date]

    cursor = con.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    return rows

