from discord.ext import tasks
from Commands.free_games import get_steamdb_free_games, get_epic_free_games

@tasks.loop(hours=1)
async def check_free_games_task(bot):
    channel_id = 123456789012345678  # Replace with your channel ID
    channel = bot.get_channel(channel_id)

    if not channel:
        print(f"Channel with ID {channel_id} not found.")
        return

    steam_games = get_steamdb_free_games()
    epic_games = get_epic_free_games()

    for game in steam_games + epic_games:
        await channel.send(game)
