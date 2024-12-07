import arc
import hikari
import miru

from miru.ext import nav
from src.bot.components.decorators import exclusive_items
from src.edt.edt_grenoble_inp import EdtGrenobleInpClient, EdtGrenobleInpGroupsEnum


plugin = arc.GatewayPlugin("edt")

@plugin.include
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
    miru_client = miru.Client.from_arc(ctx.client)
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

    if exclusive is True:
        navigator = exclusive_items(
            nav.NavigatorView,
            ctx.user, 
            error_message=f"Interaction bloquée : cette vue appartient à <@{ctx.user.id}>."
        )(pages=embeds)
    else:
        navigator = nav.NavigatorView(pages=embeds)

    builder = await navigator.build_response_async(miru_client, start_at=2)
    await ctx.respond_with_builder(builder)
    miru_client.start_view(navigator)


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)

@arc.unloader
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin)
