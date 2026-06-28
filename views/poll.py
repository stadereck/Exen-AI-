from __future__ import annotations

import discord
from discord.ui import View, Select

from utils.embeds import info_embed


def build_poll_embed(question: str, options: list[str], counts: dict[str, int]) -> discord.Embed:
    embed = info_embed("📊 Nueva encuesta", question)
    total_votes = sum(counts.values())
    for option in options:
        embed.add_field(
            name=option,
            value=f"{counts[option]} votos",
            inline=False,
        )
    embed.set_footer(text=f"Total de votos: {total_votes}")
    return embed


class PollSelect(Select):
    def __init__(self, options: list[str], counts: dict[str, int], voters: dict[int, str]) -> None:
        super().__init__(
            placeholder="Selecciona tu opción",
            min_values=1,
            max_values=1,
            options=[discord.SelectOption(label=option, value=option) for option in options],
        )
        self.counts = counts
        self.voters = voters

    async def callback(self, interaction: discord.Interaction) -> None:
        selected = self.values[0]
        previous_vote = self.voters.get(interaction.user.id)

        if previous_vote:
            self.counts[previous_vote] -= 1

        self.voters[interaction.user.id] = selected
        self.counts[selected] += 1

        embed = build_poll_embed(self.view.question, self.view.options, self.counts)
        await interaction.response.edit_message(embed=embed, view=self.view)
        await interaction.followup.send(
            f"✅ Tu voto ha sido registrado: **{selected}**.",
            ephemeral=True,
        )


class PollView(View):
    def __init__(self, question: str, options: list[str]) -> None:
        super().__init__(timeout=None)
        self.question = question
        self.options = options
        self.counts = {option: 0 for option in options}
        self.voters: dict[int, str] = {}
        self.add_item(PollSelect(options, self.counts, self.voters))
