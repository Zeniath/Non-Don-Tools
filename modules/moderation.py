from discord.ext import commands
import json, aiohttp, asyncio, traceback, discord, inspect, io, textwrap, datetime
from platform import python_version
from contextlib import redirect_stdout
from datetime import datetime
from collections import Counter
from utils import checks

MUTED_ROLE = 448054088232337408
GUILD_ID = 302689712617816064

class MemberID(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            m = await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                return int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f"{argument} is not a valid member or member ID.") from None
        else:
            can_execute = ctx.author.id == ctx.bot.owner_id or \
                          ctx.author == ctx.guild.owner or \
                          ctx.author.top_role > m.top_role

            if not can_execute:
                raise commands.BadArgument('You cannot do this action on this user due to role hierarchy.')
            return m.id

class BannedMember(commands.Converter):
    async def convert(self, ctx, argument):
        ban_list = await ctx.guild.bans()
        try:
            member_id = int(argument, base=10)
            entity = discord.utils.find(lambda u: u.user.id == member_id, ban_list)
        except ValueError:
            entity = discord.utils.find(lambda u: str(u.user) == argument, ban_list)

        if entity is None:
            raise commands.BadArgument("Not a valid previously-banned member.")
        return entity

class ActionReason(commands.Converter):
    async def convert(self, ctx, argument):
        ret = f'{ctx.author} (ID: {ctx.author.id}): {argument}'

        if len(ret) > 512:
            reason_max = 512 - len(ret) - len(argument)
            raise commands.BadArgument(f'reason is too long ({len(argument)}/{reason_max})')
        return ret

class Moderation:
    """Moderator Commands"""

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.MissingPermissions):
            try:
                e = discord.Embed(title="Error <:no:473312284148498442>", description=str(error), color=16720640)
                return await ctx.send(embed=e)
            except discord.HTTPException:
                pass

    @commands.command()
    @checks.has_permissions(manage_guild=True)
    async def blacklist(self, ctx, user: discord.User, *, reason = None):
        """Blacklist a user from using the bot's commands"""
        data = await self.bot.db.fetch("SELECT * FROM blacklist")
        await self.bot.db.execute("INSERT INTO blacklist VALUES ($1)", user.id)

        if reason is None:
            e = discord.Embed(color=discord.Color.green())
            e.add_field(name=f"Blacklisted <:yes:473312268998803466>", value=f'Blacklisted {user.mention} from using any commands')
            await ctx.send(embed=e)
        else:
            e = discord.Embed(color=discord.Color.green())
            e.add_field(name=f"Blacklisted <:yes:473312268998803466>", value=f'Blacklisted {user.mention} from using any commands for: {reason}')
            await ctx.send(embed=e)  


    @commands.command()
    async def list(self, ctx):
        """Shows the list of blacklisted members"""
        data = await self.bot.db.fetch("SELECT * FROM blacklist")
        fmt = [f"**- {self.bot.get_user(data[_]['userid'])}**\n" for _ in range(len(data))]

        e = discord.Embed(color=discord.Color.purple())
        e.add_field(name=f"Blacklisted Members ({len(data)})", value=f''.join(fmt))
        await ctx.send(embed=e)

    @list.error
    async def list_error(self, ctx, error):
        import traceback; traceback.print_exception(type(error), error, error.__traceback__)

    @commands.command()
    @commands.guild_only()
    @checks.has_permissions(ban_members=True)
    async def ban(self, ctx, member: MemberID, *, reason: ActionReason = None):
        """Bans a member"""

        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        await ctx.guild.ban(discord.Object(id=member), reason=reason)
        await ctx.send(f'**<@{member}>** has been bannned from **{ctx.guild.name}**')

    @commands.command()
    @commands.guild_only()
    @checks.has_permissions(kick_members=True)
    async def kick(self, ctx, member: MemberID, *, reason: ActionReason = None):
        """Bans a member"""

        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        await ctx.guild.kick(discord.Object(id=member), reason=reason)
        await ctx.send(f'**<@{member}>** has been kicked from **{ctx.guild.name}** for **{reason}**')

    @commands.command()
    @commands.guild_only()
    @checks.has_permissions(ban_members=True)
    async def unban(self, ctx, member: BannedMember, *, reason: ActionReason = None):
        """Unbans a member"""

        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        await ctx.guild.unban(member.user, reason=reason)
        if member.reason:
            await ctx.send(f'Unbanned {member.user} (ID: {member.user.id}), previously banned for {member.reason}.')
        else:
            await ctx.send(f'Unbanned {member.user} (ID: {member.user.id}).')

    @commands.command()
    @commands.guild_only()
    @commands.check(lambda ctx: ctx.guild and ctx.guild.id == GUILD_ID)
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, user: discord.Member, *, reason = None):
        """Mutes a member"""
        if reason is None:
            if any(r.id == MUTED_ROLE for r in ctx.author.roles):
                return await ctx.message.add_reaction('\N{WARNING SIGN}')
            try:
                await user.add_roles(discord.Object(id=MUTED_ROLE))
            except:
                await ctx.message.add_reaction('\N{NO ENTRY SIGN}')
            else:
                return await ctx.send(f"Muted <@{user.id}>")
        else:
            if any(r.id == MUTED_ROLE for r in ctx.author.roles):
                return await ctx.message.add_reaction('\N{WARNING SIGN}')
            try:
                await user.add_roles(discord.Object(id=MUTED_ROLE))
            except:
                await ctx.message.add_reaction('\N{NO ENTRY SIGN}')
            else:
                return await ctx.send(f"Muted <@{user.id}> for **{reason}**")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, user: discord.Member):
        """Mutes a member"""
        try:
            await user.remove_roles(discord.Object(id=MUTED_ROLE))
        except:
            await ctx.message.add_reaction('\N{NO ENTRY SIGN}')
        else:
            await ctx.send(f"Unmuted <@{user.id}>")

def setup(bot):
    bot.add_cog(Moderation(bot))