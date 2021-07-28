from app.GameInstance import GameInstance
from app.Player import Player
import app.Utilities as util
from app.MatchConfirmation import MatchConfirmation
import asyncio


GAMEHUB_TITLE = '♟️Game Hub ♟️'
REMATCH_PROMPT = 'That was a great match **{}** and **{}**! Would you like a rematch? Type `() rematch` for rematch and' \
                 ' `() quit` to stop playing. Timing out in 30 seconds..'
REMATCH_CONFIRMED = '**{}**, Your request for rematch is confirmed! ✅'
REMATCH_TIMEOUT = 'The rematch request between **{}** and **{}** had timed out after 30 seconds 🕑. See you later! 🙋‍♂️'
QUIT_CONFIRMED = '**{}** had cancelled the rematch. See you soon! 🙋‍♂️'
REMATCH_START = 'A rematch between **{}** and **{}** is starting! How exciting 💪'


class GameHub:
    """ Manages all of the ongoing game instances. There should be only one gamehub instance created.
    Also manages the rematch requests after a game has ended.

    Attributes:
        gamehub - A Dictionary containing Player -> Game Instance
        rematches - A Dictionary containing Player -> MatchConfirmation (For Rematch)
        event_loop - Event loop used for the async 30 second timeout
    """
    def __init__(self, event_loop):
        self.gamehub = dict()
        self.rematches = dict()
        self.event_loop = event_loop


    # Runs after 30 seconds to check if the rematch confirmation is still pending
    async def rematch_callback(self, key):
        await asyncio.sleep(30)
        rematch_req = self.rematches.pop(key, None)
        if rematch_req is None:
            return

        self.rematches.pop(rematch_req.player2, None)
        rematch_req.player1.status = Player.IDLE
        rematch_req.player2.status = Player.IDLE

        embed = util.create_embed(GAMEHUB_TITLE,
                                  REMATCH_TIMEOUT.format(rematch_req.player1.user.name, rematch_req.player2.user.name))
        await util.send_embed(rematch_req.player1.channel, rematch_req.player2.channel, embed)


    # When a player rejects the rematch request, immediately remove the rematch request and notify both parties
    async def reject_rematch(self, player):
        rematch_req = self.rematches.pop(player, None)
        if rematch_req is None:
            return
        player1, player2 = rematch_req.player1, rematch_req.player2
        self.rematches.pop(player1, None)
        self.rematches.pop(player2, None)
        player1.status = Player.IDLE
        player2.status = Player.IDLE

        embed = util.create_embed(GAMEHUB_TITLE,
                                  QUIT_CONFIRMED.format(player1.user.name, player2.user.name) )
        await util.send_embed(player1.channel, player2.channel, embed)


    # A player had accepted rematch.
    async def accept_rematch(self, player):
        rematch_req = self.rematches.get(player, None)
        if rematch_req is None:
            return
        rematch_req.isP1Ready = True if player == rematch_req.player1 else rematch_req.isP1Ready
        rematch_req.isP2Ready = True if player == rematch_req.player2 else rematch_req.isP2Ready

        await player.channel.send(embed=util.create_embed(GAMEHUB_TITLE,
                                                          REMATCH_CONFIRMED.format(player.user.name)))

        # Both parties had agreed for a rematch! init a game session
        if rematch_req.isP1Ready and rematch_req.isP2Ready:
            player1, player2 = rematch_req.player1, rematch_req.player2
            # Remove from confirmation first
            self.rematches.pop(player1, None)
            self.rematches.pop(player2, None)

            # Send prompt message
            embed = util.create_embed(GAMEHUB_TITLE,
                                      REMATCH_START.format(player1.user.name, player2.user.name))
            await util.send_embed(player1.channel, player2.channel, embed)

            # Init a new game session. Note that inversion of player1 and player2 occurs here
            await self.init_game(player2, player1)


    # Starts a new game given 2 players
    async def init_game(self, player1: Player, player2: Player):
        game = GameInstance(player1, player2)
        self.gamehub[player1] = game
        self.gamehub[player2] = game

        await game.action()


    # Called when player makes a action. Put tokens into the board, check win etc...
    async def action(self, player: Player, column: int):
        if player not in self.gamehub or self.gamehub[player].turn != player:
            return
        is_end = await self.gamehub[player].action(column)

        # RAN ONLY IF GAME ENDED ================
        # Game ended. Wait for rematch requests
        if is_end:
            # Remove the game instance from the game hub dictionary
            game = self.gamehub.pop(player, None)
            player1, player2 = game.player1, game.player2
            self.gamehub.pop(player1, None)
            self.gamehub.pop(player2, None)

            # Push into rematch dictionary.
            rematch_req = MatchConfirmation(player1, player2)
            self.rematches[player1] = rematch_req
            self.rematches[player2] = rematch_req

            # Prompts for rematch
            rematch_prompt = util.create_embed(GAMEHUB_TITLE,
                                               REMATCH_PROMPT.format(game.player1.user.name, game.player2.user.name))
            await util.send_embed(game.player1.channel, game.player2.channel, rematch_prompt)

            # After 30 seconds, the rematch request time out
            self.event_loop.create_task( self.rematch_callback(game.player1) )






