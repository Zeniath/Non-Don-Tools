from discord.ext import commands
import asyncio
import traceback
import discord
import inspect
import textwrap
from platform import python_version
from contextlib import redirect_stdout
import typing
import io
import copy
from .utils import checks
import functools
from typing import Union

# to expose to the eval command
import datetime
from collections import Counter

class Modules:
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    async def __local_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    def get_syntax_error(self, e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    @staticmethod
    def try_multiple(operations, *args, **kwargs) -> typing.Optional[Exception]:
        """
        Does multiple operations on a set of arguments, returning an exception if there was one.
        :param operations: Iterable of operations to perform
        :param args: Arguments to pass to each operation
        :param kwargs: Keyword arguments to pass to each operation
        :return: The exception object, if there was one.
        """
        try:
            for operation in operations:
                operation(*args, **kwargs)
        except Exception as exc:
            return exc

    def format_extension_management(self, operations, extension_name) -> str:
        """
        Does operations with an extension name, returning a difflist entry based on whether it succeeded.
        :param operations: Operations to perform (load_command, etc)
        :param extension_name: The extension name
        :return: Diff list entry
        """

        exception = self.try_multiple(operations, extension_name)
        if exception:
            return f"- \N{CROSS MARK} {extension_name}\n! {exception.__class__.__name__}: {exception!s:.75}"
        else:
            return f"+ \N{WHITE HEAVY CHECK MARK} {extension_name}"

    @commands.command(hidden=True)
    async def load(self, ctx, *module):
        """Loads a module"""
        modules = '\n\n'.join(map(functools.partial(self.format_extension_management,
                                                      (self.bot.load_extension,)), module))
        await ctx.send(f'Trying to **load** {len(module)} modules. \n`\n{modules}\n`')

    @commands.command(hidden=True)
    async def unload(self, ctx, *module):
        """Unloads a module"""
        modules = '\n\n'.join(map(functools.partial(self.format_extension_management,
                                                      (self.bot.unload_extension,)), module))
        await ctx.send(f'Trying to **unload** {len(module)} modules. \n`\n{modules}\n`')

    @commands.command(hidden=True)
    async def reload(self, ctx, *module):
        """Reloads a module"""
        modules = '\n\n'.join(map(functools.partial(self.format_extension_management,
                                                      (self.bot.unload_extension, self.bot.load_extension)), module))
        await ctx.send(f'Trying to **reload** {len(module)} modules. \n`\n{modules}\n`')

def setup(bot):
    bot.add_cog(Modules(bot))