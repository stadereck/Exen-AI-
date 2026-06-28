from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass(frozen=True)
class BotConfig:
    print("TOKEN:", TOKEN[:20] if TOKEN else "No encontrado")
print("GROQ:", GROQ_API_KEY[:20] if GROQ_API_KEY else "No encontrada")
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "database/bot.sqlite")
    GUILD_ID: int = int(os.getenv("GUILD_ID", "1507599533365002281"))
    OWNER_ROLES: tuple[str, ...] = ("Owner", "CoOwner")

    @classmethod
    def validate(cls) -> None:
        missing: list[str] = []

        if not cls.TOKEN:
            missing.append("TOKEN")

        if not cls.GROQ_API_KEY:
            missing.append("GROQ_API_KEY")

        if missing:
            raise EnvironmentError(
                "Faltan variables de entorno: " + ", ".join(missing) + 
                ". Añade estas claves a tu archivo .env."
            )
