from .command import ExtraCommand
from discord.ext import commands

# Decorators


def command(name=None, cls=None, **attrs):
    if cls is None:
        cls = ExtraCommand

    def decorator(func):
        if isinstance(func, commands.Command):
            raise TypeError('Callback is already a command.')
        return cls(func, name=name, **attrs)

    return decorator


def group(name=None, **attrs):
    attrs.setdefault('cls', commands.Group)
    return command(name=name, **attrs)
