import hikari

from miru.ext.nav.items import NavButton
from miru.context.view import ViewContext


class StopAndRemoveComponentsButton(NavButton):
    def __init__(
        self,
        label=None,
        *,
        emoji=chr(9989),
        style=hikari.ButtonStyle.SUCCESS,
        disabled=False,
        custom_id=None,
        row=None,
        position=None,
        autodefer=hikari.UNDEFINED
    ):
        super().__init__(
            label,
            emoji=emoji,
            style=style,
            disabled=disabled,
            custom_id=custom_id,
            row=row,
            position=position,
            autodefer=autodefer,
        )

    async def callback(self, context: ViewContext) -> None:
        if not self.view.message and not self.view._inter:
            return

        for item in self.view.children:
            item.disabled = True

        if self.view._inter:
            await self.view._inter.edit_initial_response(components=None)
        elif self.view.message:
            await self.view.message.edit(components=None)

        self.view.stop()
