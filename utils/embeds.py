import discord


def info_embed(title: str, description: str) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.blurple()
    )
    embed.set_footer(text="The Gala of Kindness")
    return embed


def success_embed(description: str) -> discord.Embed:
    embed = discord.Embed(
        description=description,
        color=discord.Color.green()
    )
    embed.set_footer(text="The Gala of Kindness")
    return embed


def error_embed(description: str) -> discord.Embed:
    embed = discord.Embed(
        description=description,
        color=discord.Color.red()
    )
    embed.set_footer(text="The Gala of Kindness")
    return embed
