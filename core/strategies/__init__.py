from typing import Protocol
from core.models import StateSpace


class BettingStrategy(Protocol):
    def get_bet(self, state: StateSpace) -> int:
        ...