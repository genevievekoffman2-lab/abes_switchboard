from dataclasses import dataclass
from typing import Optional

# data type representing a record from INVOICE/INVDET tables
@dataclass
class InvoiceRecord:
    customer_name: str
    cases: float
    sales: float
    product_id: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_distributor: Optional[bool] = None

