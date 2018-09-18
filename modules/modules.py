from discord.ext import commands
import asyncio
import traceback
import discord
import inspect
import textwrap
from platform import python_version
from contextlib import redirect_stdout
import io
import copy
from .utils import checks
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

    @commands.command(hidden=True)
    async def load(self, ctx, *, module):
        """Loads a module"""
        try:
            self.bot.load_extension(f"modules.{module}")
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send(f'Loaded module: `{module}`')

    @commands.command(hidden=True)
    async def unload(self, ctx, *, module):
        """Unloads a module"""
        try:
            self.bot.unload_extension(f"modules.{module}")
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send(f'Unloaded module: `{module}`')

    @commands.command(hidden=True)
    async def reload(self, ctx, *, module):
        """Reloads a module"""
        try:
            self.bot.unload_extension(f"modules.{module}")
            self.bot.load_extension(f"modules.{module}")
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send(f'Reloaded module: `{module}`')

def setup(bot):
    bot.add_cog(Modules(bot))