from fractions import Fraction
from dataclasses import dataclass


@dataclass(frozen=True)
class StateSpace:
    capital: Fraction
    rounds_left: int