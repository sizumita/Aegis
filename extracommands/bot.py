from discord.ext import commands
from discord.ext.commands.bot import StringView
import discord
from .context import ExtraContext, ContextGroup
from .core import command


class ContentSplit:
    text = ''


class Text(ContentSplit):
    def __init__(self, bot, text):
        self.bot = bot
        self.text = text.lstrip(' ')

    def __add__(self, other: ContentSplit):
        self.text += other.text

    def is_command(self, invoked_prefix):
        view = StringView(self.text)
        if self.text.startswith(invoked_prefix):
            view.skip_string(invoked_prefix)

        invoker = view.get_word()
        cmd = self.bot.all_commands.get(invoker)
        if cmd:
            return True

        return False


class Symbol(ContentSplit):
    def __init__(self, message, symbol):
        self.message = message
        self.text = symbol

    def __add__(self, other: ContentSplit):
        return self.text + other.text


def rebase_symbols(bot, text, symbol):
    contents = text.split(symbol)
    _ = []
    if text.startswith(symbol):
        _.append(Symbol(bot, symbol))

    _.append(Text(bot, contents.pop(0)))

    while contents:
        _.append(Symbol(bot, symbol))
        content = contents.pop(0)
        _.append(Text(bot, content))

    return _


def union(splits, invoked_prefix):
    _ = []
    for _split in splits:
        if isinstance(_split, Symbol):
            _.append(_split)
            continue

        if _split.is_command(invoked_prefix):
            _.append(_split)
            continue

        _.append(_split)

        while not _[-1].is_command(invoked_prefix):
            _[-2] + _[-1]

    return _


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

    async def _get_context_groups(self, message):
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

    async def get_context_groups(self, message):
        invoked_prefix = await self.get_invoked_prefix(message)
        if not invoked_prefix:
            return []

        not_parsed_groups = union(rebase_symbols(self, message.content, ' & '), invoked_prefix)
        groups = []

        for group in not_parsed_groups:
            if isinstance(group, Symbol):
                continue

            contexts = await self.get_contexts(message, group, invoked_prefix)
            groups.append(ContextGroup(contexts))

        return groups

    async def get_contexts(self, message, group, invoked_prefix, *, cls=ExtraContext):
        
        not_parsed_contents = union(rebase_symbols(self, group.text, ' |> '), invoked_prefix)
        contexts = []

        first_content = not_parsed_contents.pop(0)
        view = StringView(first_content.text)
        ctx = cls(prefix=None, view=view, bot=self, message=message)

        if not_parsed_contents:
            ctx.be_piped = True

        if self._skip_check(message.author.id, self.user.id):
            return [ctx]

        if first_content.text.startswith(invoked_prefix):
            view.skip_string(invoked_prefix)

        invoker = view.get_word()
        ctx.invoked_with = invoker
        ctx.prefix = invoked_prefix
        ctx.command = self.all_commands.get(invoker)
        contexts.append(ctx)

        while not_parsed_contents:
            content = not_parsed_contents.pop(0)
            if isinstance(content, Symbol):
                continue

            view = StringView(content.text)
            ctx = cls(prefix=None, view=view, bot=self, message=message)
            ctx.prefix = invoked_prefix
            if content.text.startswith(invoked_prefix):
                view.skip_string(invoked_prefix)

            invoker = view.get_word()
            ctx.command = self.all_commands.get(invoker)

            try:
                await ctx.command._parse_arguments(ctx)
            except commands.MissingRequiredArgument:
                ctx = self.get_ctx(StringView(content.text), message, invoked_prefix, content.text)
            else:
                ctx = self.get_ctx(StringView(content.text), message, invoked_prefix, content.text)
                contexts[-1].be_piped = False

            if not_parsed_contents:
                ctx.be_piped = True

            contexts.append(ctx)

        return contexts

    async def _get_contexts(self, message, *, cls=ExtraContext):
        prefix = await self.get_prefix(message)
        contexts = []
        command_contents = message.content.split(' |> ')

        first_content = command_contents.pop(0)
        view = StringView(first_content)
        ctx = cls(prefix=None, view=view, bot=self, message=message)
        ctx.view_content = first_content
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

            # _message = message
            view_content = invoked_prefix + content.lstrip(' ')

            ctx = self.get_ctx(message, view_content, invoked_prefix, cls=cls)

            if not ctx.command:
                view_content = contexts[-1].view_content + ' |> ' + content
                ctx = self.get_ctx(message, view_content, invoked_prefix, cls=cls)
                ctx.be_piped = contexts[-1].be_piped
                if not command_contents:
                    ctx.be_piped = False

                contexts[-1] = ctx
                continue

            try:
                await ctx.command._parse_arguments(ctx)
            except commands.MissingRequiredArgument:
                ctx = self.get_ctx(message, view_content, invoked_prefix, cls=cls)
            else:
                ctx = self.get_ctx(message, view_content, invoked_prefix, cls=cls)
                contexts[-1].be_piped = False

            if command_contents:
                ctx.be_piped = True

            contexts.append(ctx)

        return contexts

    def _get_ctx(self, message, view_content, invoked_prefix, *, cls=ExtraContext):
        view = StringView(view_content)
        ctx = cls(prefix=None, view=view, bot=self, message=message)
        ctx.prefix = invoked_prefix
        view.skip_string(invoked_prefix)

        invoker = view.get_word()
        ctx.invoked_with = invoker
        ctx.command = self.all_commands.get(invoker)
        ctx.view_content = view_content

        return ctx

    def get_ctx(self, view, message, invoked_prefix, content, *, cls=ExtraContext):
        ctx = cls(prefix=None, view=view, bot=self, message=message)
        ctx.prefix = invoked_prefix
        if content.startswith(invoked_prefix):
            view.skip_string(invoked_prefix)

        invoker = view.get_word()
        ctx.command = self.all_commands.get(invoker)

        return ctx



