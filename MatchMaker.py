from collections import OrderedDict
import asyncio

import Utilities as util
from Player import Player
from MatchConfirmation import MatchConfirmation

MATCHMAKING_TITLE = '⚔️ **Match Making** ⚔️'
ALREADY_IN_QUEUE = '⏳ **{}**, you are already in queue! Currently waiting for an opponent... ⏳'
ALREADY_IN_GAME = '🛑 **{}**, you are already in game! 🛑'
MATCHMAKING_PROGRESS = '⏳ **{}**, Match Making in process... Please wait patiently for opponent to emerge... ⏳'
MATCHED_MSG = "Opponent Matched! The war will begin shortly between **{}** and **{}**! Prepare to Fight! 🤺"
PROMPT_CONFIRM = 'Both **{}** and **{}**, Please enter `() yes` command to confirm match! Expires in 30 seconds... ⏳'
REMOVED_FROM_QUEUE = '**{}** successfully ran away from matchmaking queue 🏃💨'

CONFIRMATION_RECEIVED = '**{}**, Received your confirmation ✅'
CONFIRMED_MATCH = 'Both parties (**{}** vs **{}**) are confirmed! Initiating battle... ⚔️'
FAILED_CONFIRM = 'We do not receive confirmation from both parties (**{}** vs **{}**) within 30 secs... Adding you ' \
                 'back into tbe matchmaking queue (only if you\'ve confirmed previously)... ⏳'

GAME_STARTING = '**{}** and **{}**, Both parties had confirmed! Let the game begin...⚔️'


class MatchMaker:
    """ A Match Making Manager. Handles match making so players could find their opponent. Also handles
    players confirmation once match is made, so that players don't get matched with AFK players
    Internally, uses OrderedDict so to give random access in O(1) and still able to pop in FIFO order

    Attributes:
        queue - The ordered dict for general matchmaking
        confirmations - Dictionary for confirmations
        event_loop - The event loop used for the callback function 30 seconds timeout for confirmations
    """
    def __init__(self, event_loop):
        self.queue = OrderedDict()
        self.confirmations = dict()
        self.event_loop = event_loop


    # A Player had send confirmation message. If both sides are confirmed, returns tuple size 2 of players, indicating
    # that a game could be started.
    async def confirmation_by_player(self, player: Player):
        if player.user.id in self.confirmations:
            confirmation_obj = self.confirmations[player.user.id]
            confirmation_obj.isP1Ready = \
                True if player.user.id == confirmation_obj.player1.user.id else confirmation_obj.isP1Ready
            confirmation_obj.isP2Ready = \
                True if player.user.id == confirmation_obj.player2.user.id else confirmation_obj.isP2Ready
            await player.channel.send(embed=util.create_embed(MATCHMAKING_TITLE,
                                                              CONFIRMATION_RECEIVED.format(player.user.name)))

            if confirmation_obj.isP1Ready and confirmation_obj.isP2Ready:
                player1, player2 = confirmation_obj.player1, confirmation_obj.player2
                self.confirmations.pop(player1.user.id, None)
                self.confirmations.pop(player2.user.id, None)
                embed = util.create_embed(MATCHMAKING_TITLE, GAME_STARTING.format(player1.user.name, player2.user.name))

                await util.send_embed(player1.channel, player2.channel, embed)
                return player1, player2


    # Waits for 30 sec, then check whether both sides have confirmed or not.
    # If players are absent in confirmation dict, that means the players are confirmed and already been popped out
    # from the dict, so do nothing
    # Otherwise, send messages notifying that not all parties confirmed. Those who confirmed will be added back into
    # queue
    async def confirmation_callback(self, player1: Player, player2: Player):
        await asyncio.sleep(30)
        if player1.user.id in self.confirmations:
            isPlayerOneReady = self.confirmations.pop(player1.user.id, None).isP1Ready
            isPlayerTwoReady = self.confirmations.pop(player2.user.id, None).isP2Ready
            embed = util.create_embed(MATCHMAKING_TITLE, FAILED_CONFIRM.format(player1.user.name, player2.user.name))

            await player1.channel.send(embed=embed)
            if player1.channel != player2.channel:
                await player2.channel.send(embed=embed)

            player1.status = Player.IDLE
            player2.status = Player.IDLE
            if isPlayerOneReady:
                await self.request_to_join_queue(player1)
            if isPlayerTwoReady:
                await self.request_to_join_queue(player2)


    # Removes a player from the waiting queue (Not From Confirmation Queue)
    async def remove_from_queue(self, player: Player):
        # Only remove if the player is indeed in the queue
        if player.user.id in self.queue:
            player.status = Player.IDLE
            self.queue.pop(player.user.id)
            await player.channel.send(embed=util.create_embed(MATCHMAKING_TITLE,
                                                              REMOVED_FROM_QUEUE.format(player.user.name)))

    # Requests for a player to join the queue
    async def request_to_join_queue(self, player: Player):
        # Player is already in game or in queue
        if player.status == Player.IN_GAME:
            await player.channel.send(embed=util.create_embed(MATCHMAKING_TITLE,
                                                              ALREADY_IN_GAME.format(player.user.name)))
        elif player.status == Player.MATCH_MAKING:
            await player.channel.send(embed=util.create_embed(MATCHMAKING_TITLE,
                                                              ALREADY_IN_QUEUE.format(player.user.name)))
        # Queue is empty. Push to queue
        elif not len(self.queue):
            self.queue[player.user.id] = player
            player.status = Player.MATCH_MAKING
            await player.channel.send(embed=util.create_embed(MATCHMAKING_TITLE,
                                                              MATCHMAKING_PROGRESS.format(player.user.name)))
        # Queue is not empty! Immediately match them together!
        else:
            player.status = Player.MATCH_MAKING
            _, opponent = self.queue.popitem(last=False)
            match_confirmation = MatchConfirmation(player, opponent)

            self.confirmations[player.user.id] = match_confirmation
            self.confirmations[opponent.user.id] = match_confirmation

            # The two players are from the same channel
            matched_embed = util.create_embed(MATCHMAKING_TITLE,
                                              MATCHED_MSG.format(player.user.name, opponent.user.name) )
            prompt_confirm_embed = util.create_embed(MATCHMAKING_TITLE,
                                                     PROMPT_CONFIRM.format(player.user.name, opponent.user.name) )
            await util.send_embed(player.channel, opponent.channel, matched_embed )
            await util.send_embed(player.channel, opponent.channel, prompt_confirm_embed )

            # Create 30 sec countdown if they don't confirm
            self.event_loop.create_task(self.confirmation_callback(player, opponent))
