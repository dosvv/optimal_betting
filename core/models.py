from dataclasses import dataclass

@dataclass(frozen=True)
class StateSpace:
    capital: int
    rounds_left: int