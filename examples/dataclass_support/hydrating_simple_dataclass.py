from dataclasses import dataclass

from chocs.dataclasses import asdict, init_dataclass


@dataclass
class Money:
    currency: str
    amount: float


lot_of_pounds = init_dataclass({"currency": "GBP", "amount": "10000000.00"}, Money)

assert isinstance(lot_of_pounds, Money)
assert lot_of_pounds.currency == "GBP"
assert lot_of_pounds.amount == 10000000.00

print(lot_of_pounds)
print(asdict(lot_of_pounds))
