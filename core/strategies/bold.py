from math import ceil, floor
from fractions import Fraction
from core.models import StateSpace


class BoldStrategy:
    def __init__(self, target: int, payout_ratio: Fraction):
        self.target = target
        self.payout_ratio = payout_ratio

    def get_bet(self, state: StateSpace) -> int:

        if state.capital < 1 or state.capital >= self.target or state.rounds_left == 0:
            return 0

        max_available = floor(state.capital)
        if max_available < 1:
            return 0

        required_max_bet = Fraction(self.target - state.capital, self.payout_ratio - 1)
        optimal_max_bet = ceil(required_max_bet)

        return min(max_available, optimal_max_bet)