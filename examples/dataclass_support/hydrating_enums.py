import decimal
import enum
from dataclasses import dataclass

from chocs.dataclasses import asdict, init_dataclass


class Currency(enum.Enum):
    GBP = "GBP"


@dataclass
class Money:
    currency: Currency
    amount: decimal.Decimal


lot_of_pounds = init_dataclass({"currency": "GBP", "amount": "10000000.00"}, Money)

assert isinstance(lot_of_pounds, Money)
assert isinstance(lot_of_pounds.currency, Currency)

print(lot_of_pounds)
print(asdict(lot_of_pounds))
