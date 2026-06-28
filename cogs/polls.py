from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from utils.embeds import error_embed, info_embed
from views.poll import PollView, build_poll_embed


class Polls(commands.Cog):
    """Cog para encuestas interactivas con Select Menus."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="poll", description="Crea una encuesta interactiva en el canal actual.")
    @app_commands.describe(
        pregunta="Texto de la encuesta.",
        opciones="Opciones separadas con '|', mínimo 2 y máximo 5."
    )
    async def poll(
        self,
        interaction: discord.Interaction,
        pregunta: str,
        opciones: str,
    ) -> None:
        items = [option.strip() for option in opciones.split("|") if option.strip()]

        if len(items) < 2 or len(items) > 5:
            await interaction.response.send_message(
                embed=error_embed("Debes usar entre 2 y 5 opciones separadas por '|'."),
                ephemeral=True,
            )
            return

        counts = {option: 0 for option in items}
        embed = build_poll_embed(pregunta, items, counts)
        view = PollView(pregunta, items)

        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Polls(bot))
