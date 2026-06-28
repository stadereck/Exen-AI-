from __future__ import annotations

import discord
from discord.ui import View, button, Button

from database.database import Database
from utils.embeds import success_embed, error_embed


class GiveawayJoinView(View):
    def __init__(self, giveaway_id: int, db: Database) -> None:
        super().__init__(timeout=None)
        self.giveaway_id = giveaway_id
        self.db = db

    @button(label="Participar", style=discord.ButtonStyle.success, emoji="🎉")
    async def join(self, interaction: discord.Interaction, button: Button) -> None:
        existing = await self.db.fetchone(
            "SELECT 1 FROM giveaway_entries WHERE giveaway_id = ? AND user_id = ?",
            (self.giveaway_id, interaction.user.id),
        )

        if existing:
            await interaction.response.send_message(
                embed=error_embed("Ya estás participando en este sorteo."),
                ephemeral=True,
            )
            return

        await self.db.execute(
            "INSERT INTO giveaway_entries (giveaway_id, user_id) VALUES (?, ?)",
            (self.giveaway_id, interaction.user.id),
        )

        await interaction.response.send_message(
            embed=success_embed("✅ Te has registrado correctamente en el sorteo."),
            ephemeral=True,
        )
