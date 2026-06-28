from __future__ import annotations

import discord
from config.config import BotConfig


def has_admin_role(member: discord.Member | discord.User | None) -> bool:
    """Valida si el miembro es administrador por rol, por propietario del servidor o por permisos especiales."""
    if member is None:
        return False

    if isinstance(member, discord.Member):
        if member.guild.owner_id == member.id:
            return True

        allowed_role_names = {role_name.lower().strip() for role_name in BotConfig.OWNER_ROLES}
        member_role_names = {role.name.lower().strip() for role in member.roles}

        if member_role_names & allowed_role_names:
            return True

        return member.guild_permissions.administrator

    return False
