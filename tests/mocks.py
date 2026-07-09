# mocked data
from models.invoice_record import InvoiceRecord
from services.mappers import cast_to_invoice_records

mock_tuples = [
    ('ABE908', "Muffin - Abe's 12 - Carrot BOX", '2', 'WF NE Rochester', 'Retail', 9.0, 318.51),
    ('ABE908', "Muffin - Abe's 12 - Carrot BOX", '2', 'WF NE Spring Lake Wall', 'Retail', 25.0, 884.78),
    ('ABE908', "Muffin - Abe's 12 - Carrot BOX", '2', 'WF NE Stamford', 'Retail', 23.0, 813.968),
    ('BW305', 'BTW Bakery - GF Choc Layer Cake', '7', 'WF NE Port Chester', 'Distr', 12.0, 631.68),
    ('BW305', 'BTW Bakery - GF Choc Layer Cake', '7', 'WF NE Ridgewood', 'Distr', 13.0, 684.3199),
    ('BW305', 'BTW Bakery - GF Choc Layer Cake', '7', 'WF NE Rochester', 'Distr', 13.0, 684.31999),
    ('BW305', 'BTW Bakery - GF Choc Layer Cake', '7', 'WF NE Spring Lake Wall', 'Distr', 14.0, 736.99)
]

mock_invoice_records = cast_to_invoice_records(mock_tuples)