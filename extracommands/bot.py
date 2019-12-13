from discord.ext import commands
from discord.ext.commands.bot import StringView
import discord
from .context import ExtraContext, ContextGroup
from .core import command
import copy


class Bot(commands.Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)

    def command(self, *args, **kwargs):
        def decorator(func):
            kwargs.setdefault('parent', self)
            result = command(*args, **kwargs)(func)
            self.add_command(result)
            return result

        return decorator

    async def process_commands(self, message):
        if message.author.bot:
            return
        for abreast_content in message.content.split(' & '):
            message.content = abreast_content
            invoked_context = None
            contexts = await self.get_contexts(message)
            for context in contexts:
                if invoked_context and invoked_context.pipe_contents:
                    context.passed_pipe_content = '\n'.join(invoked_context.pipe_contents)
                await self.invoke(context)
                invoked_context = context

    async def get_invoked_prefix(self, message):
        prefix = await self.get_prefix(message)
        view = StringView(message.content)
        try:
            # if the context class' __init__ consumes something from the view this
            # will be wrong.  That seems unreasonable though.
            if message.content.startswith(tuple(prefix)):
                return discord.utils.find(view.skip_string, prefix)
            return None

        except TypeError:
            return None

    async def get_context_groups(self, message):
        groups = []
        invoked_prefix = await self.get_invoked_prefix(message)
        if not invoked_prefix:
            return []

        for abreast_content in message.content.split(' & '):
            if not abreast_content.startswith(invoked_prefix):
                abreast_content = invoked_prefix + abreast_content.lstrip(' ')
            message.content = abreast_content
            contexts = await self.get_contexts(message)
            groups.append(ContextGroup(contexts))

        return groups

    async def get_contexts(self, message, *, cls=ExtraContext):
        prefix = await self.get_prefix(message)
        contexts = []
        command_contents = message.content.split(' |> ')

        _message = message
        _message.content = command_contents[0]

        view = StringView(command_contents.pop(0))
        ctx = cls(prefix=None, view=view, bot=self, message=_message)
        if command_contents:
            ctx.be_piped = True

        if self._skip_check(message.author.id, self.user.id):
            return [ctx]

        try:
            # if the context class' __init__ consumes something from the view this
            # will be wrong.  That seems unreasonable though.
            if message.content.startswith(tuple(prefix)):
                invoked_prefix = discord.utils.find(view.skip_string, prefix)
            else:
                return [ctx]

        except TypeError:
            if not isinstance(prefix, list):
                raise TypeError("get_prefix must return either a string or a list of string, "
                                "not {}".format(prefix.__class__.__name__))

            # It's possible a bad command_prefix got us here.
            for value in prefix:
                if not isinstance(value, str):
                    raise TypeError("Iterable command_prefix or list returned from get_prefix must "
                                    "contain only strings, not {}".format(value.__class__.__name__))

            # Getting here shouldn't happen
            raise

        invoker = view.get_word()
        ctx.invoked_with = invoker
        ctx.prefix = invoked_prefix
        ctx.command = self.all_commands.get(invoker)
        contexts.append(ctx)

        while command_contents:
            content = command_contents.pop(0)

            _message = message
            _message.content = invoked_prefix + content.lstrip(' ')

            ctx = self.get_ctx(_message, invoked_prefix, cls=cls)

            try:
                await ctx.command._parse_arguments(ctx)
            except Exception:
                ctx = self.get_ctx(_message, invoked_prefix, cls=cls)
            else:
                ctx = self.get_ctx(_message, invoked_prefix, cls=cls)
                contexts[-1].be_piped = False

            if command_contents:
                ctx.be_piped = True

            contexts.append(ctx)

        return contexts

    def get_ctx(self, message, invoked_prefix, *, cls=ExtraContext):
        view = StringView(message.content)
        ctx = cls(prefix=None, view=view, bot=self, message=message)
        ctx.prefix = invoked_prefix
        view.skip_string(invoked_prefix)

        invoker = view.get_word()
        ctx.invoked_with = invoker
        ctx.command = self.all_commands.get(invoker)

        return ctx



