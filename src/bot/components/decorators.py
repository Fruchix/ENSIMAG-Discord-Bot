from hikari import User
from hikari import MessageFlag
from miru.view import View
from miru.context.view import ViewContext


def exclusive_items(cls: View, user: User, error_message: str | None = None) -> View:
    """Edit a View class so that its interactive items can only be used by the
      user from which the view was started.

    :param cls: the class to edit
    :type: cls: View
    :param user: the only user that should be able to interact with the items
    :type user: User
    :param error_message: the error message to print whenever someone else tries to interact
    :type error_message: str | None, defaults to None
    :return: the edited class, ready to be instanciated
    :rtype: View
    """
    cls_init = cls.__init__

    # redefine the View class' "__init__" method
    def __init__(self, *args, **kwargs):
        old_add_item = self.add_item

        # dynamically redefining the "add_item" method from the "__init__" method
        def new_add_item(item):
            # dynamically redefine the "callback" method from the "add_item" method,
            # ONLY if it has one: some items are not meant to be interactive
            try:
                old_callback = item.callback

                item._exclusive_user = user

                async def new_callback(context: ViewContext):
                    if item._exclusive_user.id != context.user.id:
                        if error_message is not None:
                            await context.respond(
                                error_message, flags=MessageFlag.EPHEMERAL
                            )
                        return
                    return await old_callback(context)

                item.callback = new_callback
            except AttributeError:
                pass
            finally:
                return old_add_item(item)

        self.add_item = new_add_item
        cls_init(self, *args, **kwargs)

    cls.__init__ = __init__
    return cls
