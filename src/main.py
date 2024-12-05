import hikari
import miru
import os
import arc

from dotenv import load_dotenv
from miru.ext import nav

from src.edt.edt_grenoble_inp import EdtGrenobleInpClient, EdtGrenobleInpGroupsEnum

load_dotenv()
token = os.getenv("TOKEN")
guilds = os.getenv("GUILDS").split(",")

bot = hikari.GatewayBot(token)
arc_client = arc.GatewayClient(bot)
client = miru.Client.from_arc(arc_client)


@arc_client.include
@arc.slash_command("edt", "Ouvrir l'emploi du temps", guilds=guilds)
async def my_command(
    ctx: arc.GatewayContext,
    group: arc.Option[
        str,
        arc.StrParams(
            "Groupe",
            choices={g.value["name"]: g.name for g in EdtGrenobleInpGroupsEnum},
        ),
    ],
    week: arc.Option[
        int,
        arc.IntParams(
            "Semaine",
        ),
    ] = 0,
) -> None:
    edt = EdtGrenobleInpClient()
    edt.options.set_week_starting_from_current(week)

    group: EdtGrenobleInpGroupsEnum = EdtGrenobleInpGroupsEnum[group]

    embeds = []
    current_week_id = edt.options.week
    for i in range(-2, 3):
        edt.download_edt(group, week + i)

        embed = (
            hikari.Embed(
                title=f"Emploi du temps",
            )
            .add_field("Groupe", group.value["name"], inline=True)
            .add_field("Semaine", edt.options.get_pretty_week(), inline=True)
            .set_image(f"data/edt-{group.name}-{current_week_id+i}.png")
        )

        embeds.append(embed)

    navigator = nav.NavigatorView(pages=embeds)

    builder = await navigator.build_response_async(client, start_at=2)
    await ctx.respond_with_builder(builder)
    client.start_view(navigator)


bot.run()
