import discord
from discord.ext import commands, tasks
from datetime import datetime, time, timezone, timedelta
from Utils.fetch_games import get_steamdb_free_games, get_epic_free_games
from Database.models import session, BotConfig

SGT_OFFSET = timedelta(hours=8)  # Singapore Time (UTC+8)
SGT_TZ = timezone(SGT_OFFSET)  # Define Singapore timezone

def setup_free_games_commands(bot):
    
    def get_free_games_channel():
        """Retrieve the stored free games channel from the database."""
        config = session.query(BotConfig).first()
        return config.free_games_channel if config else None

    def set_free_games_channel(channel_id):
        """Store the free games announcement channel in the database."""
        config = session.query(BotConfig).first()
        if config:
            config.free_games_channel = channel_id
        else:
            config = BotConfig(free_games_channel=channel_id)
            session.add(config)
        session.commit()

    def remove_free_games_channel():
        """Remove the stored free games announcement channel."""
        config = session.query(BotConfig).first()
        if config:
            session.delete(config)
            session.commit()
            return True
        return False

    def get_scheduled_time():
        """Retrieve the stored time for free games updates in SGT."""
        config = session.query(BotConfig).first()
        return config.free_games_time if config else "12:00"

    def set_scheduled_time(hour, minute):
        """Store the new time for free games updates (SGT)."""
        config = session.query(BotConfig).first()
        if config:
            config.free_games_time = f"{hour:02}:{minute:02}"
        else:
            config = BotConfig(free_games_time=f"{hour:02}:{minute:02}")
            session.add(config)
        session.commit()

    @bot.command()
    async def freegames(ctx):
        """Manually fetch and display free games."""
        await fetch_and_send_free_games(ctx.channel)

    @bot.command()
    async def setfreegameschannel(ctx):
        """Set the current channel as the free games update channel."""
        set_free_games_channel(ctx.channel.id)
        await ctx.send(f"✅ This channel ({ctx.channel.mention}) is now set for daily free game updates!")

    @bot.command()
    async def getfreegameschannel(ctx):
        """Display the current free games reminder channel."""
        channel_id = get_free_games_channel()
        if channel_id:
            channel = bot.get_channel(channel_id)
            if channel:
                await ctx.send(f"📢 Free games updates are sent in: {channel.mention}")
            else:
                await ctx.send(f"⚠️ The stored channel ID `{channel_id}` is not found.")
        else:
            await ctx.send("❌ No free games channel is currently set.")

    @bot.command()
    async def removefreegameschannel(ctx):
        """Remove the free games reminder channel."""
        if remove_free_games_channel():
            await ctx.send("🗑️ Free games reminder channel has been **removed**.")
        else:
            await ctx.send("❌ No free games reminder channel was set.")

    @bot.command()
    async def setfreegamestime(ctx, hour: int, minute: int):
        """Set the daily time (SGT) for free games updates."""
        if 0 <= hour < 24 and 0 <= minute < 60:
            set_scheduled_time(hour, minute)  # Store time in DB
            restart_scheduled_task()  # Restart scheduler with new time
            await ctx.send(f"⏰ Free games updates will now be sent daily at **{hour:02}:{minute:02} SGT (UTC+8)**!")
        else:
            await ctx.send("❌ Invalid time. Please enter a valid 24-hour format time. Example: `!setfreegamestime 14 30`")

    @bot.command()
    async def getfreegamestime(ctx):
        """Get the current scheduled time for free games updates in SGT."""
        current_time = get_scheduled_time()
        await ctx.send(f"⏰ Free games updates are currently scheduled for **{current_time} SGT (UTC+8)**.")

    @tasks.loop(time=time(12, 0, tzinfo=SGT_TZ))  # Default time in SGT
    async def scheduled_free_games():
        """Fetch and send free games at the scheduled time in SGT."""
        channel_id = get_free_games_channel()
        if channel_id:
            channel = bot.get_channel(channel_id)
            if channel:
                await fetch_and_send_free_games(channel)
            else:
                print("⚠️ Channel not found. Ensure the bot has access.")

    async def fetch_and_send_free_games(channel):
        """Fetch free games and send them to a specific channel."""
        try:
            steam_games = await get_steamdb_free_games()
            epic_games = get_epic_free_games()

            if steam_games:
                await channel.send("🎮 **Free Steam Games:**")
                for game in steam_games:
                    await channel.send(
                        f"**{game['title']}**\n{game['description']}\n[More Info]({game['url']})"
                    )

            if epic_games:
                await channel.send("🎮 **Free Epic Games:**")
                for game in epic_games:
                    await channel.send(
                        f"**{game['title']}**\n{game['description']}\n[More Info]({game['url']})"
                    )

            if not steam_games and not epic_games:
                await channel.send("No free games found today.")

        except Exception as e:
            print(f"Error fetching free games: {e}")
            await channel.send("An error occurred while fetching free games.")

    def restart_scheduled_task():
        """Restart the scheduled task with the new time in SGT."""
        scheduled_free_games.stop()  # Stop current loop
        time_parts = get_scheduled_time().split(":")
        new_hour, new_minute = int(time_parts[0]), int(time_parts[1])
        scheduled_free_games.change_interval(time=time(new_hour, new_minute, tzinfo=SGT_TZ))
        scheduled_free_games.start()  # Restart with new time


    @bot.event
    async def on_ready():
        """Load the saved channel and time, then start the scheduler."""
        time_parts = get_scheduled_time().split(":")
        new_hour, new_minute = int(time_parts[0]), int(time_parts[1])
        scheduled_free_games.change_interval(time=time(new_hour, new_minute, tzinfo=SGT_TZ))
        scheduled_free_games.start()
        print(f"{bot.user} is ready and the scheduled task is running at {new_hour:02}:{new_minute:02} SGT (UTC+8)!")

