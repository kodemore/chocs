"""
Do not edit! 

This file was automatically generated from: 
/Users/krac/Projects/kodemore/chocs/tests/fixtures/openapi.yml

Generation time: 
2021-07-02 12:52:29.748524 
"""

import datetime
import typing
import decimal
import ipaddress
import dataclasses


@dataclasses.dataclass()
class NewPet:
    name: str
    base_tag: typing.Optional[str]


@dataclasses.dataclass()
class PetTag:
    name: typing.Optional[str]
    id: typing.Optional[int]


@dataclasses.dataclass()
class Error:
    code: int
    message: str


@dataclasses.dataclass()
class Pet(NewPet):
    id: int
    tags: typing.Optional[typing.List['PetTag']]
