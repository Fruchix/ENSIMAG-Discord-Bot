import arc
import hikari
import miru
import logging

from miru.ext import nav
from pathlib import Path

from src.bot import logger
from src.bot.components.decorators import exclusive_items
from src.bot.components.buttons import StopAndRemoveComponentsButton
from src.edt.edt_grenoble_inp import (
    EdtGrenobleInpClient,
    EdtGrenobleInpGroupsEnum,
    EdtGrenobleInpOptions,
)
from src.utils.datetime_utils import get_week_id_relative_to_current

from src.config import EDT_DIR


plugin = arc.GatewayPlugin("edt")


@plugin.include
@arc.slash_command("edt", "Ouvrir l'emploi du temps", is_dm_enabled=True)
async def edt_command(
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
    group: EdtGrenobleInpGroupsEnum = EdtGrenobleInpGroupsEnum[group]

    if logger.level <= logging.INFO:
        str_week = f"{get_week_id_relative_to_current(EdtGrenobleInpOptions.FIRST_WEEK_MONDAY, week)}"
        str_context = (
            f"user.id='{ctx.user.id}',user.global_name='{ctx.user.global_name}',"
        )

        log_message = f"Command invoked in {'dm' if ctx.guild_id is None else 'guild'} for week='{str_week}',group='{group}'. Context: {str_context}"
        if ctx.guild_id is not None:
            log_message += f"guild.id='{ctx.guild_id}',guild.name='{ctx.get_guild().name}',user.display_name='{ctx.user.display_name}'"

        logger.info(log_message)

    miru_client = miru.Client.from_arc(ctx.client)
    edt = EdtGrenobleInpClient()

    embeds = []
    for i in range(-2, 3):
        edt.download_edt(group, week + i)

        embed = (
            hikari.Embed(
                title=f"Emploi du temps",
                color=hikari.Color.of(0x8DC63F),
            )
            .add_field("Groupe", group.value["name"], inline=True)
            .add_field("Semaine", edt.options.get_pretty_week(), inline=True)
            .set_image(Path(EDT_DIR, f"edt-{group.name}-{edt.options.week_id}.png"))
            .set_footer("📌 Stolen from ADE")
        )

        embeds.append(embed)

    buttons = [
        nav.PrevButton(),
        nav.IndicatorButton(),
        nav.NextButton(),
        StopAndRemoveComponentsButton(),
    ]

    if exclusive is True:
        navigator = exclusive_items(
            nav.NavigatorView,
            ctx.user,
            error_message=f"Interaction bloquée : cette vue appartient à <@{ctx.user.id}>.",
        )(pages=embeds, items=buttons)
    else:
        navigator = nav.NavigatorView(pages=embeds, items=buttons)

    builder = await navigator.build_response_async(miru_client, start_at=2)
    await ctx.respond_with_builder(builder)
    miru_client.start_view(navigator)


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)


@arc.unloader
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin)
