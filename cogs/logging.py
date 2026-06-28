from __future__ import annotations

import discord
from discord.ext import commands


class Logging(commands.Cog):
    """Cog con listeners de eventos para registrar acciones en un canal de logs."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def _get_log_channel(self, guild: discord.Guild) -> discord.TextChannel | None:
        return discord.utils.get(guild.text_channels, name="logs")

    async def _send_log(self, guild: discord.Guild, embed: discord.Embed) -> None:
        channel = self._get_log_channel(guild)
        if channel is None:
            return
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        embed = discord.Embed(
            title="Nuevo miembro",
            description=f"👋 {member.mention} se ha unido al servidor.",
            color=discord.Color.green()
        )
        embed.add_field(name="ID", value=str(member.id), inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        await self._send_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        embed = discord.Embed(
            title="Miembro salido",
            description=f"👋 {member.mention} ha salido del servidor.",
            color=discord.Color.orange()
        )
        embed.add_field(name="ID", value=str(member.id), inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        await self._send_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        if message.author.bot or message.guild is None:
            return

        embed = discord.Embed(
            title="Mensaje eliminado",
            description=message.content or "(Sin contenido)",
            color=discord.Color.red()
        )
        embed.add_field(name="Autor", value=message.author.mention, inline=True)
        embed.add_field(name="Canal", value=message.channel.mention, inline=True)
        embed.set_footer(text=f"ID mensaje: {message.id}")
        embed.timestamp = discord.utils.utcnow()
        await self._send_log(message.guild, embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Logging(bot))
