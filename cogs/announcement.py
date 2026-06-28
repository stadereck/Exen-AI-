from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from utils.embeds import error_embed, success_embed
from utils.permissions import has_admin_role


class Announcement(commands.Cog):
    """Cog para publicar noticias y anuncios en el servidor."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="press_news", description="Publica una noticia en el canal actual.")
    @app_commands.describe(
        titulo="Título de la noticia.",
        descripcion="Contenido de la noticia.",
        imagen="URL de imagen opcional para la noticia."
    )
    async def press_news(
        self,
        interaction: discord.Interaction,
        titulo: str,
        descripcion: str,
        imagen: str | None = None
    ) -> None:
        if not has_admin_role(interaction.user):
            await interaction.response.send_message(
                embed=error_embed("Solo **Owner** y **CoOwner** pueden usar este comando."),
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"📰 {titulo}",
            description=descripcion,
            color=discord.Color.gold()
        )
        embed.set_author(name="The Gala of Kindness News")
        embed.set_footer(text=f"Publicado por {interaction.user.display_name}")
        embed.timestamp = discord.utils.utcnow()

        if imagen:
            embed.set_image(url=imagen)

        await interaction.channel.send(embed=embed)
        await interaction.response.send_message(
            embed=success_embed("✅ Noticia publicada correctamente."),
            ephemeral=True
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Announcement(bot))
