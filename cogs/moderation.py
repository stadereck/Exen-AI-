from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from utils.embeds import error_embed, success_embed
from utils.permissions import has_admin_role


class Moderation(commands.Cog):
    """Cog para comandos de moderación con roles administrativos."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _require_admin(self, interaction: discord.Interaction) -> bool:
        if has_admin_role(interaction.user):
            return True

        await interaction.response.send_message(
            embed=error_embed("Solo **Owner** y **CoOwner** pueden usar este comando."),
            ephemeral=True
        )
        return False

    @app_commands.command(name="ban", description="Expulsa a un usuario del servidor.")
    @app_commands.describe(usuario="Usuario a banear.", razon="Razón para el ban.")
    async def ban(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        razon: str | None = None
    ) -> None:
        if not await self._require_admin(interaction):
            return

        await usuario.ban(reason=razon)
        await interaction.response.send_message(
            embed=success_embed(f"✅ {usuario.display_name} ha sido baneado."),
            ephemeral=True
        )

    @app_commands.command(name="kick", description="Expulsa a un usuario temporalmente.")
    @app_commands.describe(usuario="Usuario a expulsar.", razon="Razón para la expulsión.")
    async def kick(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        razon: str | None = None
    ) -> None:
        if not await self._require_admin(interaction):
            return

        await usuario.kick(reason=razon)
        await interaction.response.send_message(
            embed=success_embed(f"✅ {usuario.display_name} ha sido expulsado."),
            ephemeral=True
        )

    @app_commands.command(name="clear", description="Elimina mensajes del canal actual.")
    @app_commands.describe(cantidad="Cantidad de mensajes a eliminar.")
    async def clear(
        self,
        interaction: discord.Interaction,
        cantidad: int
    ) -> None:
        if not await self._require_admin(interaction):
            return

        deleted = await interaction.channel.purge(limit=cantidad)
        await interaction.response.send_message(
            embed=success_embed(f"✅ Se eliminaron {len(deleted)} mensajes."),
            ephemeral=True
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Moderation(bot))
