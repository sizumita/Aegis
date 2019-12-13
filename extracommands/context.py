from discord.ext import commands


class ExtraContext(commands.Context):
    def __init__(self, **attrs):
        super().__init__(**attrs)
        self.be_piped = attrs.pop('be_piped', False)
        self.passed_pipe_content = attrs.pop('passed_pipe_content', None)
        self.pipe_contents = []
        self.view_content = ''

    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None):
        if self.be_piped:
            if content:
                self.pipe_contents.append(str(content))
                return

        await super().send(content,
                           tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce)


class ContextGroup:
    def __init__(self, contexts):
        self.contexts = contexts
        self.bot = contexts[0].bot

    async def invoke(self):
        invoked_context = None
        for context in self.contexts:
            if invoked_context and invoked_context.pipe_contents:
                context.passed_pipe_content = '\n'.join(invoked_context.pipe_contents)
            await self.bot.invoke(context)
            invoked_context = context
