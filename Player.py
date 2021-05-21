import discord
import Utilities as util

PROFILE_TXT = "Name: **{}**\n" \
              "Wins: **{}**\n" \
              "Losses: **{}**\n" \
              "Ties: **{}**\n" \
              "Status: **{}**\n"


class Player:
    """ A class representing a player.

    Class Constants:
        IDLE - One of the statuses. Player is not in game nor in matchmaking process
        MATCH_MAKING - One of the statuses. Player is in matchmaking process
        IN_GAME - One of the statuses. Player is currently in game with another player

    Attributes:
        user - Discord User object of the player
        channel - Discord channel where the last activity of the player was in
        wins - Number of times the player had won against another
        losses - Number of times the player had lost against another
        ties - Number of times the player ended in a tie with another
        status - Status of the player.
    """
    IDLE = 'Idle'
    MATCH_MAKING = 'Match Making'
    IN_GAME = 'In Game'

    def __init__(self, user: discord.Member, channel: discord.abc.Messageable):
        self.user = user
        self.channel = channel
        self.wins = 0
        self.losses = 0
        self.ties = 0
        self.status = Player.IDLE


    def update_channel(self, channel: discord.abc.Messageable):
        """ Sets the player's channel to the channel provided in the argument

        :param channel: The channel to be set
        """
        self.channel = channel


    def profile_embed(self):
        """ Returns an Discord Embed object which shows the details of the Player. The Embed is meant to be sent
        to text channels

        :return: Embed object with details of the Player
        """
        return util.create_embed('💳\tProfile\t💳', PROFILE_TXT.format(self.user.name,
                                                                       self.wins,
                                                                       self.losses,
                                                                       self.ties,
                                                                       self.status))
