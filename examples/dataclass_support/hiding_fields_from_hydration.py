from chocs.dataclasses import init_dataclass
from dataclasses import dataclass, field
from typing import List


@dataclass
class Pet:
    name: str
    tags: List[str]
    tags_length: int = field(init=False, default=0)

    def __post_init__(self):
        self.tags_length = len(self.tags)


boo = init_dataclass({"name": "Boo", "tags": ["hamster", "boo"], "tags_length": 0}, Pet)

assert isinstance(boo, Pet)
assert boo.tags_length == 2
