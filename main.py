"""
Main file of sheffield uni freshers comp sci discord bot.

Authored by:
Felix Randle
"""
import os
from discord.ext import commands

import database

# Load our login details from environment variables and check they are set
BOT_TOKEN = os.getenv("BOT_TOKEN")

if BOT_TOKEN is None:
    raise Exception("Cannot find required bot token.")

# Set our bot's prefix to ! this must be typed before any command
bot = commands.Bot(command_prefix="$")
db = database.Database()


@bot.event
async def on_ready():
    """Run post-launch setup."""
    print(f'{bot.user.name} has successfully connected to Discord!')

    # Load all of our cogs
    if os.path.exists("./cogs"):
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                bot.load_extension("cogs." + file[:-3])
                print(f"Loaded cog {file[:-3]}")


@bot.event
async def on_guild_join(guild):
    registering_id = None
    member_id = None
    for role in guild.roles:
        if role.name.lower() == "registering":
            registering_id = role.id
        if role.name.lower() == "member":
            member_id = role.id

    db.add_guild(guild.id, registering_id, member_id)


@bot.event
async def on_member_join(member):
    """Send user a welcome message."""
    await member.create_dm()
    await member.dm_channel.send(
        f'Hey {member.name}, welcome to the University of Sheffield Computer '
        'Science Freshers Discord!\n'
        'We like to know who we\'re talking to, so please change your '
        'nickname on the server to include your real name in some way.\n'
        'Apart from that, have fun on the server, get to know people and '
        'feel free to ask any questions about the course that you may have, '
        'we\'re all here to help each other!\n'
        'Many thanks,\n'
        'The Discord Server Admin Team'
    )

    db.add_user(member)

    role_id = await db.get_guild_info(member.guild.id, "registeringID")

    await add_role(member, role_id)


@bot.event
async def on_raw_reaction_add(payload):
    if payload.member.bot:
        return

    expected_id = await db.get_guild_info(payload.guild_id, "welcomeMessageID")
    if payload.message_id == expected_id:
        message = await payload.member.guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
        await message.remove_reaction(payload.emoji, payload.member)
        if payload.emoji.name == u"\u2705":
            registering_id = await db.get_guild_info(payload.guild_id, "registeringID")
            member_id = await db.get_guild_info(payload.guild_id, "memberID")

            await add_role(payload.member, member_id)
            await remove_role(payload.member, registering_id)

        elif payload.emoji.name == u"\u274E":
            await payload.member.guild.kick(payload.member, reason="Rejected T's&C's")


@bot.event
async def on_command_error(ctx, error):
    """Handle any command errors that may appear."""
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send(
            "You do not have the correct permissions for this command."
            "If you believe this is an error, please contact an Admin.")


async def add_role(member, role_id):
    role = member.guild.get_role(role_id)

    if role:
        await member.add_roles(role)


async def remove_role(member, role_id):
    role = member.guild.get_role(role_id)

    if role:
        await member.remove_roles(role)

# Start the bot
print("Starting bot...")
bot.run(BOT_TOKEN)
