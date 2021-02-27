from dataclasses import dataclass, field
from typing import List

from chocs.dataclasses import asdict


@dataclass
class Pet:
    name: str
    tags: List[str] = field(repr=False)


boo = Pet(name="Boo", tags=["pet", "hamster", "powerful!"])

boo_dict = asdict(boo)

assert "tags" not in boo_dict
