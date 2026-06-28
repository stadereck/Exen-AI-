from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()


@dataclass(frozen=True)
class BotConfig:
    TOKEN: str = os.getenv("TOKEN", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "database/bot.sqlite")
    GUILD_ID: int = int(os.getenv("GUILD_ID", "1507599533365002281"))
    OWNER_ROLES: tuple[str, ...] = ("Owner", "CoOwner")

    @classmethod
    def validate(cls) -> None:
        missing = []

        if not cls.TOKEN:
            missing.append("TOKEN")

        if not cls.GROQ_API_KEY:
            missing.append("GROQ_API_KEY")

        if missing:
            raise EnvironmentError(
                "Faltan variables de entorno: " + ", ".join(missing)
            )
