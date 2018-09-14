import discord
from discord.ext import commands
import asyncio, sys, traceback, datetime
from async_timeout import timeout
from functools import partial
import itertools
from youtube_dl import YoutubeDL
from discord.ext.commands.cooldowns import BucketType

ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ffmpegopts = {
    'before_options': '-nostdin -preset ultrafast',
    'options': '-vn -threads 1'
}

ytdl = YoutubeDL(ytdlopts)


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""


class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')

        if self.title is None:
            self.title = "No title available"

        self.web_url = data.get('webpage_url')
        self.thumbnail = data.get('thumbnail')

        if self.thumbnail is None:
            self.thumbnail = "http://ppc.tools/wp-content/themes/ppctools/img/no-thumbnail.jpg"

        self.duration = data.get('duration')

        if self.duration is None:
            self.duration = 0

        self.uploader = data.get('uploader')

        if self.uploader is None:
            self.uploader = "Unknown uploader"
        
        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.

        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        e = discord.Embed(title="Added <:yes:473312268998803466>", description=f""":notes: Added to queue: **{data["title"]}**""", color=discord.Color.green())
        await ctx.send(embed=e, delete_after=3)

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.

        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)


class MusicPlayer:
    """A class which is assigned to each guild using the bot for Music.

    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.

    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = ('bot', '_guild', '_ctxs', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume', 'buttons', 'requester', 'music', 'music_controller', 'restmode')

    def __init__(self, ctx):

        self.buttons = {'⏯': 'rp',
                        '⏭': 'skip',
                        '➕': 'vol_up',
                        '➖': 'vol_down',
                        '🖼': 'thumbnail',
                        '🎶': 'lyrics',
                        '⏹': 'stop',
                        'ℹ': 'queue',
                        '❔': 'tutorial'}

        self.bot = ctx.bot
        self._guild = ctx.guild
        self._ctxs = ctx
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None
        self.volume = .5
        self.current = None
        self.music_controller = None

        ctx.bot.loop.create_task(self.player_loop())

    async def buttons_controller(self, guild, current, source, channel, context):
        vc = guild.voice_client
        vctwo = context.voice_client

        for react in self.buttons:
            await current.add_reaction(str(react))

        def check(r, u):
            if not current:
                return False
            elif str(r) not in self.buttons.keys():
                return False
            elif u.id == self.bot.user.id or r.message.id != current.id:
                return False
            elif u not in vc.channel.members:
                return False
            return True

        while current:
            if vc is None:
                return False

            react, user = await self.bot.wait_for('reaction_add', check=check)
            control = self.buttons.get(str(react))

            if control == 'rp':
                if vc.is_paused():
                    vc.resume()
                else:
                    vc.pause()

            if control == 'skip':
                e = discord.Embed(title="Skipped <:yes:473312268998803466>", description=f":notes: **`{context.author}`** has **skipped** the current song!", color=discord.Color.green())
                vc.stop()

            if control == 'stop':
                em = discord.Embed(title="Stopped <:yes:473312268998803466>", description=f":notes: **`{context.author}`** has **stopped** the bot from playing anymore songs!", color=discord.Color.green())
                await context.send(embed=em)
                await self._cog.cleanup(guild)
                try:
                    self.music_controller.cancel()
                except:
                    pass

            if control == 'vol_up':
                player = self._cog.get_player(context)
                if vctwo.source:
                    if not vctwo.source.volume > 100 or player.volume > 100:
                        vctwo.source.volume += 5
                        player.volume += 5
                        
            if control == 'vol_down':
                player = self._cog.get_player(context)
                if vctwo.source:
                    if not vctwo.source.volume < 10 or player.volume < 10:
                        vctwo.source.volume -= 5
                        player.volume -= 5

            if control == 'thumbnail':
                await channel.send(embed=discord.Embed(title="Song thumbnail:", color=discord.Colour.blurple()).set_image(url=source.thumbnail).set_footer(text=f"Requested by {source.requester} | Video: {source.title}", icon_url=source.requester.avatar_url), delete_after=10)

            if control == 'tutorial':
                await channel.send(embed=discord.Embed(color=discord.Colour.blurple()).add_field(name="How to use Music Controller?", value="⏯ - Resume or pause player\n⏭ - Skip song\n➕ - Volume up\n➖ - Volume down\n🎶 - Gets the song lyrics\n🖼 - Get song thumbnail\n⏹ - Stop music session\nℹ - Song queue\n❔ - Shows you how to use Music Controller"), delete_after=10)
            
            if control == 'queue': 
                player = self.get_player(ctx)
                if player.queue.empty():
                    e = discord.Embed(title="Error <:no:473312284148498442>", description=":notes: There are currently **no** more queued songs.", color=16720640)
                    return await ctx.send(embed=e, delete_after=10)

                upcoming = list(itertools.islice(player.queue._queue, 0, 5))
        
                fmt = [f'{a+1}. `{_["title"]}`' for _ in upcoming for a in range(len(upcoming))]
                embed = discord.Embed(title=f'Upcoming Songs - {len(upcoming)}', description=''.join(fmt), color=discord.Colour.blurple())
                await ctx.send(embed=embed)

            if control == 'lyrics':
                await self._cog.search_lyrics(context, source.uploader, source.title)

            try:
                await current.remove_reaction(react, user)
            except discord.HTTPException:
                pass

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                if self in self._cog.players.values():
                    return self.destroy(self._guild)
                return

            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f':notes: There was an error processing your song.\n'
                                             f'```css\n[{e}]\n```')
                    continue

            source.volume = self.volume
            self.current = source
            try:
                self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            except Exception:
                continue

            embednps = discord.Embed(color=discord.Colour.dark_blue())
            embednps.add_field(name=":notepad_spiral: Song title:", value=f"```fix\n{source.title}```", inline=False)
            embednps.add_field(name=":trumpet: Requested by:", value=f"**{source.requester}**", inline=True)
            embednps.add_field(name=":link: Song URL:", value=f"**[URL]({source.web_url})**", inline=True)
            embednps.add_field(name=":spy: Uploader:", value=f"**{source.uploader}**", inline=True)
            embednps.add_field(name=":notes: Song duration:", value=f"**{datetime.timedelta(seconds=source.duration)}**", inline=True)
            embednps.add_field(name=":loudspeaker: Volume:", value=f'**{int(self.volume * 100)}%**', inline=True)
            embednps.set_thumbnail(url=f"{source.thumbnail}")
            self.np = await self._channel.send(embed=embednps)

            self.music_controller = self.bot.loop.create_task(self.buttons_controller(self._guild, self.np, source, self._channel, self._ctxs))
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None

            try:
                # We are no longer playing this song...
                await self.np.delete()
                self.music_controller.cancel()
            except Exception:
                pass

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))

class Music:
    """Music Commands"""

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                e = discord.Embed(title="Error <:no:473312284148498442>", description=":notes: This command **cannot** be used in **Private Messages**", color=16720640)
                return await ctx.send(embed=e, delete_after=10)
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            embed = discord.Embed(title="Error <:no:473312284148498442>", description=":notes: **Invalid voice channel**\n\n:notes: Please join a **voice channel** or specifically provide me with one", color=16720640)
            await ctx.send(embed=embed, delete_after=10)

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.command(name='thumbnail', aliases=["tn"])
    async def thumbnail_(self, ctx):
        """Shows the thumbnail of the current song"""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            e = discord.Embed(title="Error <:no:473312284148498442>", description=":notes: I am **not** currently playing anything!", colour=16720640)
            return await ctx.send(embed=e, delete_after=10)

        elif ctx.author not in ctx.guild.voice_client.channel.members:
            e = discord.Embed(title="Error <:no:473312284148498442>", description=":notes: Please join my **voice channel** to execute this command", color=16720640)
            return await ctx.send(embed=e, delete_after=10)

        elif ctx.author in ctx.guild.voice_client.channel.members:
            return await ctx.send(embed=discord.Embed(title="Song thumbnail:", color=discord.Colour.dark_blue()).set_image(url=vc.source.thumbnail).set_footer(text=f"Requested by {vc.source.requester} | Video: {vc.source.title}", icon_url=vc.source.requester.avatar_url), delete_after=10)
        
    @commands.command(name='disconnect', aliases=['dc', 'leave'])
    async def disconnect_(self, ctx):
        """Disconnects from the current voice channel"""

        vc = ctx.voice_client

        if vc:
            try:
                await vc.disconnect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Disconnecting from channel: **{vc.channel}** timed out.')

        embed = discord.Embed(title="Disconnected <:yes:473312268998803466>", description=f":notes: Disconnected from channel: **{vc.channel}**", color=discord.Color.green())
        await ctx.send(embed=embed, delete_after=10)

    @commands.command(name='connect', aliases=['join'])
    async def connect_(self, ctx, *, channel: discord.VoiceChannel=None):
        """Connects to a voice channel"""

        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                embed = discord.Embed(title="Error <:no:473312284148498442>", description=":notes: **Invalid voice channel**\n\nPlease join a **voice channel** or specifically provide me with one", color=16720640)
                await ctx.send(embed=embed, delete_after=10)

        vc = ctx.voice_client
        
        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Moving to channel: **{channel}** timed out.')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Connecting to channel: **{channel}** timed out.')

        embed = discord.Embed(title="Connected <:yes:473312268998803466>", description=f":notes: Connected into voice channel: **{channel}**", color=discord.Color.green())
        await ctx.send(embed=embed, delete_after=3.5)

    @commands.command(name="100degrees", aliases=['💯', '100o', '100', '100_degrees'], hidden=True)
    async def degrees100(self, ctx):
        """Some weather guy saying '100 degrees'"""

        await ctx.trigger_typing()

        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(self.connect_)

        elif ctx.author not in ctx.guild.voice_client.channel.members:
            e = discord.Embed(title="Error <:no:473312284148498442>", description=":notes: Please join my **voice channel** to execute this command", color=16720640)
            return await ctx.send(embed=e, delete_after=10)            

    @commands.command(name='pause')
    async def pause_(self, ctx):
        """Pauses the current song"""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            e = discord.Embed(title="Error <:no:473312284148498442>", description=":notes: I am **not** currently playing anything!", colour=16720640)
            return await ctx.send(embed=e, delete_after=10)
        elif vc.is_paused():
            return

        vc.pause()
        e = discord.Embed(title="Paused <:yes:473312268998803466>", description=f":notes: **`{ctx.author}`** has **paused** the current song!", color=discord.Colour.green())
        await ctx.send(embed=e)

    @commands.command(name='resume', aliases=['res'])
    async def resume_(self, ctx):
        """Resumes the current song"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            e = discord.Embed(title="Error <:no:473312284148498442>", description=":notes: I am **not** currently playing anything!", colour=16720640)
            return await ctx.send(embed=e, delete_after=10)
        elif not vc.is_paused():
            return

        vc.resume()
        e = discord.Embed(title="Resumed <:yes:473312268998803466>", description=f":notes: **`{ctx.author}`** has **resumed** the current song!", color=discord.Color.green())
        await ctx.send(embed=e)
        
    @commands.command(name='play', aliases=['sing', 'p'])
    async def play_(self, ctx, *, song: str):
        """Plays a song"""
        await ctx.trigger_typing()

        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(self.connect_)

        elif ctx.author not in ctx.guild.voice_client.channel.members:
            e = discord.Embed(title="Error <:no:473312284148498442>", description=":notes: Please join my **voice channel** to execute this command", color=16720640)
            return await ctx.send(embed=e, delete_after=10)

        await ctx.trigger_typing()

        player = self.get_player(ctx)

        source = await YTDLSource.create_source(ctx, song, loop=self.bot.loop, download=False)
        await player.queue.put(source)

    @commands.command(name='stop')
    async def stop_(self, ctx):
        """Stop the bot from playing any more songs"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            e = discord.Embed(colour=16720640)
            e.add_field(name="Error <:no:473312284148498442>", value=":notes: I am **not** currently playing anything!")
            return await ctx.send(embed=e, delete_after=10)
        else:
            e = discord.Embed(color=discord.Color.green())
            e.add_field(name="Stopped <:yes:473312268998803466>", value=f"Stopped bot from playing any more songs, and disconnected from **{vc.channel}**")
            await ctx.send(embed=e)

        await self.cleanup(ctx.guild)

    @commands.command(name='skip', aliases=['s'])
    async def skip_(self, ctx):
        """Skips the current song"""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            e = discord.Embed(colour=16720640)
            e.add_field(name="Error <:no:473312284148498442>", value=":notes: I am **not** currently playing anything!")
            return await ctx.send(embed=e, delete_after=10)
        elif vc.source.requester != ctx.author:
            e = discord.Embed(colour=16720640)
            e.add_field(name="Error <:no:473312284148498442>", value=":notes: You can only skip songs that you have requested!")
            return await ctx.send(embed=e, delete_after=10)

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()
        e = discord.Embed(title="Skipped <:yes:473312268998803466>", description=f":notes: **`{ctx.author}`** has **skipped** the current song!", color=discord.Color.green())
        await ctx.send(embed=e)

    @commands.command(name='volume', aliases=['vol'])
    async def change_volume(self, ctx, *, vol: float):
        """Change the player volume"""

        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            e = discord.Embed(title=f"Error <:no:473312284148498442>", description=":notes: I am **not** currently connected to voice", color=16720640)
            return await ctx.send(embed=e, delete_after=10)

        if not 0 < vol < 101:
            e = discord.Embed(title=f"Error <:no:473312284148498442>", description=":notes: Please enter a value between **1** and **100**", color=16720640)
            return await ctx.send(embed=e, delete_after=10)

        if ctx.author not in ctx.guild.voice_client.channel.members:
            e = discord.Embed(title=f"Error <:no:473312284148498442>", description=":notes: Please join my voice channel to execute this command", color=16720640)
            return await ctx.send(embed=e, delete_after=10)

        player = self.get_player(ctx)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        e = discord.Embed(title=f"Volume <:yes:473312268998803466>", description=f":notes: **`{ctx.author}`** set the volume to **{vol}%**", color=discord.Color.green())
        return await ctx.send(embed=e, delete_after=10)
        await ctx.send(f'**`{ctx.author}`**: Set the volume to **{vol}%**')

    @commands.command(name='now_playing', aliases=['np', 'current', 'currentsong', 'playing'])
    async def now_playing_(self, ctx):
        """Shows the current song"""

        vc = ctx.voice_client
        player = self.get_player(ctx)
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        if not vc or not vc.is_connected():
            e = discord.Embed(title="Error <:no:473312284148498442>", description=":notes: I am **not** connected to voice.", color=16720640)
            return await ctx.send(embed=e, delete_after=10)

        elif ctx.author not in ctx.guild.voice_client.channel.members:
            e = discord.Embed(title="Error <:no:473312284148498442>", description=":notes: Please join my **voice channel** to execute this command.", color=16720640)
            return await ctx.send(embed=e, delete_after=10)

        if not vc or not vc.is_playing():
            e = discord.Embed(title="Error <:no:473312284148498442>", description=":notes: I am **not** currently playing any songs.", color=16720640)
            return await ctx.send(embed=e, delete_after=10)

        embednp = discord.Embed(color=discord.Colour.dark_blue())
        embednp.add_field(name=":notepad_spiral: Song title:", value=f"```fix\n{vc.source.title}```", inline=False)
        embednp.add_field(name=":trumpet: Requested by:", value=f"**{vc.source.requester}**", inline=True)
        embednp.add_field(name=":link: Song URL:", value=f"**[URL]({vc.source.web_url})**", inline=True)
        embednp.add_field(name=":spy: Uploader:", value=f"**{vc.source.uploader}**", inline=True)
        embednp.add_field(name=":notes: Song duration:", value=f"**{datetime.timedelta(seconds=vc.source.duration)}**", inline=True)
        embednp.add_field(name=":bell: Songs queued:", value=f"**{len(upcoming)}**")
        embednp.set_thumbnail(url=f"{vc.source.thumbnail}")
        player.np = await ctx.send(embed=embednp)
        self.music_controller = self.bot.loop.create_task(MusicPlayer(ctx).buttons_controller(ctx.guild, player.np, vc.source, ctx.channel, ctx))

    @commands.command(name="queue", aliases=["q", "que"])
    async def queue_info(self, ctx):
        """Shows the current queued songs"""
        vc = ctx.voice_client

        player = self.get_player(ctx)
        if player.queue.empty():
            e = discord.Embed(title="Error <:no:473312284148498442>", description=":notes: There are not any more songs queued", color=16720640)
            return await ctx.send(embed=e, delete_after=10)

        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        fmt = [f'{_+1}. `{upcoming[_]["title"]}` - Requested by **{vc.source.requester}**' for _ in range(len(upcoming))]
        embed = discord.Embed(color=discord.Colour.dark_blue())
        embed.add_field(name=f"Upcoming Songs: {len(upcoming)}", value='\n'.join(fmt))
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Music(bot))