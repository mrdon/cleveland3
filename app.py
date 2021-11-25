from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List

MAX_ATTEMPTS = 1_000_000

NUM_DICE = 5


@dataclass
class Dice:
    value: int

    @staticmethod
    def roll():
        return Dice(value=random.randint(1, 6))


class Turn:

    kept_dice: List[Dice]

    def __init__(self):
        self.kept_dice = []

    def roll(self) -> List[Dice]:
        num = NUM_DICE - len(self.kept_dice)
        return [Dice.roll() for _ in range(num)]

    def keep(self, *dice: Dice):
        assert 1 <= len(dice) <= (NUM_DICE - len(self.kept_dice))
        self.kept_dice.extend(dice)

    @property
    def over(self):
        return len(self.kept_dice) == NUM_DICE


class Player:
    turn: Turn

    def __init__(self, name: str, strategy: Strategy):
        self.name = name
        self.strategy = strategy
        self.turn = Turn()

    def do_round(self, game: Game):
        dice = self.turn.roll()
        kept_dice = self.strategy(game, self, dice)
        self.turn.keep(*kept_dice)

    @property
    def score(self):
        score = 0
        for d in self.turn.kept_dice:
            if d.value != 3:
                score += d.value
        return score


class Strategy:
    def __call__(self, game: Game, player: Player, dice: List[Dice]) -> List[Dice]:
        raise NotImplemented

    def __str__(self):
        return self.__class__.__name__


class RandomStrategy(Strategy):
    def __call__(self, game: Game, player: Player, dice: List[Dice]) -> List[Dice]:
        return [random.choice(dice)]


class SimpleStrategy(Strategy):
    def __call__(self, game: Game, player: Player, dice: List[Dice]) -> List[Dice]:
        keep = []
        for die in dice:
            if die.value == 3:
                keep.append(die)

        if not keep:
            keep = [min(dice, key=lambda d: d.value)]

        return keep


class KeepOnesStrategy(Strategy):
    def __call__(self, game: Game, player: Player, dice: List[Dice]) -> List[Dice]:
        keep = []
        for die in dice:
            if die.value in (3, 1):
                keep.append(die)

        if not keep:
            keep = [min(dice, key=lambda d: d.value)]

        return keep


class KeepOnesAndTwosStrategy(Strategy):
    def __call__(self, game: Game, player: Player, dice: List[Dice]) -> List[Dice]:
        keep = []
        for die in dice:
            if die.value in (3, 1, 2):
                keep.append(die)

        if not keep:
            keep = [min(dice, key=lambda d: d.value)]

        return keep


class KeepOnesUnlessLosingStrategy(Strategy):
    def __call__(self, game: Game, player: Player, dice: List[Dice]) -> List[Dice]:
        keep = []
        for die in dice:
            if die.value == 3:
                keep.append(die)
            elif die.value == 1:
                prior_scores = [p.score for p in game.players if p.turn.over]
                if len(prior_scores) > 0 and min(prior_scores) > player.score:
                    keep.append(die)

        if not keep:
            keep = [min(dice, key=lambda d: d.value)]

        return keep


class Game:
    players: List[Player]

    def __init__(self, players: List[Player]):
        self.players = players

    def play(self):

        active_players = list(self.players)
        for player in active_players:
            while not player.turn.over:
                player.do_round(self)

        winners: List[Player] = []
        for player in self.players:
            if not winners:
                winners.append(player)
            elif player.score < winners[0].score:
                winners.clear()
                winners.append(player)
            elif player.score == winners[0].score:
                winners.append(player)

        return winners


def run():
    # strategies = [RandomStrategy(), SimpleStrategy(), KeepOnesStrategy(), KeepOnesUnlessLosingStrategy(),
    #               KeepOnesAndTwosStrategy()]
    strategies = [SimpleStrategy(), KeepOnesUnlessLosingStrategy()]

    scores = {str(s): 0 for s in strategies}
    for attempt in range(MAX_ATTEMPTS):
        if attempt % 10000 == 0:
            print(f"Attempt: {attempt}")
        players = [Player(str(s), s) for s in strategies]
        # random.shuffle(players)
        players.reverse()
        game = Game(players)
        winners = game.play()
        for winner in (w for w in winners if len(winners) == 1):
            scores[str(winner.strategy)] = scores[str(winner.strategy)] + 1

    for strategy, score in scores.items():
        print(f"{strategy}: {(score / MAX_ATTEMPTS) * 100}%")


if __name__ == "__main__":
    run()
