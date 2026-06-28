from __future__ import annotations

import asyncio
import random
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from database.database import Database
from utils.embeds import error_embed, success_embed, info_embed
from utils.permissions import has_admin_role
from utils.time import parse_duration
from views.giveaway import GiveawayJoinView


class Giveaways(commands.Cog):
    """Cog para sorteos con botones interactivos y cierre automático."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db: Database = bot.db
        self._background_task = self.bot.loop.create_task(self._watch_active_giveaways())

    async def cog_unload(self) -> None:
        self._background_task.cancel()

    async def _watch_active_giveaways(self) -> None:
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            try:
                rows = await self.db.fetchall(
                    "SELECT id, message_id, channel_id, prize, ends_at FROM giveaways WHERE active = 1"
                )
                now = datetime.utcnow()

                for row in rows:
                    ends_at = datetime.fromisoformat(row["ends_at"])
                    if now < ends_at:
                        continue

                    entries = await self.db.fetchall(
                        "SELECT user_id FROM giveaway_entries WHERE giveaway_id = ?",
                        (row["id"],),
                    )

                    if not entries:
                        await self.db.execute(
                            "UPDATE giveaways SET active = 0 WHERE id = ?",
                            (row["id"],),
                        )
                        continue

                    winner = random.choice(entries)["user_id"]
                    await self.db.execute(
                        "UPDATE giveaways SET active = 0, winner_id = ? WHERE id = ?",
                        (winner, row["id"]),
                    )

                    channel = self.bot.get_channel(int(row["channel_id"]))
                    if isinstance(channel, discord.TextChannel):
                        winner_mention = f"<@{winner}>"
                        embed = info_embed(
                            title="🎉 Sorteo finalizado",
                            description=(
                                f"El sorteo de **{row['prize']}** ha terminado.\n"
                                f"Ganador: {winner_mention}"
                            ),
                        )
                        await channel.send(embed=embed)

                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(30)

    @app_commands.command(name="giveaway", description="Crea un sorteo de canal con botón de participación.")
    @app_commands.describe(
        premio="Premio del sorteo.",
        duracion="Duración en formato 1d2h30m (por ejemplo)."
    )
    async def giveaway(
        self,
        interaction: discord.Interaction,
        premio: str,
        duracion: str,
    ) -> None:
        if not has_admin_role(interaction.user):
            await interaction.response.send_message(
                embed=error_embed("Solo **Owner** y **CoOwner** pueden crear sorteos."),
                ephemeral=True,
            )
            return

        delta = parse_duration(duracion)
        if delta is None:
            await interaction.response.send_message(
                embed=error_embed("Duración inválida. Usa el formato 1d2h30m."),
                ephemeral=True,
            )
            return

        ends_at = datetime.utcnow() + delta
        embed = info_embed(
            title="🎉 Nuevo sorteo creado",
            description=(
                f"Premio: **{premio}**\n"
                f"Termina en: <t:{int(ends_at.timestamp())}:R>"
            ),
        )

        giveaway_id = await self.db.execute(
            "INSERT INTO giveaways (message_id, channel_id, prize, ends_at, active) VALUES (?, ?, ?, ?, 1)",
            (0, interaction.channel.id, premio, ends_at.isoformat()),
        )

        view = GiveawayJoinView(int(giveaway_id), self.db)
        await interaction.response.send_message(embed=embed, view=view)
        message = await interaction.original_response()

        await self.db.execute(
            "UPDATE giveaways SET message_id = ?, channel_id = ? WHERE id = ?",
            (message.id, interaction.channel.id, int(giveaway_id)),
        )

        await interaction.followup.send(
            embed=success_embed("✅ Sorteo creado correctamente."),
            ephemeral=True,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Giveaways(bot))
