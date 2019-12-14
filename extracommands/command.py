from discord.ext import commands
from discord.ext.commands.errors import MissingRequiredArgument
from discord.ext.commands import converter as converters


class ExtraCommand(commands.Command):
    def __init__(self, func, **kwargs):
        super().__init__(func, **kwargs)
        self.invalid_pipe = kwargs.pop('invalid_pipe', False)

    async def transform(self, ctx, param):
        required = param.default is param.empty
        converter = self._get_converter(param)
        consume_rest_is_special = param.kind == param.KEYWORD_ONLY and not self.rest_is_raw
        view = ctx.view
        view.skip_ws()

        # The greedy converter is simple -- it keeps going until it fails in which case,
        # it undos the view ready for the next parameter to use instead
        if type(converter) is converters._Greedy:
            if param.kind == param.POSITIONAL_OR_KEYWORD:
                return await self._transform_greedy_pos(ctx, param, required, converter.converter)
            elif param.kind == param.VAR_POSITIONAL:
                return await self._transform_greedy_var_pos(ctx, param, converter.converter)
            else:
                # if we're here, then it's a KEYWORD_ONLY param type
                # since this is mostly useless, we'll helpfully transform Greedy[X]
                # into just X and do the parsing that way.
                converter = converter.converter

        if view.eof and not getattr(ctx, 'passed_pipe_content', None):
            if param.kind == param.VAR_POSITIONAL:
                raise RuntimeError()  # break the loop
            if required:
                if self._is_typing_optional(param.annotation):
                    return None
                raise MissingRequiredArgument(param)
            return param.default

        previous = view.index
        if consume_rest_is_special:
            argument = view.read_rest().strip()
            if not argument and getattr(ctx, 'passed_pipe_content', None):
                argument = ctx.passed_pipe_content
        else:
            word = view.get_quoted_word()
            if not word and getattr(ctx, 'passed_pipe_content', None):
                argument = ctx.passed_pipe_content
            else:
                argument = word

        view.previous = previous

        return await self.do_conversion(ctx, converter, argument, param)

