from core.models import StateSpace
from fractions import Fraction


class DPStrategy:
    def __init__(self, betting_map: dict[StateSpace, tuple[Fraction, int]]):
        self.betting_map = betting_map

    def get_bet(self, state: StateSpace) -> int:
        if state not in self.betting_map:
            return 0

        return self.betting_map[state][1]