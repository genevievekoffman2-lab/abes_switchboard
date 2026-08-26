# file contains all SQL queries to the Firebird database

from datetime import date, timedelta


# gets a list of all the customers
def get_all_cust(con):
    cursor = con.cursor()
    cursor.execute("SELECT * FROM cust")
    rows = cursor.fetchall()
    cursor.close()
    return rows

# basic operation to grab all open orders uses state
# only works when the time period is current bc it depends on 'state=ordered'
#
def get_open_orders_(con, from_date: date, to_date: date):
    date_filter = "AND CAST(j.NEEDDATE AS DATE) BETWEEN ? AND ?"
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
    cursor.execute(query, [from_date, to_date])
    rows = cursor.fetchall()
    cursor.close()
    return rows

# gets the open orders placed between from-to dates
# that have a NEEDATE coming up
def get_open_orders_after_date(con, from_date: date, to_date: date):
    ninety_days_before_from_date = from_date - timedelta(days=90)
    query = """
            SELECT 
                item.ADFIELD2, 
                SUM(det.EXTPRICE)
            FROM JOBS j
            LEFT JOIN INVOICE inv ON j.JOBNO = inv.JOBNO 
            JOIN JOBDETL det ON j.JOBNO = det.JOBNO 
            JOIN ITEM item ON det.REFID = item.ITEMCODE 
            WHERE j.JOBNO LIKE 'SO%'
            AND CAST(j.CRETDATE AS DATE) BETWEEN ? AND ? 
            AND CAST(j.NEEDDATE AS DATE) > ?
            AND inv.JOBNO IS NULL
            AND item.ADFIELD2 IN ('1', '2', '3', '7')
            GROUP BY item.ADFIELD2 
            ORDER BY item.ADFIELD2
        """
    cursor = con.cursor()
    cursor.execute(query, [ninety_days_before_from_date, to_date, to_date])
    rows = cursor.fetchall()
    cursor.close()
    return rows


# used for MFG Open Orders Module
# gets a list such that
#       INVDATE is between from and to dates
# list returned is the total sales per ADFIELD2 (category)
def get_total_sales(con, from_date: date, to_date: date):
    query = """
        SELECT
            item.ADFIELD2,
            SUM(det.EXTPRICE) AS SUMOFEXTPRICE
        FROM INVOICE inv
        INNER JOIN INVDETL det
            ON det.SUBNO = inv.SUBNO
            AND det.JOBNO = inv.JOBNO
        INNER JOIN ITEM item
            ON det.REFID = item.ITEMCODE
        WHERE CAST(inv.INVDATE AS DATE) BETWEEN ? AND ?
            AND item.CATEGORY <> 'Z-CUSTOM'
        GROUP BY item.ADFIELD2
        ORDER BY item.ADFIELD2;
         
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

# grabs all open orders from a year ago using the invoice creation date and
# the job creation date as params; also includes jobs within 90 days; see docs
# for more details
def get_open_orders_last_year(con, from_date: date, to_date: date):
    from_date_90 = from_date - timedelta(days=90)
    query = f"""
        SELECT 
            item.ADFIELD2, 
            SUM(det.EXTPRICE)
        FROM JOBS j
        LEFT JOIN INVOICE inv ON j.JOBNO = inv.JOBNO 
        JOIN JOBDETL det ON j.JOBNO = det.JOBNO 
        JOIN ITEM item ON det.REFID = item.ITEMCODE 
        WHERE j.JOBNO LIKE 'SO%'
        AND CAST(j.CRETDATE AS DATE) BETWEEN '{from_date_90}' AND '{to_date}'
        AND ( CAST(inv.INVDATE AS DATE) > '{to_date}' OR inv.JOBNO IS NULL )
        AND item.ADFIELD2 IN ('1', '2', '3', '7')
        GROUP BY item.ADFIELD2 
        ORDER BY item.ADFIELD2
    """
    cursor = con.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    return rows

# gives us sales in the time range from the customers by item
def get_sales_by_item_cr(con, customer_names: list, from_date: date, to_date: date):
    placeholders = ",".join(["?" for _ in customer_names])  # creates a list filled with ? same len as customer names
    query = f"""
        SELECT 
            det.REFID,
            det.DESCRIPT,
            i.ADFIELD2, 
            i.ADFIELD3,
            SUM(det.QTY),
            SUM(det.EXTPRICE)
        FROM INVOICE inv
        JOIN INVDETL det ON inv.JOBNO = det.JOBNO 
        JOIN ITEM i ON det.REFID = i.ITEMCODE
        WHERE inv.CUSTNAME IN ({placeholders})
        AND CAST(inv.INVDATE AS DATE) BETWEEN ? AND ?
        GROUP BY det.REFID, det.DESCRIPT, i.ADFIELD2, i.ADFIELD3 
        ORDER BY det.REFID 
        """
    params = customer_names + [from_date, to_date]
    cursor = con.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    return rows

# gets sales (with cost attribute) for PM module
# category filter (none- all; Mfg - manufacturing; Dist - distributors)
def get_sales_and_cost(con, from_date: date, to_date: date, category_filter=None):
    where_clause = ""
    if category_filter == 'Distributed':
        where_clause = "AND item.CATEGORY = 'PURCHASED FOR DIST.'"
    elif category_filter == 'Mfg':
        where_clause = "AND item.CATEGORY IN ('BAKEV', 'BAKEC')"
    query = f"""
            SELECT 
               item.ADFIELD2,
				item.ADFIELD3,
                det.REFID,
                det.DESCRIPT,
                SUM(det.EXTPRICE ) AS total_sales,
                SUM(det.EXTCOST) AS total_cost
            FROM INVOICE inv
            JOIN INVDETL det ON inv.JOBNO = det.JOBNO 
            AND inv.SUBNO = det.SUBNO
            JOIN ITEM item ON det.REFID = item.ITEMCODE 
            WHERE inv.JOBNO LIKE 'SO%'
            {where_clause}
            AND CAST(inv.INVDATE AS DATE) BETWEEN ? AND ?
            GROUP BY item.ADFIELD2, item.ADFIELD3, det.REFID, det.DESCRIPT
			ORDER BY item.ADFIELD2, item.ADFIELD3, det.REFID
    """
    cursor = con.cursor()
    cursor.execute(query, [from_date, to_date])
    rows = cursor.fetchall()
    cursor.close()
    return rows