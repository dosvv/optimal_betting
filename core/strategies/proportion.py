from core.models import StateSpace
from math import floor


class ProportionalStrategy:
    def __init__(self, target: int, percentage: int):
        self.target = target
        self.proportion = percentage / 100
    def get_bet(self, state: StateSpace) -> int:

        if state.capital < 1 or state.capital >= self.target or state.rounds_left == 0:
            return 0

        return max(0, floor(state.capital * self.proportion))