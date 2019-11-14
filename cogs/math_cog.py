from discord.ext import commands
from typing import Union
import math


class Math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gcd(self, ctx, a: int, b: int):
        """整数aとbの最大公約数を返します。"""
        await ctx.send(math.gcd(a, b))

    @commands.command()
    async def fabs(self, ctx, x: Union[int, float]):
        """xの絶対値を返します。"""
        await ctx.send(math.fabs(x))

    @commands.command(name='ln')
    async def log(self, ctx, x: Union[int, float], base: Union[int, float, None] = None):
        """引数が1つの場合、x の (e を底とする)自然対数を返します。
        引数が2つの場合、log(x)/log(base) として求められる base を底とした x の対数を返します。"""
        await ctx.send(math.log(x, base))

    @commands.command()
    async def log1p(self, ctx, x: Union[int, float]):
        """1+x の自然対数(つまり底 e の対数)を返します。"""
        await ctx.send(math.log1p(x))

    @commands.command()
    async def log2(self, ctx, x: Union[int, float]):
        """2を底とする x の対数を返します。"""
        await ctx.send(math.log2(x))

    @commands.command()
    async def log10(self, ctx, x: Union[int, float]):
        """x の10を底とした対数(常用対数)を返します。"""
        await ctx.send(math.log10(x))

    @commands.command()
    async def sin(self, ctx, x: Union[int, float]):
        """x ラジアンの正弦を返します。"""
        await ctx.send(math.sin(x))

    @commands.command()
    async def cos(self, ctx, x: Union[int, float]):
        """x ラジアンの余弦を返します。"""
        await ctx.send(math.cos(x))

    @commands.command()
    async def tan(self, ctx, x: Union[int, float]):
        """x ラジアンの正接を返します。"""
        await ctx.send(math.tan(x))

    @commands.command()
    async def asin(self, ctx, x: Union[int, float]):
        """x の逆正弦を、ラジアンで返します。"""
        await ctx.send(math.asin(x))

    @commands.command()
    async def acos(self, ctx, x: Union[int, float]):
        """x の逆余弦を、ラジアンで返します。"""
        await ctx.send(math.acos(x))

    @commands.command()
    async def atan(self, ctx, x: Union[int, float]):
        """x の逆正接を、ラジアンで返します。"""
        await ctx.send(math.atan(x))

    @commands.command()
    async def degrees(self, ctx, x: Union[int, float]):
        """角 x をラジアンから度に変換します。"""
        await ctx.send(math.degrees(x))

    @commands.command()
    async def radians(self, ctx, x: Union[int, float]):
        """角 x を度からラジアンに変換します。"""
        await ctx.send(math.radians(x))

    @commands.command()
    async def rpn(self, ctx, *, formula):
        calcs = {
            # l: list, (計算結果, 計算に使った数字の個数)
            '*': lambda l: (l[1] * l[0], 2),
            '/': lambda l: (l[1] / l[0], 2),
            '-': lambda l: (l[1] - l[0], 2),
            '+': lambda l: (l[1] + l[0], 2),
            '**': lambda l: (l[1] ** l[0], 2),
            'sin': lambda l: (math.sin(l[0]), 1),
            'cos': lambda l: (math.cos(l[0]), 1),
            'tan': lambda l: (math.tan(l[0]), 1),
            'sqrt': lambda l: (math.sqrt(l[0]), 1),
            'gcd': lambda l: (math.gcd(l[0], l[1]), 2),

        }
        algebras = {
            'pi': math.pi,
        }
        result = []
        try:
            for x in formula.split(' '):
                if x in calcs.keys():
                    c = calcs[x](result[::-1])
                    del result[-1 * c[1]:]
                    result.append(c[0])
                    continue

                if x in algebras.keys():
                    result.append(algebras[x])
                    continue

                result.append(float(x) if "." in x else int(x))
                continue
        except:
            await ctx.send("計算エラー")
            raise
        await ctx.send(result[0])


def setup(bot):
    return bot.add_cog(Math(bot))
