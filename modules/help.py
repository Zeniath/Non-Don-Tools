import discord
from discord.ext import commands
from utils.HelpPaginator import HelpPaginator, CannotPaginate
from datetime import datetime
import datetime
import inspect, os

class Help:
    """Helpful Commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, *, command: str = None):
        """Shows help about a command or the bot"""
        try:
            if command is None:
                p = await HelpPaginator.from_bot(ctx)
            else:
                entity = self.bot.get_cog(command) or self.bot.get_command(command)

                if entity is None:
                    clean = command.replace('@', '@\u200b')
                    return await ctx.send(f'Command or category "{clean}" not found.')
                elif isinstance(entity, commands.Command):
                    p = await HelpPaginator.from_command(ctx, entity)
                else:
                    p = await HelpPaginator.from_cog(ctx, entity)

            await p.paginate()
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, number: int, target: discord.User = None):
        """Purges any amount of messages

        If a user is provided, it will clear only their messages

        If no user is provided, it will clear all of the messages

        You must have Manage Messages permissions to use this command"""

        if number <= 0:
            em = discord.Embed(color=16720640)
            em.add_field(name="Error <:no:473312284148498442>", value=f"You must purge at least 1 message!")
            return await ctx.send(embed=em)

        if target is None:
            check = None
        else:
            check = lambda m: m.author == target

        deleted = await ctx.message.channel.purge(limit=number, check=check)

        messages = [f'Deleted __**{len(deleted)}**__ {" message!" if len(deleted) == 1 else " messages!"}']
        
        embed = discord.Embed(title='Purged <:yes:473312268998803466>', description='\n'.join(messages), color=9305953)
        embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed, delete_after=5)

    @commands.command(aliases=['sauce', 'sawce'])
    async def source(self, ctx, command: str = None):
        """Get the bot's source link for a command or the whole source"""

        source_url = "https://github.com/Zeniath/Non-Don-Tools"
        if command is None:
            return await ctx.send(source_url)
        

        obj = self.bot.get_command(command.replace('.', ' '))
        if obj is None:
            return await ctx.send('Could not find command.')

        src = obj.callback.__code__
        lines, firstlineno = inspect.getsourcelines(src)
        if not obj.callback.__module__.startswith('discord'):
            location = os.path.relpath(src.co_filename).replace('\\', '/')
        else:
            location = obj.callback.__module__.replace('.', '/') + '.py'
            source_url = "https://github.com/Zeniath/Non-Don-Tools"

        await ctx.send(f"<{source_url}/tree/master/{location}/#L{firstlineno}-L{firstlineno + len(lines) - 1}>")

    @commands.command(aliases=['feedback', 'fb', 'bug', 'suggest'])
    async def report(self, ctx, *, suggestion: str = None):
        """Report a bug or give feedback/suggestions"""

        channel = self.bot.get_channel(485679174309249046)

        if suggestion is None:
            msg = await ctx.send('What would you like to report/feedback on?')

            def check(message):
                return message.author.id == ctx.author.id

            try:
                report = await self.bot.wait_for('message', check=check, timeout=180)
            except asyncio.TimeoutError:
                return await msg.delete()

            embed = discord.Embed(title=f'Bug Report/Feedback', colour=discord.Color.dark_blue(),
                                description=f'```css\n{report.content}\n```')
            embed.add_field(name='User', value=f'**{ctx.author}** ({ctx.author.id})')
            embed.add_field(name='Guild', value=f'**{ctx.guild.name}** ({ctx.guild.id})')
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.set_footer(text='Received ').timestamp = datetime.datetime.utcnow()
            embed.set_thumbnail(url=ctx.author.avatar_url)
            await channel.send(embed=embed)
            await ctx.send("Thanks for the feedback or report!")

        else:
            embed = discord.Embed(title=f'Bug Report/Feedback', colour=discord.Color.dark_blue(),
                                  description=f'```css\n{suggestion}\n```')
            embed.add_field(name='User', value=f'**{ctx.author}** ({ctx.author.id})')
            embed.add_field(name='Guild', value=f'**{ctx.guild.name}** ({ctx.guild.id})')
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.set_footer(text='Received ').timestamp = datetime.datetime.utcnow()
            embed.set_thumbnail(url=ctx.author.avatar_url)
            await channel.send(embed=embed)
            await ctx.send("Thanks for the feedback or report!")

def setup(bot):
    bot.add_cog(Help(bot))