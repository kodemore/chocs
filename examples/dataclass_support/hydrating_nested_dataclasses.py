import datetime
import decimal
import enum
from dataclasses import dataclass
from typing import List

from chocs.dataclasses import asdict, init_dataclass


class Currency(enum.Enum):
    GBP = "GBP"


@dataclass
class Money:
    currency: Currency
    amount: decimal.Decimal


@dataclass
class Transaction:
    started: datetime.datetime
    status: str
    value: Money


@dataclass
class Transactions:
    last_transaction: datetime.datetime
    transactions: List[Transaction]


transactions = init_dataclass(
    {
        "last_transaction": "2020-10-01T15:21:31",
        "transactions": [
            {
                "started": "2020-10-01T15:21:31",
                "status": "approved",
                "value": {
                    "currency": "GBP",
                    "amount": "10.21",
                }
            },
            {
                "started": "2020-09-01T12:21:31",
                "status": "declined",
                "value": {
                    "currency": "GBP",
                    "amount": "100.00",
                }
            },
            {
                "started": "2020-09-01T19:12:00",
                "status": "pending",
                "value": {
                    "currency": "GBP",
                    "amount": "50.21",
                }
            },
        ]
    },
    Transactions
)

assert isinstance(transactions, Transactions)

for transaction in transactions.transactions:
    assert isinstance(transaction, Transaction)
    assert isinstance(transaction.value, Money)
    assert isinstance(transaction.value.currency, Currency)


print(transactions)
print(asdict(transactions))
