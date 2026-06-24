from fractions import Fraction
from core.models import StateSpace
from core.solver import BettingSolver
from core.betting_map import BettingMapGenerator

def test_solver_generator():
    target = 5
    total_rounds = 3
    prob_win = Fraction(1, 2)
    payout_ratio = Fraction(2, 1)

    solver = BettingSolver(target, total_rounds, prob_win, payout_ratio)
    generator = BettingMapGenerator(solver)

    bet_map = generator.generate()

    state_on_target = StateSpace(capital= 5, rounds_left= 1)
    assert bet_map[state_on_target][0] == Fraction(1,1)
    assert bet_map[state_on_target][1] == 0

    state_no_cap = StateSpace(capital= 0, rounds_left= 1)
    assert bet_map[state_no_cap][0] == Fraction(0,1)
    assert bet_map[state_no_cap][1] == 0

    state_no_rounds = StateSpace(capital= 3, rounds_left= 0)
    assert bet_map[state_no_rounds][0] == Fraction(0,1)
    assert bet_map[state_no_rounds][1] == 0