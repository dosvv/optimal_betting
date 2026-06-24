from fractions import Fraction
from core.models import StateSpace

class BettingMapGenerator:
    def __init__(self, solver):
        self.solver = solver

    def generate(self) -> dict[StateSpace, tuple[Fraction, int]]:
        """
        :return:
        :key: StateSpace(capital, rounds_left)
        :value: (probability, optimal bet)
        """
        betting_map = {}
        capital = self.solver.original_target
        rounds = self.solver.total_rounds

        for c in range(capital + 1):
            for r in range(rounds + 1):
                state = StateSpace(capital=c, rounds_left= r)

                betting_map[state] = self.solver.solve_state(state)

        return betting_map