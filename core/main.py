import math
import random
from fractions import Fraction

from core.models import StateSpace

def get_capital_history(
        strategy, init_capital: Fraction, target: int, total_rounds: int, prob_win: Fraction,
        payout_ratio: Fraction
        ) -> list[float]:

    """
    :return: Plays one game and returns development of capital
    """

    current_state = StateSpace(capital= init_capital, rounds_left= total_rounds)
    history = [float(current_state.capital)]

    while 0 < current_state.capital < target and current_state.rounds_left > 0:
        bet = strategy.get_bet(current_state)
        if bet < 0:
            break

        bet = min(bet, math.floor(current_state.capital))
        is_win = random.random() < float(prob_win)

        if is_win:
            new_capital = current_state.capital - bet + (bet * payout_ratio)
        else:
            new_capital = current_state.capital - bet

        current_state = StateSpace(capital= new_capital, rounds_left= current_state.rounds_left - 1)

        history.append(float(current_state.capital))

    while len(history) < total_rounds + 1:
        history.append(float(current_state.capital))

    return history

def get_monte_carlo_stats(
        strategies: list, num_sim: int, init_capital: Fraction, target: int,
        total_rounds: int, prob_win: Fraction, payout_ratio: Fraction
        ) -> dict[str, dict]:

    dataset = {}

    for strat, name in strategies:
        all_histories = []
        wins, ruins = 0, 0

        for _ in range(num_sim):
            history = get_capital_history(strat, init_capital, target,
                                          total_rounds, prob_win, payout_ratio)
            all_histories.append(history)

            final_capital = history[-1]
            if final_capital >= target:
                wins += 1
            if final_capital <= 0:
                ruins += 1

        final_caps = [x[-1] for x in all_histories]
        ev = sum(final_caps) / num_sim
        var = sum((x - ev) ** 2 for x in final_caps) / num_sim

        dataset[name] = {
            "stat" : {
                "win_rate" : (wins / num_sim),
                "ruin_rate" : (ruins / num_sim),
                "expected_value" : ev,
                "std_dev" : math.sqrt(var)
                },
            "data" : {
                "histories" : all_histories,
                "final_capitals" : final_caps
            }
        }
    return dataset