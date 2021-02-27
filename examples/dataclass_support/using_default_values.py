from dataclasses import dataclass, field
from typing import List

from chocs.dataclasses import init_dataclass


@dataclass
class Pet:
    name: str
    tags: List[str] = field(default_factory=lambda: ["pet"])


boo = init_dataclass({"name": "Boo"}, Pet)

assert isinstance(boo, Pet)
assert boo.tags == ['pet']
