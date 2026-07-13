from enum import StrEnum, auto


class Environment(StrEnum):
    dev = auto()
    prod = auto()
    test = auto()
