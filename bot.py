from __future__ import annotations

import asyncio
from pathlib import Path

import discord
from discord.ext import commands

from config.config import BotConfig
from database.database import Database

BASE_DIR = Path(__file__).resolve().parent


async def load_extensions() -> None:
    """Carga automáticamente todos los cogs en la carpeta cogs."""
    for path in sorted((BASE_DIR / "cogs").glob("*.py")):
        if path.name == "__init__.py":
            continue

        extension = f"cogs.{path.stem}"
        try:
            print("="*40)
print("TOKEN:", repr(BotConfig.TOKEN[:25]))
print("GROQ :", repr(BotConfig.GROQ_API_KEY[:15]))
print("="*40)
            print(f"✅ Cargada extension: {extension}")
        except Exception as error:
            print(f"❌ Error al cargar {extension}: {error}")


intents = discord.Intents.default()
intents.members = True
intents.message_content = False

bot = commands.Bot(command_prefix="!", intents=intents)


def _setup_working_directory() -> None:
    """Asegura que el bot se ejecute siempre desde el directorio raíz del proyecto."""
    import os

    os.chdir(BASE_DIR)


@bot.event
async def on_ready() -> None:
    try:
        await bot.tree.sync()
        print("===================================")
        print(f"✅ Conectado como {bot.user}")
        print("✅ Slash commands sincronizados.")
        print("===================================")
    except Exception as error:
        print(f"❌ Error al sincronizar comandos: {error}")


async def main() -> None:
    _setup_working_directory()
    BotConfig.validate()

    bot.db = Database()
    await bot.db.connect()

    await load_extensions()

    try:
        await bot.start(BotConfig.TOKEN)
    finally:
        await bot.db.close()


if __name__ == "__main__":
    asyncio.run(main())
