from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
from random import randint
from discord import DMChannel
from discord.message import Message

# Load environment variables
load_dotenv()
TOKEN = os.getenv("Discord_Token")

# Setup bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Define the dice command
@bot.command(name="dice", help="Rolls a dice and returns a random number between 1 and 6.")
async def dice(ctx):
    """Rolls a dice and sends the result."""
    await ctx.send(f'You rolled: {randint(1, 6)}')

# Handle custom messages
@bot.event
async def on_message(message):
    # Skip if the message is from the bot itself
    if message.author == bot.user:
        return

    # Get the message content
    user_message = message.content

    # Check if the message starts with the prefix
    if user_message.startswith('!'):
        await bot.process_commands(message)  # Let the bot process commands
        return

    # Handle non-command messages (for responses)
    response = user_message + "not a recognized command"
    
    # Send the response in the same channel
    await message.channel.send(response)


# Define the clear command
@bot.command(name="clear", help="Clear a specified number of messages from the channel.")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    """
    Deletes the specified number of messages in the channel.
    """
    if amount < 1:
        await ctx.send("Please provide a number greater than 0.", delete_after=5)
        return

    try:
        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include the clear command message
        await ctx.send(f"🧹 Cleared {len(deleted) - 1} messages!", delete_after=5)
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}", delete_after=5)

# Error handler for the clear command
@clear.error
async def clear_error(ctx, error):
    """
    Handles errors for the clear command.
    """
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have the required permissions to clear messages.", delete_after=5)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Usage: !clear <number>", delete_after=5)
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please specify a valid integer for the number of messages to delete.", delete_after=5)
    else:
        await ctx.send("An unexpected error occurred while processing the command.", delete_after=5)

@bot.command(name='clear_dm', help="Clears the bot's messages in DMs.")
async def clear_dm(ctx, amount: int):
    """
    Clears the bot's messages in the DM channel.
    """
    if isinstance(ctx.channel, DMChannel):  # Check if it's a DM
        await ctx.send("Clearing messages...", delete_after=2)

        # Fetch the last 100 messages in the DM
        async for msg in ctx.channel.history(limit=100):
            if msg.author == bot.user:  # Check if the message was sent by the bot
                try:
                    await msg.delete()
                except Exception as e:
                    print(f"Error deleting message: {e}")

        await ctx.send("✅ Bot's messages cleared!, I can't clear yours as it is Forbidden", delete_after=5)
    else:
        await ctx.send("❌ This command can only be used in DMs.", delete_after=5)
        
@bot.event
async def on_ready():
    print(f"{bot.user} is now running!")

def main():
    bot.run(TOKEN)

if __name__ == "__main__":
    main()
