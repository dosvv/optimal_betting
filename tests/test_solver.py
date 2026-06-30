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
    # --------------- trivial base cases --------------------
    state_on_target = StateSpace(capital= 5, rounds_left= 1)
    assert bet_map[state_on_target][0] == Fraction(1,1)
    assert bet_map[state_on_target][1] == 0

    state_no_cap = StateSpace(capital= 0, rounds_left= 1)
    assert bet_map[state_no_cap][0] == Fraction(0,1)
    assert bet_map[state_no_cap][1] == 0

    state_no_rounds = StateSpace(capital= 3, rounds_left= 0)
    assert bet_map[state_no_rounds][0] == Fraction(0,1)
    assert bet_map[state_no_rounds][1] == 0
    # -------------------------------------------------------
    # --------------- non-trivial cases ---------------------
    # 1 left to target, 1 round left
    # need to bet 1, p = 1/2
    state_4_1 = StateSpace(capital=4, rounds_left=1)
    assert bet_map[state_4_1][0] == Fraction(1, 2)
    assert bet_map[state_4_1][1] == 1

    # 2 left to target, 1 round left
    # need to bet 2, p = 1/2
    state_3_1 = StateSpace(capital=3, rounds_left=1)
    assert bet_map[state_3_1][0] == Fraction(1, 2)
    assert bet_map[state_3_1][1] == 2

    # 1 left to target, 2 rounds left
    # bet 1:
    # - win (p = 1/2): target -> p_win = 1
    # - loss (p = 1/2): c=3, r=1 -> bet 2, p_win = 1/2
    # comes to: P = (1/2 * 1) + (1/2 * 1/2) = 3/4
    state_4_2 = StateSpace(capital=4, rounds_left=2)
    assert bet_map[state_4_2][0] == Fraction(3, 4)
    assert bet_map[state_4_2][1] == 1

    # 3 left to target, 2 rounds left
    # from c=2, r=2, only option is to bet 2, then
    # available two bets: 1 and 2
    # - bet 1:
    #   win -> c=3, r=1 (p_win = 1/2). loss -> c=1, r=1 (p_win = 0).
    #   P(bet 1) = 1/2 * 1/2 = 1/4.
    # - bet 2:
    #   win -> c=4, r=1 (p_win = 1/2). loss -> c=0, r=1 (p_win = 0).
    #   P(bet 2) = 1/2 * 1/2 = 1/4.
    # both bets 1,2 have probability of winning (1/4), parameter prefer_larger_bets decides
    # by default prefer_larger_bets=True, therefore the bet must be 2.
    state_2_2 = StateSpace(capital=2, rounds_left=2)
    assert bet_map[state_2_2][0] == Fraction(1, 4)
    assert bet_map[state_2_2][1] == 2
    # -------------------------------------------------------