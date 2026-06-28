from __future__ import annotations

import discord
from discord import app_commands
from discord.ui import Modal, TextInput, View, button, Button

from database.database import Database
from utils.embeds import success_embed, error_embed
from utils.permissions import has_admin_role
from config.config import BotConfig


class TicketModal(Modal, title="Crear un ticket"):
    asunto = TextInput(
        label="Asunto del ticket",
        placeholder="Describe brevemente el motivo del ticket.",
        max_length=100,
    )
    descripcion = TextInput(
        label="Descripción detallada",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=500,
    )

    def __init__(self, db: Database, author: discord.Member) -> None:
        super().__init__()
        self.db = db
        self.author = author

    async def on_submit(self, interaction: discord.Interaction) -> None:
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                embed=error_embed("Este comando solo puede ejecutarse en un servidor."),
                ephemeral=True,
            )
            return

        ticket_category_id = await self.db.get_config("ticket_category_id")
        category = None
        if ticket_category_id is not None:
            category = discord.utils.get(guild.categories, id=int(ticket_category_id))

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            self.author: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True),
        }

        for role in guild.roles:
            if role.name in BotConfig.OWNER_ROLES:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)

        channel_name = f"ticket-{self.author.display_name}-{self.author.id}".lower()[:100]
        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            topic=f"Ticket de {self.author} ({self.author.id})",
            overwrites=overwrites,
        )

        await self.db.execute(
            "INSERT INTO tickets (user_id, channel_id, status, created_at) VALUES (?, ?, ?, ?)",
            (self.author.id, ticket_channel.id, "open", discord.utils.utcnow().isoformat()),
        )

        embed = discord.Embed(
            title="🎫 Ticket creado",
            description=(
                f"Tu ticket ha sido creado: {ticket_channel.mention}\n"
                "Un miembro del staff responderá en breve."
            ),
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Asunto", value=self.asunto.value, inline=False)
        embed.add_field(name="Descripción", value=self.descripcion.value or "No especificada.", inline=False)
        embed.set_footer(text="The Gala of Kindness")

        await ticket_channel.send(embed=embed, view=TicketCloseView(self.db, self.author.id))
        await interaction.response.send_message(
            embed=success_embed(f"✅ Ticket creado correctamente en {ticket_channel.mention}."),
            ephemeral=True,
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(
            embed=error_embed("Ocurrió un error al crear el ticket. Intenta de nuevo más tarde."),
            ephemeral=True,
        )


class TicketCloseView(View):
    def __init__(self, db: Database, author_id: int) -> None:
        super().__init__(timeout=None)
        self.db = db
        self.author_id = author_id

    @button(label="Cerrar ticket", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: Button) -> None:
        if not has_admin_role(interaction.user) and interaction.user.id != self.author_id:
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
            embed=success_embed("✅ Ticket cerrado. Este canal será eliminado en unos momentos."),
            ephemeral=True,
        )

        if interaction.channel is not None:
            await interaction.channel.delete(reason="Ticket cerrado")
