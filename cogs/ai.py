from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from services.groq_service import ask
from utils.embeds import error_embed, info_embed


class AI(commands.Cog):
    """Cog para interacción con IA basada en Groq."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ai", description="Habla con la IA del servidor.")
    @app_commands.describe(pregunta="Pregunta o mensaje para la IA.")
    async def ai(self, interaction: discord.Interaction, pregunta: str) -> None:
        await interaction.response.defer(thinking=True)
        try:
            respuesta = ask(pregunta)
            embed = info_embed("🧠 Respuesta de IA", respuesta)
            await interaction.followup.send(embed=embed)
        except Exception as error:
            await interaction.followup.send(
                embed=error_embed("Ocurrió un error al procesar la IA. Intenta de nuevo más tarde."),
                ephemeral=True,
            )
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AI(bot))
