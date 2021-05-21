from Board import Board
from Player import Player
import Utilities as util

GAME_TITLE = '🔴 \t**Connect 4**\t 🟡'
BOARD_STATUS = 'Game: **{}** VS **{}**. Current turn: **{}**.\n\n{}'
PROMPT_TURN = "**{}**, It's your turn now! Enter command `() [0-6]` (column no) or react to the emojis" \
              " 0️⃣1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣ to make your move!"
WINNER_DETERMINED = 'The war ended with **{0}** being victorious over **{1}**! Congratulations **{0}**!'
INVALID_MOVE = '❌ **{}**, the move was invalid. Select again! ❌'
TIE = 'The war ended in a tie. Try again **{}** and **{}**! '


class GameInstance:
    def __init__(self, player1: Player, player2: Player):
        player1.status = Player.IN_GAME
        player2.status = Player.IN_GAME
        self.board: Board = Board()
        self.player1 = player1  # Player1 will be RED, and moves first
        self.player2 = player2  # Player2 will be YELLOW, and moves second
        self.turn = player1
        self.prev_msg = []
        self.is_busy = False     # A flag to indicate whether the game is ready. Because sending emoji takes time,
                                 # If a player reacts before emoji finish sending, the game will be messed up


    async def clear_prev_msg(self):
        """ Deletes all messages in self.prev_msg list """
        while len(self.prev_msg):
            msg = self.prev_msg.pop()
            if msg is not None:
                await msg.delete()


    async def action(self, column: int = None):
        """ Main function called when a player makes a move. Procedure are:
        Insert Token -> Check for game end -> Delete previous messages -> Print board -> Prompt move or announce result

        :returns True if the game is ended after current turn. Otherwise False
        """
        if self.is_busy:
            return

        status = None
        # The column is None when the game initializes and this function is called. Then, it only prints board
        # and prompt user for input. In other cases, we would want to insert a token into the board
        if column is not None:
            # Attempts to insert token. If failed, send error message and return
            if not self.board.insert_token(1 if self.turn == self.player1 else -1, column):
                await self.turn.channel.send(embed=util.create_embed(GAME_TITLE,
                                                                     INVALID_MOVE.format(self.turn.user.name)))
                return False
            status = self.board.check_win()
            self.change_side()

        self.is_busy = True
        await self.clear_prev_msg()
        await self.print_board(status)

        # The game continues
        if status is None:
            await self.prompt_input()
            self.is_busy = False
            return False
        else:
            await self.announce_result(status)
            return True


    async def announce_result(self, status: int):
        """ Send messages to both players, announcing the winner (or ties) according to the argument status.
        Also update the player's stats

        :param status: The status of the game. Either 1, -1 or 0 representing P1 win, P2 win and tie
        """
        if status == 0:
            embed = util.create_embed(GAME_TITLE,
                                      TIE.format(self.player1.user.name, self.player2.user.name))
            await util.send_embed(self.player1.channel, self.player2.channel, embed)
            self.player1.ties += 1
            self.player2.ties += 1
        elif status == 1:
            embed = util.create_embed(GAME_TITLE,
                                      WINNER_DETERMINED.format(self.player1.user.name, self.player2.user.name))
            await util.send_embed(self.player1.channel, self.player2.channel, embed)
            self.player1.wins += 1
            self.player2.losses += 1
        elif status == -1:
            embed = util.create_embed(GAME_TITLE,
                                      WINNER_DETERMINED.format(self.player2.user.name, self.player1.user.name))
            await util.send_embed(self.player1.channel, self.player2.channel, embed)
            self.player2.wins += 1
            self.player1.losses += 1



    def change_side(self):
        """ Changes the current turn of the game. P1 -> P2 and vice versa """
        self.turn = self.player1 if self.turn == self.player2 else self.player2


    async def print_board(self, status):
        """ Sends the board representation to both player's channel. Also appends the sent messages to the
        self.prev_msg list

        :param status: Status of the game. If 1, -1 or 0 (Game ended), no react (emoji) will be made by the bot
        """
        embed = util.create_embed(GAME_TITLE,
                                  BOARD_STATUS.format(self.player1.user.name, self.player2.user.name,
                                                      self.turn.user.name,
                                                      self.board))
        msgs = await util.send_embed(self.player1.channel, self.player2.channel, embed,
                                     ('0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣') if status is None else None)
        for m in msgs:
            self.prev_msg.append(m)


    async def prompt_input(self):
        """ Prompts whoever is in current turn to make their move. Sent message will be inserted into self.prev_msg """
        embed = util.create_embed(GAME_TITLE,
                                  PROMPT_TURN.format(self.turn.user.name))
        self.prev_msg.append( await self.turn.channel.send(embed=embed) )
