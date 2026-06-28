from __future__ import annotations

import discord
from discord.ext import commands

from database.database import Database
from utils.embeds import info_embed


class Welcome(commands.Cog):
    """Cog para enviar mensajes de bienvenida en canales configurados."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db: Database = bot.db

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        welcome_channel_id = await self.db.get_config("welcome_id")
        if welcome_channel_id is None:
            return

        channel = member.guild.get_channel(int(welcome_channel_id))
        if not isinstance(channel, discord.TextChannel):
            return

        embed = info_embed(
            title="🎉 Bienvenido",
            description=(
                f"¡Hola {member.mention}! Bienvenido a **{member.guild.name}**."
            ),
        )
        embed.add_field(
            name="¿Qué hacer ahora?",
            value="Lee las reglas, presenta tu cuenta y disfruta de la comunidad.",
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        await channel.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Welcome(bot))
