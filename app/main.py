import sys

import discord
from decouple import config
import app.Utilities as util
from app.MatchMaker import MatchMaker
from app.GameHub import GameHub
from app.Player import Player
from app.keepAlive import app
from threading import Thread
import os

try:
    TOKEN = os.environ['TOKEN']
except Exception:
    print('Discord bot token not found in os.environ')
    TOKEN = config('TOKEN')
print(TOKEN)

TITLE = '🔴 \t** Simple Connect Four **\t 🟡'
HELP = '**A Simple Connect 4 Games with cross-channel, multiplayer support**\n' \
       '1. Type `() play` to join the matchmaking queue to be matched against an opponent!\n' \
       '2. Once you are matched with someone, type `() yes` for confirmation!\n' \
       '3. Once both parties had confirmed, the game of connect 4 will initiate!\n' \
       '4. Use `() [0-6]` or click emoji to decide which column to place your tokens once it is your turn\n' \
       '5. Once the game ended, you may request for rematch via `() rematch`, or `() quit` to quit\n' \
       '\n\n' \
       '**Other Commands:**\n' \
       '`() profile` - Shows your own profile\n' \
       '`() leave` - Leaves the matchmaking queue\n'
help_embed = util.create_embed(TITLE, HELP)

my_bot = discord.Client()

# ==========================
# Players List
# ==========================
# Note that if player list is not cleaned, it may bloat up in size when increasing usage
players_list = dict()

# ==========================
# Game's Matchmaking Lobby
# ==========================
match_maker = MatchMaker(my_bot.loop)

# ===========================
# Game Instances
# ===========================
game_hub = GameHub(my_bot.loop)


# ========================
# Discord bot Logics
# ========================
async def confirm(player: Player):
    ready_players = await match_maker.confirmation_by_player(player)
    if ready_players is None:
        return

    await game_hub.init_game(*ready_players)


async def make_move(player: Player, column: int):
    await game_hub.action(player, column)


async def get_profile(player: Player):
    await player.channel.send(embed=player.profile_embed())


async def help(player: Player):
    await player.channel.send(embed=help_embed)


bot_commands = {
    '() play': match_maker.request_to_join_queue,
    '() leave': match_maker.remove_from_queue,
    '() yes': confirm,
    '() profile': get_profile,
    '() rematch': game_hub.accept_rematch,
    '() quit': game_hub.reject_rematch,
    '() help': help,
    '() 0': lambda p: make_move(p, 0),
    '() 1': lambda p: make_move(p, 1),
    '() 2': lambda p: make_move(p, 2),
    '() 3': lambda p: make_move(p, 3),
    '() 4': lambda p: make_move(p, 4),
    '() 5': lambda p: make_move(p, 5),
    '() 6': lambda p: make_move(p, 6),
}


@my_bot.event
async def on_ready():
    print(f"AdmiBot logged in as {my_bot.user}")

@my_bot.event
async def on_message(msg):
    # Not a command or it is own bot message. Simply return
    if msg.author == my_bot.user or msg.content not in bot_commands:
        return

    user = msg.author
    channel = msg.channel

    # New user! Put into the player's list
    if user.id not in players_list:
        players_list[user.id] = Player(user, channel)
    # In any way, update the channel
    players_list[user.id].update_channel(channel)

    # Execute the command
    await bot_commands[msg.content](players_list[user.id])


EMOJI_MAP = {
    '0️⃣': 0,
    '1️⃣': 1,
    '2️⃣': 2,
    '3️⃣': 3,
    '4️⃣': 4,
    '5️⃣': 5,
    '6️⃣': 6
}


@my_bot.event
async def on_reaction_add(reaction, user):
    if user.id not in players_list or reaction.emoji not in EMOJI_MAP:
        return

    player = players_list[user.id]
    await game_hub.action(player, EMOJI_MAP[reaction.emoji])

t = Thread(target=app.run)
t.start()
my_bot.run(TOKEN)
