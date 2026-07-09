# file containing all func to cast from one Object type into another
from models.invoice_record import InvoiceRecord
from models.ranked_invoice_record import RankedInvoiceRecord


# input: an InvoiceRecord object
# output: a RankedInvoiceRecord
def transform_invoiceRecord_rankedInvoiceRecord(record, rank, percent, cum):
    return RankedInvoiceRecord(
        record = record,
        rank = rank,
        percent = percent,
        cumulative = cum
    )

# casts each record from the DB into a InvoiceRecord object
# input: list of [refid, desc, cat, custname, distributor field, qty, extprice]
# output: list of InvoiceRecord objs
def cast_to_invoice_records(rows):
    invoice_records = []
    for row in rows:
        ref_id, descr, cat, custname, distr, qty, extprice = row
        invoice_records.append(
            InvoiceRecord(
                customer_name=custname,
                cases=qty,
                sales=extprice,
                product_id=ref_id,
                description=descr,
                category=cat,
                is_distributor= distr == 'Distr'
            )
        )
    return invoice_records