from tests.mocks import mock_tuples, mock_invoice_records
from services.aggregators import aggregate_by_customer, aggregate_by_item

def test_aggregate_by_customer_a():
    res = aggregate_by_customer(mock_invoice_records)
    assert len(res) == 5

def test_aggregate_by_item_a():
    res = aggregate_by_item(mock_invoice_records)
    print(res)
    assert len(res) == 2 