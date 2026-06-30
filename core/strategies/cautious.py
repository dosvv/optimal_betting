from core.models import StateSpace


class CautiousStrategy:
    def __init__(self, target):
        self.target = target

    def get_bet(self, state: StateSpace) -> int:

        if state.capital < 1 or state.capital >= self.target or state.rounds_left == 0:
            return 0

        return 1
