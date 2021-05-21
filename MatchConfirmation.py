from Player import Player


class MatchConfirmation:
    """ A class for both match confirmation and rematch confirmation.

    Attributes:
        player1 - Player 1 of the match
        player2 - Player 2 of the match
        isP1Ready - Boolean value indicating whether player 1 is ready
        isP2Ready - Boolean value indicating whether player 2 is ready
    """
    def __init__(self, player1: Player, player2: Player):
        self.player1 = player1
        self.player2 = player2
        self.isP1Ready = False
        self.isP2Ready = False
