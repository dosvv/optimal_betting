from fractions import Fraction
from core.models import StateSpace
from functools import lru_cache


@lru_cache(maxsize=None)
def _solve_state(state_space: StateSpace, target: int, prob_win: Fraction, payout_ratio: Fraction) -> tuple[Fraction, int]:
    # base cases
    if state_space.capital >= target:
        return Fraction(1,1), 0
    elif state_space.capital <= 0 or state_space.rounds_left == 0:
        return Fraction(0,1), 0

    # recursive case
    if payout_ratio <= 1:
        max_optimal_bet = 0
    else:
        max_optimal_bet = int((target - state_space.capital) // (payout_ratio - 1))

    max_bet = min(state_space.capital, max_optimal_bet)

    if max_bet < 1:
        return Fraction(0,1), 0

    all_bets = range(1, max_bet + 1)

    best_prob, best_bet = max(
        (
            (
                 prob_win * _solve_state(
                    StateSpace(
                        capital= (state_space.capital - bet) + int(bet * payout_ratio),
                        rounds_left= state_space.rounds_left - 1
                    ),
                    target, prob_win, payout_ratio
                 )[0]
                 + (1 - prob_win) * _solve_state(
                    StateSpace(
                        capital= state_space.capital - bet,
                        rounds_left= state_space.rounds_left - 1
                    ),
                    target, prob_win, payout_ratio
                )[0]
            ),
            bet
        )
        for bet in all_bets
    )

    return best_prob, best_bet

class BettingSolver:
    def __init__(self, target: int, total_rounds: int, prob_win: Fraction, payout_ratio: Fraction):
        self.total_rounds = total_rounds
        self.prob_win = prob_win
        self.scale_factor = payout_ratio.denominator
        self.payout_ratio = payout_ratio * self.scale_factor
        self.target = target * self.scale_factor

    def solve_state(self, state_space: StateSpace) -> tuple[Fraction, int]:

        scaled_state = StateSpace(
            capital= state_space.capital * self.scale_factor,
            rounds_left= state_space.rounds_left
        )

        prob, scaled_bet = _solve_state(
            scaled_state, self.target, self.prob_win, self.payout_ratio
        )

        return prob, scaled_bet // self.scale_factor