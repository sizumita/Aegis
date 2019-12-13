from discord.ext import commands
import discord
import re
from extracommands import core
from .utils.generating import draw_lines, draw_string


change_types = {
    ('s', 'size'): int,
    ('width', 'bw'): float,
}
name_to_kwargs = {
    's': 'size',
    'b': 'border',
    'width': 'border_width',
    'bw': 'border_width',
    'c': 'color',
    'bc': 'background',
}


class Moji(commands.Cog):
    already_on = True

    def __init__(self, bot):
        self.bot = bot

    @core.group(invoke_without_command=True)
    async def moji(self, ctx, *, text):
        """テキストを画像にして表示します。カスタム絵文字・ユニコード絵文字も使用可能です。複数行表示可能です。"""
        if '\n' in text:
            buffer = await draw_lines(ctx, text)
        else:
            buffer = await draw_string(ctx, text)

        await ctx.send(file=discord.File(buffer, filename='image.png'))

    @moji.command()
    async def discord(self, ctx, *, text):
        """Discordのロゴのフォントを使用します。英語・数字・記号のみ対応です。カスタム絵文字・ユニコード絵文字も使用可能です。複数行表示可能です。"""
        if '\n' in text:
            buffer = await draw_lines(ctx, text, font='./cogs/utils/otf/Uni Sans Heavy.otf')
        else:
            buffer = await draw_string(ctx, text, font='./cogs/utils/otf/Uni Sans Heavy.otf')

        await ctx.send(file=discord.File(buffer, filename='image.png'))

    @moji.command()
    async def custom(self, ctx, *, contents):
        """色などをカスタマイズして画像として表示するコマンドです。１行目に設定、２行目以降に文章を書いてください。複数行表示可能です。
        カスタマイズの設定は、`パラメーター1=値 パラメーター2=値`のような書式で指定してください。
        また、画像ファイルを添付した場合、
        **パラメーター一覧([]内はエイリアスです)**
        size[s]: 文字のサイズを指定します。デフォルト: 100
        color[c]: 文字色を指定します。デフォルト: #7289DA
        background[bc]: 背景色を指定します。デフォルト: なし
        border[b]: ボーダーラインの色を指定します。デフォルト: #23272A
        width[bw]: ボーダーラインの幅を指定します。デフォルト: 1.2
        """
        params, *texts = contents.split('\n')

        #  スペースが入っていても対応する
        params = params.split('=')
        params = '='.join([s.strip(' ') for s in params])

        params = params.split(' ')
        payload = {}
        for param in params:
            if match := re.match(r'(.+)=(.+)', param):
                name, value = match.groups()

                #  適切なタイプに変形
                for p, _type in change_types.items():
                    if name in p:
                        value = _type(value)

                #  適切な名前に変形
                if name in name_to_kwargs:
                    name = name_to_kwargs[name]

                payload[name] = value

        text = '\n'.join(texts)

        if '\n' in text:
            buffer = await draw_lines(ctx, text, **payload)
        else:
            buffer = await draw_string(ctx, text, **payload)

        await ctx.send(file=discord.File(buffer, filename='image.png'))


def setup(bot):
    return bot.add_cog(Moji(bot))
