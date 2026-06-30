from math import ceil, floor
from fractions import Fraction
from core.models import StateSpace


class KellyStrategy:
    def __init__(self, target, payout_ratio, prob_win):
        self.target = target
        self.payout_ratio = payout_ratio
        self.prob_win = prob_win

    def get_bet(self, state: StateSpace):

        if state.capital < 1 or state.capital >= self.target or state.rounds_left == 0:
            return 0

        kelly_frac = self.prob_win - Fraction(1 - self.prob_win, self.payout_ratio - 1)

        if kelly_frac < 0:
            return 0

        kelly_bet = floor(state.capital * kelly_frac)

        if kelly_frac > 0 and kelly_bet == 0:
            return 1

        required_max_bet = Fraction(self.target - state.capital, self.payout_ratio - 1)
        optimal_max_bet = ceil(required_max_bet)

        return min(kelly_bet, optimal_max_bet)