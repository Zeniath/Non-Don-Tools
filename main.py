from discord.ext import commands
import discord
import asyncpg
import asyncio
import datetime
from datetime import datetime
from discord.ext.commands.cooldowns import BucketType

TOKEN = ''

extensions = ['modules.music',
              'modules.admin',
              'modules.api',
              'modules.information',
              'modules.fun',
              'modules.moderation',
              'modules.server',
              'modules.economy',
              'modules.help',
              'modules.modules']

class NonBot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix=self.get_pref, case_insensitive=True)
        self.launch_time = datetime.utcnow()
        self.embed = discord.Embed(color=discord.Color.purple())

    async def get_pref(self, bot, ctx):
        data = await self.db.fetchrow("SELECT prefix FROM prefixes WHERE guildid=$1;", ctx.guild.id)
        if not data:
            return ['non ', 'Non ', 'don ', 'Don ', '<@!448038812048949253> ', '<@448038812048949253> ']
        return data['prefix']

    def run(self):
        self.remove_command("help")
        self.load_extension("jishaku")
        for ext in extensions:
            try:
                self.load_extension(ext)
                print(f"Loaded extension {ext}")
            except Exception as e:
                print(f"Failed to load extensions {ext}")
                print(f"{type(e).__name__}: {e}")
        super().run(TOKEN)

    async def loop_game(self):
        await self.wait_until_ready()
        next_game = 0
        while True:
            games = [f'non help | {len(self.users)} members', f'non help | {len(self.guilds)} servers']
            if next_game + 1 == len(games):
                next_game = 0
            else:
                next_game += 1
            await self.change_presence(activity = discord.Activity(name = games[next_game], type = 3))
            await asyncio.sleep(60)

    async def on_ready(self):
        print("Bot loaded")
        print(f"Logged in as: {self.user}")
        print(f"Total Servers: {len(self.guilds)}")
        print(f"Total Cogs: {len(self.cogs)}")
        print(f"Total Commands: {len(self.commands)}")
        print("-"*35)
        creds = {"user": "zeniath", "password": "hypixel", "database": "nonbot", "host": "127.0.0.1"}
        self.db = await asyncpg.create_pool(**creds)
        self.blacklist = [u['userid'] for u in await self.db.fetch("SELECT * FROM blacklist;")]
        self.loop.create_task(self.loop_game())

    async def on_command_completion(self, ctx):
        await self.db.execute("UPDATE commands SET commandcount = commandcount + 1;")

    async def on_message(self, message):
        if message.author.bot:
            return 
        if message.author.id in self.blacklist:
            return
        if message.content == "non" or message.content == "🇳 🇴 🇳":
            await message.channel.send(f"no u")
            return
        await self.process_commands(message)


if __name__ == "__main__":
    NonBot().run()