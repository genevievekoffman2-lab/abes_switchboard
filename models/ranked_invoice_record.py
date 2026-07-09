from dataclasses import dataclass
from models.invoice_record import InvoiceRecord

# represents an invoice records ranking among other data points
@dataclass
class RankedInvoiceRecord:
    record: InvoiceRecord
    rank: int
    percent: float
    cumulative: float

    def get_attribute(self, attribute_name):
        if hasattr(self, attribute_name):
            return getattr(self, attribute_name)
        return getattr(self.record, attribute_name)