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
import asyncio
from typing import Union

# to expose to the eval command
import datetime
from collections import Counter

class Admin:
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

    async def _basic_cleanup_strategy(self, ctx, search):
        count = 0
        async for msg in ctx.history(limit=search, before=ctx.message):
            if msg.author == ctx.me:
                await msg.delete()
                count += 1
        return { 'Bot': count }

    async def _complex_cleanup_strategy(self, ctx, search):
        prefixes = tuple(self.bot.get_guild_prefixes(ctx.guild)) # thanks startswith

        def check(m):
            return m.author == ctx.me or m.content.startswith(prefixes)

        deleted = await ctx.channel.purge(limit=search, check=check, before=ctx.message)
        return Counter(m.author.display_name for m in deleted)

    @commands.command(aliases=['eval'], hidden=True)
    @commands.is_owner()
    async def evaluate(self, ctx, *, body: str):
        
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'
        
        try:
            exec(to_compile, env)
        except Exception as e:
            fooem = discord.Embed(color=0xff0000)
            fooem.add_field(name="Code evaluation was not successful. <:pepesad:455483563064819713>", value=f'```\n{e.__class__.__name__}: {e}\n```')
            fooem.set_footer(text=f"Evaluated using Python Version {python_version()}", icon_url="http://i.imgur.com/9EftiVK.png")
            fooem.timestamp = ctx.message.created_at
            return await ctx.send(embed=fooem)

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            fooem = discord.Embed(color=0xff0000)
            fooem.add_field(name="Code evaluation was not successful. <:pepesad:455483563064819713>", value=f'```py\n{value}{traceback.format_exc()}\n```')
            fooem.set_footer(text=f"Evaluated using Python Version {python_version()}", icon_url="http://i.imgur.com/9EftiVK.png")
            fooem.timestamp = ctx.message.created_at
            await ctx.send(embed=fooem)
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction(':white_check_mark:')
            except:
                pass

            if ret is None:
                if value:
                    sfooem = discord.Embed(color=discord.Colour.green())
                    sfooem.add_field(name="Code evaluation was successful! <:yay:451178223720595456>", value=f'```py\n{value}\n```')
                    sfooem.set_footer(text=f"Evaluated using Python Version {python_version()}", icon_url="http://i.imgur.com/9EftiVK.png")
                    sfooem.timestamp = ctx.message.created_at
                    await ctx.send(embed=sfooem)
            else:
                self._last_result = ret
                ssfooem = discord.Embed(color=discord.Colour.green())
                ssfooem.add_field(name="Code evaluation was successful! <:yay:451178223720595456>", value=f'```py\n{value}{ret}\n```')
                ssfooem.set_footer(text=f"Evaluated using Python Version {python_version()}", icon_url="http://i.imgur.com/9EftiVK.png")
                ssfooem.timestamp = ctx.message.created_at
                await ctx.send(embed=ssfooem)

    @commands.command(hidden=True)
    async def sql(self, ctx, *, query: str):
        """Run some SQL"""
        from .utils.formats import TabularData, Plural
        import time

        query = self.cleanup_code(query)

        is_multistatement = query.count(';') > 1
        if is_multistatement:
            # fetch does not support multiple statements
            strategy = self.bot.db.execute
        else:
            strategy = self.bot.db.fetch

        try:
            start = time.perf_counter()
            results = await strategy(query)
            dt = (time.perf_counter() - start) * 1000.0
        except Exception:
            return await ctx.send(f'```py\n{traceback.format_exc()}\n```')

        rows = len(results)
        if is_multistatement or rows == 0:
            return await ctx.send(f'`{dt:.2f}ms: {results}`')

        headers = list(results[0].keys())
        table = TabularData()
        table.set_columns(headers)
        table.add_rows(list(r.values()) for r in results)
        render = table.render()

        fmt = f'```\n{render}\n```\n*Returned {Plural(row=rows)} in {dt:.2f}ms*'
        await ctx.send(fmt)

    @commands.command(aliases=['runas', 'as'], hidden=True)
    async def sudo(self, ctx, who: Union[discord.Member, discord.User], *, command: str):
        """Run a command as another user"""
        msg = copy.copy(ctx.message)
        msg.author = who
        msg.content = ctx.prefix + command
        new_ctx = await self.bot.get_context(msg)
        await self.bot.invoke(new_ctx)

    @commands.command(aliases=['clean'], hidden=True)
    @checks.has_permissions(manage_messages=True)
    async def cleanup(self, ctx, search=10):
        """Cleans up the bot's messages from the channel
        If a search number is specified, it searches that many messages to delete.
        If the bot has Manage Messages permissions then it will try to delete
        messages that look like they invoked the bot as well.
        After the cleanup is completed, the bot will send you a message with
        which people got their messages deleted and their count. This is useful
        to see which users are spammers.
        You must have Manage Messages permission to use this.
        """

        strategy = self._basic_cleanup_strategy
        if ctx.me.permissions_in(ctx.channel).manage_messages:
            strategy = self._complex_cleanup_strategy

        spammers = await strategy(ctx, search)
        deleted = sum(spammers.values())
        messages = [f"""Deleted __**{deleted}**__ of the bot's{" message" if deleted == 1 else " messages"}"""]
        if deleted:
            messages.append('')
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f'- **{author}**: {count}' for author, count in spammers)

        e = discord.Embed(color=discord.Color.green())
        e.add_field(name=f"Cleanup <:yes:473312268998803466>", value="\n".join(messages))
        await ctx.send(embed=e, delete_after=10)

    @commands.command(aliases=['logout', 'restart', 'shutdown', 'kys', 'suicide'], hidden=True)
    @commands.is_owner()
    async def die(self, ctx):
        """Kills the bot"""
        await ctx.send("wow lowkey rude but fine")
        await self.bot.logout()


def setup(bot):
    bot.add_cog(Admin(bot))