import sys
from datetime import date
from db.queries import get_invoices, add_rank_and_percents
from db.connection import get_connection

def test_get_invoices_multiple_customers():
    con = get_connection()

    invoices = get_invoices(
        con,
        ["WF NE Columbus Circle", "WF NE Clark"],
        date(2026, 4, 1),
        date(2026, 6, 10)
    )

    con.close()
    assert len(invoices) > 0

def test_get_invoices_single_customer():
    con = get_connection()

    invoices = get_invoices(
        con,
        ["WF NE Clark"],
        date(2026, 4, 1),
        date(2026, 6, 10)
    )

    for invoice in invoices:
        print(invoice)

    con.close()
    assert len(invoices) > 0

def test_get_invoices_updated_invoice():
    con = get_connection()

    invoices = get_invoices(
        con,
        ["WF NE Columbus Circle", "WF NE Clark"],
        date(2026, 4, 1),
        date(2026, 6, 10)
    )

    update_invoices = add_rank_and_percents(invoices)
    for invoice in update_invoices:
        print(invoice)

    con.close()
    con.close()
    assert len(invoices) > 0

