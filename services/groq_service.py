from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError(
        "Falta GROQ_API_KEY en el archivo .env. Añade tu clave de Groq para habilitar la IA."
    )

client = Groq(api_key=GROQ_API_KEY)


def ask(prompt: str) -> str:
    """Envía una consulta al servicio de IA Groq."""
    response: Any = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
