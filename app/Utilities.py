import discord


def create_embed(title: str, desc: str, color=0xe74c3c):
    """Creates a discord embed instance to be sent to channels.

    :param title (str): Title of the embed
    :param desc (str): Content of the embed
    :param color (int): Color of the side strip of embed. Defaults to 0xe74c3c (Red-ish)
    :return: Embed instance
    """
    return discord.Embed(title=title,
                         description=desc,
                         color=color)


async def send_embed(channel1, channel2, embed, emojis=None):
	"""Given two player's channel, send the embed to them. If both channels are same, then send only once
	If a list of emojis are provided, the bot will also react to the sent message

	:param channel1: Channel of player 1
	:param channel2: Channel of player 2
	:param embed: Embed to send to the channels
	:param emojis: List of emojis for the bot to react on the sent embed
	:return: Tuple of two messages that were sent to the two channels. If both channels are same, then returns
						(message, None)
	"""
	msg = await channel1.send(embed=embed)
	msg2 = None
	if channel1 != channel2:
			msg2 = await channel2.send(embed=embed)

	if emojis is not None:
			for e in emojis:
					await msg.add_reaction(e)
					if msg2 is not None:
						await msg2.add_reaction(e)
	return msg, msg2
