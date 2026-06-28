from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from database.database import Database
from utils.embeds import success_embed, error_embed, info_embed
from utils.permissions import has_admin_role


class Configuration(commands.Cog):
    """Cog para configurar canales clave y mostrar ajuste actuales."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db: Database = bot.db

    async def _ensure_admin(self, interaction: discord.Interaction) -> bool:
        if has_admin_role(interaction.user):
            return True

        await interaction.response.send_message(
            embed=error_embed("Solo **Owner** y **CoOwner** pueden usar este comando."),
            ephemeral=True,
        )
        return False

    @app_commands.command(name="set_channel", description="Configura un canal para bienvenida, logs o tickets.")
    @app_commands.describe(
        tipo="Tipo de configuración: welcome, logs, ticket_category.",
        canal="Canal de texto para la configuración."
    )
    @app_commands.choices(tipo=[
        app_commands.Choice(name="welcome", value="welcome"),
        app_commands.Choice(name="logs", value="logs"),
        app_commands.Choice(name="ticket_category", value="ticket_category"),
    ])
    async def set_channel(
        self,
        interaction: discord.Interaction,
        tipo: app_commands.Choice[str],
        canal: discord.TextChannel,
    ) -> None:
        if not await self._ensure_admin(interaction):
            return

        await self.db.set_config(f"{tipo.value}_id", str(canal.id))
        await interaction.response.send_message(
            embed=success_embed(f"✅ Canal {tipo.value} configurado en {canal.mention}."),
            ephemeral=True,
        )

    @app_commands.command(name="show_config", description="Muestra la configuración actual del bot.")
    async def show_config(self, interaction: discord.Interaction) -> None:
        if not await self._ensure_admin(interaction):
            return

        welcome_channel_id = await self.db.get_config("welcome_id")
        logs_channel_id = await self.db.get_config("logs_id")
        ticket_category_id = await self.db.get_config("ticket_category_id")

        welcome_channel = (
            f"<#{welcome_channel_id}>" if welcome_channel_id else "No configurado"
        )
        logs_channel = f"<#{logs_channel_id}>" if logs_channel_id else "No configurado"
        ticket_category = (
            f"<#{ticket_category_id}>" if ticket_category_id else "No configurado"
        )

        embed = info_embed(
            title="⚙️ Configuración actual",
            description="Canales y categoría configurados para el bot."
        )
        embed.add_field(name="Canal de bienvenida", value=welcome_channel, inline=False)
        embed.add_field(name="Canal de logs", value=logs_channel, inline=False)
        embed.add_field(name="Categoría de tickets", value=ticket_category, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Configuration(bot))
