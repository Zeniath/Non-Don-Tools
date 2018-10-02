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

    @commands.group(invoke_without_command=True)
    async def blacklist(self, ctx):
        """Shows the blacklisted members"""
        data = await self.bot.db.fetch("SELECT * FROM blacklist")
        fmt = [f"**- {self.bot.get_user(data[_]['userid'])}**\n" for _ in range(len(data))]

        if len(data) == 0:
            e = discord.Embed(color=16720640)
            e.add_field(name=f"Blacklisted Members ({len(data)})", value=f'No one is currently blacklisted!')
            await ctx.send(embed=e)
        else:
            e = discord.Embed(color=discord.Color.purple())
            e.add_field(name=f"Blacklisted Members ({len(data)})", value=f''.join(fmt))
            await ctx.send(embed=e)

    @blacklist.command()
    @checks.has_permissions(manage_guild=True)
    async def add(self, ctx, user: discord.Member, *, reason = None):
        """Blacklist a user from using the bot's commands"""

        data = await self.bot.db.fetch("SELECT * FROM blacklist WHERE userid=$1 AND guildid=$2;", user.id, ctx.guild.id)
        if data:
            e = discord.Embed(color=16720640)
            e.add_field(name=f"Error <:no:473312284148498442>", value=f"{user.mention} is already blacklisted!")
            return await ctx.send(embed=e)
            
        await self.bot.db.execute("INSERT INTO blacklist VALUES ($1, $2)", user.id, ctx.guild.id)
        self.bot.blacklist.append(user.id)

        if reason is None:
            e = discord.Embed(color=discord.Color.green())
            e.add_field(name=f"Blacklist Add <:yes:473312268998803466>", value=f'Blacklisted {user.mention} from using the bots commands')
            await ctx.send(embed=e)
        else:
            e = discord.Embed(color=discord.Color.green())
            e.add_field(name=f"Blacklist Add <:yes:473312268998803466>", value=f'Blacklisted {user.mention} from using the bots commands for: {reason}')
            await ctx.send(embed=e) 

    @blacklist.command(aliases=['un'])
    @checks.has_permissions(manage_guild=True)
    async def remove(self, ctx, *, user: discord.Member):
        """Remove a blacklisted user"""

        data = await self.bot.db.fetch("SELECT * FROM blacklist WHERE userid=$1 AND guildid=$2;", user.id, ctx.guild.id)
        if not data:
            e = discord.Embed(color=16720640)
            e.add_field(name=f"Error <:no:473312284148498442>", value=f"{user.mention} is not blacklisted!")
            return await ctx.send(embed=e)

        await self.bot.db.execute("DELETE FROM blacklist WHERE userid=$1 AND guildid=$2", user.id, ctx.guild.id)
        self.bot.blacklist.remove(user.id)

        e = discord.Embed(color=discord.Color.green())
        e.add_field(name=f"Blacklist Removed <:yes:473312268998803466>", value=f"Removed {user.mention} from the blacklisted list. They can now use commands again")
        await ctx.send(embed=e)

    @commands.group(aliases=['nick'], invoke_without_command=True)
    @commands.has_permissions(manage_nicknames=True)
    async def nickname(self, ctx):
        """This is a subcommand for all commands following nick

        You must have Manage Nicknames permissions to use this command"""

        pass

    @nickname.command()
    @commands.has_permissions(manage_nicknames=True)
    async def set(self, ctx, member: discord.Member, *, nick):
        """Change the nickname of a member

        Must have Manage Nicknames permission to use the command"""

        await member.edit(nick=nick)
        e = discord.Embed(color=discord.Color.orange())
        e.add_field(name="Nick Changed <:yes:473312268998803466>", value=f"**{member}**'s nickname has been changed to **{nick}**!")
        await ctx.send(embed=e)

    @nickname.command()
    @commands.has_permissions(manage_nicknames=True)
    async def reset(self, ctx, *, member: discord.Member):
        """Reset the nickname of a member

        Must have Manage Nicknames permission to use the command"""

        await member.edit(nick=None)
        e = discord.Embed(color=discord.Color.orange())
        e.add_field(name="Nick Reset <:yes:473312268998803466>", value=f"**{member}**'s nickname has been reset!")
        await ctx.send(embed=e)

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds="15"):
        """Activate slowmode in a channel for 'x' number of seconds

        Default seconds are 15

        You must have Manage Channels permissions to use this command"""

        await ctx.channel.edit(slowmode_delay=seconds)
        e = discord.Embed(color=discord.Color.blue())
        e.add_field(name="Slowmode <:yes:473312268998803466>", value=f"Slowmode has now been activated for **{seconds}** seconds in channel <#{ctx.channel.id}>")
        await ctx.send(embed=e)

    @slowmode.group(aliases=['off', 'o', 'none', '0'])
    @commands.has_permissions(manage_channels=True)
    async def reset(self, ctx):
        """Turn off slowmode in a channel

        You must have Manage Channels permissions to use this command"""

        await ctx.channel.edit(slowmode_delay=None)
        e = discord.Embed(color=discord.Color.blue())
        e.add_field(name="Slowmode Reset <:yes:473312268998803466>", value=f"Slowmode has been turned off in channel <#{ctx.channel.id}>")
        await ctx.send(embed=e)

    @commands.command()
    @commands.guild_only()
    @checks.has_permissions(ban_members=True)
    async def ban(self, ctx, member: MemberID, *, reason: ActionReason = None):
        """Bans a member from the server

        You must specify the users' ID, @tag, or Username

        It is optional to use a reason for the ban"""
        
        channel = self.bot.get_channel(448342563980705794)

        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        await ctx.guild.ban(discord.Object(id=member), reason=reason)
        await channel.send(f'**<@{member}>** has been bannned from **{ctx.guild.name}** for **{reason}**')


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
            if None(r.id == MUTED_ROLE for r in ctx.author.roles):
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
        return await ctx.send(f"Unmuted <@{user.id}>")

def setup(bot):
    bot.add_cog(Moderation(bot))