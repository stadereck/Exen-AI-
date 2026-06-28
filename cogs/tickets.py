from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from database.database import Database
from utils.embeds import success_embed, error_embed
from utils.permissions import has_admin_role
from views.ticket import TicketModal


class Tickets(commands.Cog):
    """Cog para sistema de tickets con Modal y botones."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db: Database = bot.db

    @app_commands.command(name="ticket", description="Abre un ticket privado para soporte.")
    async def ticket(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                embed=error_embed("Este comando solo puede ejecutarse dentro de un servidor."),
                ephemeral=True,
            )
            return

        await interaction.response.send_modal(TicketModal(self.db, interaction.user))

    @app_commands.command(name="close_ticket", description="Cierra el ticket actual (solo creador o staff).")
    async def close_ticket(self, interaction: discord.Interaction) -> None:
        if interaction.channel is None or interaction.guild is None:
            await interaction.response.send_message(
                embed=error_embed("No se pudo determinar el canal actual."),
                ephemeral=True,
            )
            return

        ticket = await self.db.fetchone(
            "SELECT user_id FROM tickets WHERE channel_id = ? AND status = ?",
            (interaction.channel.id, "open"),
        )
        if ticket is None:
            await interaction.response.send_message(
                embed=error_embed("Este canal no se encuentra registrado como un ticket abierto."),
                ephemeral=True,
            )
            return

        author_id = int(ticket["user_id"])
        if not has_admin_role(interaction.user) and interaction.user.id != author_id:
            await interaction.response.send_message(
                embed=error_embed("Solo el creador del ticket o un rol administrativo puede cerrarlo."),
                ephemeral=True,
            )
            return

        await self.db.execute(
            "UPDATE tickets SET status = ? WHERE channel_id = ?",
            ("closed", interaction.channel.id),
        )

        await interaction.response.send_message(
            embed=success_embed("✅ Ticket cerrado. El canal será eliminado."),
            ephemeral=True,
        )
        await interaction.channel.delete(reason="Ticket cerrado")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Tickets(bot))
