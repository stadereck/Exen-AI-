from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from utils.embeds import info_embed


class Core(commands.Cog):
    """Cog principal con comandos generales y de información."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ping", description="Muestra la latencia del bot.")
    async def ping(self, interaction: discord.Interaction) -> None:
        embed = info_embed(
            title="🏓 Pong!",
            description=f"Latencia: **{round(self.bot.latency * 1000)} ms**"
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="hola", description="Saluda en el servidor.")
    async def hola(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title="👋 ¡Hola!",
            description=(
                "Bienvenido al servidor oficial de\n"
                "**The Gala of Kindness** ❤️\n\n"
                "Esperamos que disfrutes tu estancia."
            ),
            color=discord.Color.blurple()
        )
        embed.set_footer(text="The Gala of Kindness")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="Muestra información del servidor.")
    async def serverinfo(self, interaction: discord.Interaction) -> None:
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "❌ Este comando solo funciona dentro de un servidor.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"📊 {guild.name}",
            color=discord.Color.green()
        )
        embed.add_field(name="Miembros", value=str(guild.member_count), inline=True)
        embed.add_field(name="Canales", value=str(len(guild.channels)), inline=True)
        embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Muestra información de un usuario.")
    @app_commands.describe(usuario="El usuario para mostrar información. Si no se especifica, se usa tu perfil.")
    async def userinfo(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member | None = None
    ) -> None:
        if usuario is None:
            usuario = interaction.user  # type: ignore[assignment]

        embed = discord.Embed(
            title=f"👤 {usuario.display_name}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=usuario.display_avatar.url)
        embed.add_field(name="ID", value=str(usuario.id), inline=False)
        embed.add_field(
            name="Cuenta creada",
            value=usuario.created_at.strftime("%d/%m/%Y"),
            inline=False
        )
        embed.add_field(
            name="Entró al servidor",
            value=usuario.joined_at.strftime("%d/%m/%Y") if usuario.joined_at else "Desconocido",
            inline=False
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Core(bot))
