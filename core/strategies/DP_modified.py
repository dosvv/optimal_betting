from fractions import Fraction
from math import floor
from core.models import StateSpace
from core.strategies.bold import BoldStrategy
from core.strategies.cautious import CautiousStrategy
from core.strategies.kelly import KellyStrategy


class DPModStrategy:
    def __init__(self, betting_map: dict[StateSpace, tuple[Fraction, int]],
                 target: int, prob_win: Fraction, payout_ratio: Fraction,
                 prefer_larger_bets: bool = True):

        self.betting_map = betting_map
        self.target = target
        self.prob_win = prob_win
        self.payout_ratio = payout_ratio
        self.prefer_larget_bets = prefer_larger_bets

        self.cautious = CautiousStrategy(target= target)
        self.bold = BoldStrategy(target= target, payout_ratio= payout_ratio)
        self.kelly = KellyStrategy(target= target, payout_ratio= payout_ratio, prob_win= prob_win)

    def get_bet(self, state: StateSpace) -> int:
        if state.capital < 1 or state.capital >= self.target or state.rounds_left == 0:
            return 0

        max_available = floor(state.capital)
        if max_available < 1:
            return 0

        bet_cautious = self.cautious.get_bet(state)
        bet_bold = self.bold.get_bet(state)
        bet_kelly = self.kelly.get_bet(state)

        if bet_kelly > bet_bold:
            bet_kelly = bet_bold

        all_bets = {bet for bet in (bet_cautious, bet_bold, bet_kelly) if 0 < bet <= max_available}
        if not all_bets:
            return 0

        prefer_larger_bets_toggle = 1 if self.prefer_larget_bets else -1

        def next_step(bet: int) -> tuple[Fraction, int]:
            state_win = StateSpace(
                capital= state.capital - bet + (bet * self.payout_ratio),
                rounds_left= state.rounds_left - 1
            )

            state_loss = StateSpace(
                capital= state.capital - bet,
                rounds_left= state.rounds_left - 1
            )

            p_win_next = self.betting_map.get(
                state_win, (Fraction(1 if state_win.capital >= self.target else 0, 1),0)
            )[0]

            p_loss_next = self.betting_map.get(
                state_loss, (Fraction(0, 1),0)
            )[0]

            exp_prob = (self.prob_win * p_win_next) + ((1- self.prob_win) * p_loss_next)

            return exp_prob, bet

        best_prob, best_bet = max(
            (next_step(bet) for bet in all_bets),
            key= lambda x: (x[0], prefer_larger_bets_toggle* x[1])
        )

        return best_bet