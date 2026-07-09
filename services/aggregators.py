# file containing any func performing summing or grouping logic
from models.invoice_record import InvoiceRecord


# given a list of InvoiceRecord objects
# calculates total sales and cases bought by customer (ignoring items)
def aggregate_by_customer(records):
    customers = {}

    for record in records:
        if record.customer_name not in customers:
            customers[record.customer_name] = InvoiceRecord(
                customer_name=record.customer_name,
                cases=0,
                sales=0
            )

        customers[record.customer_name].cases += record.cases
        customers[record.customer_name].sales += record.sales

    return list(customers.values())


# given a list of InvoiceRecord objects
# calculates total cases and total sales sold per item (ignoring customer)
# returns a list of InvoiceRecord objects
def aggregate_by_item(records):
    products = {}

    for record in records:
        if record.product_id not in products:
            products[record.product_id] = InvoiceRecord(
                customer_name="All customers",
                cases=0,
                sales=0,
                product_id=record.product_id,
                description=record.description,
                category=record.category
            )

        products[record.product_id].cases += record.cases  # add cases to total cases
        products[record.product_id].sales += record.sales  # add sales to total sales

    return list(products.values())

# iterates through records and groups them by their category
# records: list of InvoiceRecord objects
def group_by_category(records):
    categories = {}  # dictionary with key=cat & values = a list of RankedRecord objects
    for record in records:
        category = record.category
        if category not in categories:
            categories[category] = []
        categories[category].append(record)
    return categories