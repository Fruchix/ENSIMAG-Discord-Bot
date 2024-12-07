import hikari
import miru
import os
import arc

from dotenv import load_dotenv
from miru.ext import nav

from src.bot.components.decorators import exclusive_items
from src.edt.edt_grenoble_inp import EdtGrenobleInpClient, EdtGrenobleInpGroupsEnum

load_dotenv()
token = os.getenv("TOKEN")
guilds = os.getenv("GUILDS").split(",")

bot = hikari.GatewayBot(token)
arc_client = arc.GatewayClient(bot)
client = miru.Client.from_arc(arc_client)


@arc_client.include
@arc.slash_command("edt", "Ouvrir l'emploi du temps", is_dm_enabled=True)
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
            "Semaine : relativement à la semaine actuelle (1=sem suivante, -1=précédente, etc.)",
        ),
    ] = 0,
    exclusive: arc.Option[
        bool,
        arc.BoolParams(
            "Vue exclusive : personne d'autre ne peut interagir avec cette vue.",
        ),
    ] = True,
) -> None:
    edt = EdtGrenobleInpClient()

    group: EdtGrenobleInpGroupsEnum = EdtGrenobleInpGroupsEnum[group]

    embeds = []
    for i in range(-2, 3):
        edt.download_edt(group, week + i)

        embed = (
            hikari.Embed(
                title=f"Emploi du temps",
                color=hikari.Color.of(0x8dc63f),
            )
            .add_field("Groupe", group.value["name"], inline=True)
            .add_field("Semaine", edt.options.get_pretty_week(), inline=True)
            .set_image(f"data/edt-{group.name}-{edt.options.week_id}.png")
            .set_footer("📌 Stolen from ADE")
        )

        embeds.append(embed)

    if exclusive:
        navigator = exclusive_items(
            nav.NavigatorView,
            ctx.user, 
            error_message=f"Interaction bloquée : cette vue appartient à <@{ctx.user.id}>."
        )(pages=embeds)
    else:
        navigator = nav.NavigatorView(pages=embeds)

    builder = await navigator.build_response_async(client, start_at=2)
    await ctx.respond_with_builder(builder)
    client.start_view(navigator)


bot.run()
