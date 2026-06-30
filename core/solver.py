from fractions import Fraction
from math import ceil, floor

from core.models import StateSpace


class BettingSolver:
    def __init__(self, target: int, total_rounds: int, prob_win: Fraction,
                 payout_ratio: Fraction, prefer_larger_bets: bool = True):
        self.target = target
        self.total_rounds = total_rounds
        self.prob_win = prob_win
        self.payout_ratio = payout_ratio
        self.prefer_larger_bets = prefer_larger_bets

        self.cache: dict[StateSpace, tuple[Fraction, int]] = {}

    def solve_state(self, state_space: StateSpace) -> tuple[Fraction, int]:

        if state_space in self.cache:
            return self.cache[state_space]

        # base cases
        if state_space.capital >= self.target:
            self.cache[state_space] = (Fraction(1, 1), 0)
            return self.cache[state_space]

        if state_space.capital <= 0 or state_space.rounds_left == 0:
            self.cache[state_space] = (Fraction(0, 1), 0)
            return self.cache[state_space]

        if self.payout_ratio <= 1:
            max_optimal_bet = 0
        else:
            max_optimal_bet_help = Fraction(self.target - state_space.capital, self.payout_ratio - 1)
            max_optimal_bet = ceil(max_optimal_bet_help)

        max_bet = int(min(floor(state_space.capital), max_optimal_bet))

        all_bets = list(range(1, max_bet + 1))
        if not all_bets:
            self.cache[state_space] = (Fraction(0, 1), 0)
            return self.cache[state_space]

        prefer_larger_bets_toggle = 1 if self.prefer_larger_bets else -1

        best_prob, best_bet = max(
            (
                (
                    self.prob_win * self.solve_state(
                        StateSpace(
                            capital=state_space.capital - bet + bet * self.payout_ratio,
                            rounds_left=state_space.rounds_left - 1,
                        )
                    )[0]
                    + (1 - self.prob_win) * self.solve_state(
                        StateSpace(
                            capital=state_space.capital - bet,
                            rounds_left=state_space.rounds_left - 1,
                        )
                    )[0],
                    bet,
                )
                for bet in all_bets
            ),
            key=lambda x: (x[0], prefer_larger_bets_toggle * x[1]),
        )

        self.cache[state_space] = (best_prob, best_bet)
        return best_prob, best_bet