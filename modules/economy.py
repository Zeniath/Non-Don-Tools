from discord.ext import commands
import discord
import asyncpg
import random
import requests
from .utils import checks
from random import randint
from discord.ext.commands.cooldowns import BucketType

class Economy:
    """Economic Commands"""

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
        elif isinstance(error, commands.CommandInvokeError):
            try:
                e = discord.Embed(color=16720640)
                e.add_field(name="Error <:no:473312284148498442>", value=str(error))
                await ctx.send(embed=e)
            except discord.HTTPException:
                pass
        elif isinstance(error, commands.MissingRequiredArgument):
            try:
                e = discord.Embed(color=16720640)
                e.add_field(name="Error <:no:473312284148498442>", value=str(error))
                await ctx.send(embed=e)
            except discord.HTTPException:
                pass
        elif isinstance(error, commands.CheckFailure):
            try:
                e = discord.Embed(title="Error <:no:473312284148498442>", description=str(error), color=16720640)
                return await ctx.send(embed=e)
            except discord.HTTPException:
                pass


    @commands.command(aliases=['create'])
    async def register(self, ctx, *, name = None):
        """Register your account"""

        if name is None:
            name = ctx.author.name

        data = await self.bot.db.fetchrow("SELECT * FROM economy WHERE userid=$1;", ctx.author.id)
        if data:
            await ctx.send("You are already registered!")
            return
        await self.bot.db.execute("INSERT INTO economy VALUES (1000, $1);", ctx.author.id)
        await ctx.send(f"Successfully created your account! Your account name is **{name}**, and you will start out with **$1000**. Use `{ctx.prefix}help Economy` for information on commands")


    @commands.command(aliases=['w', '$', 'credits', 'bal', 'wallet', 'coins', 'cred', 'money'])
    async def balance(self, ctx, user: discord.User = None):
        """Shows a users' or your balance"""

        if user is None:
            user = ctx.author

        data = await self.bot.db.fetchrow(f"SELECT balance FROM economy WHERE userid={user.id}")
        if not data:
            await ctx.send(f"**{user.name}** does not have an account! Use the register command `{ctx.prefix}register` to create an account.")
            return

        money = data['balance']

        if user != ctx.author:
            embed = discord.Embed(color=0xF3B800)
            embed.add_field(name='Money Balance', value=f"**${money}**", inline=True)
            embed.set_author(name=f"{user.name}'s Wallet", icon_url=user.avatar_url)
            embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url="http://www.skillifynow.com/wp-content/uploads/2017/03/money3.jpg")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(color=0xF3B800)
            embed.add_field(name='Money Balance', value=f"**${money}**", inline=True)
            embed.set_author(name=f"{user.name}'s Wallet", icon_url=user.avatar_url)
            embed.set_thumbnail(url="http://www.skillifynow.com/wp-content/uploads/2017/03/money3.jpg")
            await ctx.send(embed=embed)

    @commands.command(name='50x2', aliases=['50'])
    async def fifty(self, ctx, amount: int):
        """Gamble your money by 1/100 for 2x your cash"""

        result = randint(1, 100)

        data = await self.bot.db.fetchrow(f"SELECT balance FROM economy WHERE userid={ctx.author.id}")
        if not data:
            await ctx.send(f"**{ctx.author.name}** does not have an account! Use the register command `{ctx.prefix}register` to create an account.")
            return
        money = data['balance']

        if amount > money:
            em = discord.Embed(color=16720640)
            em.add_field(name="Error <:no:473312284148498442>", value=f"You don't have enough money for that bet! You have **${money}**")
            await ctx.send(embed=em)
            return
        elif amount < 100:
            em = discord.Embed(color=16720640)
            em.add_field(name="Error <:no:473312284148498442>", value=f"The minimum amount of money you can bet is **$100**")
            await ctx.send(embed=em)
            return
        elif result < 50:
            await self.bot.db.execute(f"UPDATE economy SET balance=balance-{amount} WHERE userid={ctx.author.id};")
            emb = discord.Embed(color=16720640)
            emb.set_author(name=f"{ctx.author.name}'s Bet", icon_url=ctx.author.avatar_url)
            emb.add_field(name="50x2 Dicing", value=f"You have rolled a **{result}** out of **100**, and **did not** win your bet. You have lost **${amount}**")
            emb.set_thumbnail(url="http://www.skillifynow.com/wp-content/uploads/2017/03/money3.jpg")
            await ctx.send(embed=emb)
            return
        elif result > 50 and result < 99:
            await self.bot.db.execute(f"UPDATE economy SET balance=balance+{amount} WHERE userid={ctx.author.id};")
            e = discord.Embed(color=discord.Colour.green())
            e.set_author(name=f"{ctx.author.name}'s Bet", icon_url=ctx.author.avatar_url)
            e.add_field(name="50x2 Dicing", value=f"You have rolled a **{result}** out of **100**, and successfully **won** your bet! You have won **${amount*2}**!")
            e.set_thumbnail(url="http://www.skillifynow.com/wp-content/uploads/2017/03/money3.jpg")
            await ctx.send(embed=e)
            return
        elif result == 100:
            await self.bot.db.execute(f"UPDATE economy SET balance=balance+{amount*9} WHERE userid={ctx.author.id};")
            e = discord.Embed(color=discord.Colour.green())
            e.set_author(name=f"{ctx.author.name}'s Bet", icon_url=ctx.author.avatar_url)
            e.add_field(name="50x2 Dicing", value=f"You have rolled a **{result}** out of **100**, and successfully **won** your bet! You have won **${amount*10}**!")
            e.set_thumbnail(url="http://www.skillifynow.com/wp-content/uploads/2017/03/money3.jpg")
            await ctx.send(embed=e)
            return

    @commands.command(name='75x3', aliases=['75'])
    async def sevenfive(self, ctx, amount: int):
        """Gamble your money by 1/100 for 3x your cash"""

        result = randint(1, 100)

        data = await self.bot.db.fetchrow(f"SELECT balance FROM economy WHERE userid={ctx.author.id}")
        if not data:
            await ctx.send(f"**{ctx.author.name}** does not have an account! Use the register command `{ctx.prefix}register` to create an account.")
            return
        money = data['balance']

        if amount > money:
            em = discord.Embed(color=16720640)
            em.add_field(name="Error <:no:473312284148498442>", value=f"You don't have enough money for that bet! You have **${money}**")
            await ctx.send(embed=em)
            return
        elif amount < 100:
            em = discord.Embed(color=16720640)
            em.add_field(name="Error <:no:473312284148498442>", value=f"The minimum amount of money you can bet is **$100**")
            await ctx.send(embed=em)
            return
        elif result < 75:
            await self.bot.db.execute(f"UPDATE economy SET balance=balance-{amount} WHERE userid={ctx.author.id};")
            emb = discord.Embed(color=16720640)
            emb.set_author(name=f"{ctx.author.name}'s Bet", icon_url=ctx.author.avatar_url)
            emb.add_field(name="75x3 Dicing", value=f"You have rolled a **{result}** out of **100**, and **did not** win your bet. You have lost **${amount}**")
            emb.set_thumbnail(url="http://www.skillifynow.com/wp-content/uploads/2017/03/money3.jpg")
            await ctx.send(embed=emb)
            return
        elif result > 75 and result < 99:
            await self.bot.db.execute(f"UPDATE economy SET balance=balance+{amount*2} WHERE userid={ctx.author.id};")
            e = discord.Embed(color=discord.Colour.green())
            e.set_author(name=f"{ctx.author.name}'s Bet", icon_url=ctx.author.avatar_url)
            e.add_field(name="75x3 Dicing", value=f"You have rolled a **{result}** out of **100**, and successfully **won** your bet! You have won **${amount*3}!**")
            e.set_thumbnail(url="http://www.skillifynow.com/wp-content/uploads/2017/03/money3.jpg")
            await ctx.send(embed=e)
            return
        elif result == 100:
            await self.bot.db.execute(f"UPDATE economy SET balance=balance+{amount*9} WHERE userid={ctx.author.id};")
            e = discord.Embed(color=discord.Colour.green())
            e.set_author(name=f"{ctx.author.name}'s Bet", icon_url=ctx.author.avatar_url)
            e.add_field(name="75x3 Dicing", value=f"You have rolled a **{result}** out of **100**, and successfully **won** your bet! You have won **${amount*10}**!")
            e.set_thumbnail(url="http://www.skillifynow.com/wp-content/uploads/2017/03/money3.jpg")
            await ctx.send(embed=e)
            return

    @commands.command(aliases=['gamble'])
    async def bet(self, ctx):
        """Shows the betting commands"""
        await ctx.send(f"To bet, use `{ctx.prefix}50x2 <amount>` or `{ctx.prefix}75x3 <amount>`. More help can be found using `{ctx.prefix}help Economy`")

    @commands.command(aliases=['find'])
    @commands.cooldown(1, 20, BucketType.user)
    async def search(self, ctx):
        """Search for money"""

        amount = randint(1, 100)

        possible_responses = [
            f'You search the rubbish bin and find **${amount}**', 
            f'''You're searching in the back of your garden and notice a **${amount}** note laying around''', 
            f'While walking around the corner of your house, you pick up **${amount}**', 
            f'Whilst entering the nearest pub, you find **${amount}** on the ground',
            f'While trying to find out how to code, you find a dandy **${amount}**',
            f'While on the way to the store, you stumble across your friend who gives you **${amount}**',
            f'During your coding session, you notice there is **${amount}** sitting on your table',
            f'On the way to work, you buy your friend breakfast. In return, he hands you **${amount}**'
            ]

        search = random.choice(possible_responses)

        data = await self.bot.db.fetchrow(f"SELECT balance FROM economy WHERE userid={ctx.author.id}")
        if not data:
            self.bot.get_command("hourly").reset_cooldown(ctx)
            await ctx.send(f"**{ctx.author.name}** does not have an account! Use the register command `{ctx.prefix}register` to create an account.")
            return

        money = data['balance']

        await self.bot.db.execute(f"UPDATE economy SET balance = balance + $1 WHERE userid = {ctx.author.id};", amount)
        e = discord.Embed(color=discord.Color.green())
        e.add_field(name="Search <:yes:473312268998803466>", value=search)
        await ctx.send(embed=e)

    @search.error
    async def search_handler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            seconds = error.retry_after
            seconds = round(seconds, 2)
            hours, remainder = divmod(int(seconds), 3600)
            minutes, seconds = divmod(remainder, 60)
            await ctx.send(f"You are on cooldown! Please try again in **{seconds} seconds**")

    @commands.command(aliases=['give'])
    async def transfer(self, ctx, user: discord.User, amount: int):
        """Transfer an amount of money to someone"""

        data = await self.bot.db.fetchrow(f"SELECT balance FROM economy WHERE userid={ctx.author.id}")
        if not data:
            await ctx.send(f"**{user.name}** does not have an account! Use the register command `{ctx.prefix}register` to create an account.")
            return
        money = data['balance']
        await self.bot.db.execute(f"UPDATE economy SET balance = balance + $1 WHERE userid = {user.id};", amount)

        if amount > money:
            em = discord.Embed(color=16720640)
            em.add_field(name="Error <:no:473312284148498442>", value=f"You don't have enough money to transfer that to <@{user.id}>'s Wallet! You have **${amount}**")
            await ctx.send(embed=em)
            return
        elif amount < 100:
            em = discord.Embed(color=16720640)
            em.add_field(name="Error <:no:473312284148498442>", value=f"The minimum amount of money you can transfer is **$100**")
            await ctx.send(embed=em)
            return
        elif amount < money:
            await self.bot.db.execute(f"UPDATE economy SET balance = balance - $1 WHERE userid = {ctx.author.id};", amount)
            e = discord.Embed(color=discord.Colour.green())
            e.add_field(name="Transfered <:yes:473312268998803466>", value=f"You have transfered **${amount}** to <@{user.id}>'s Wallet! You now have **${money-amount}** in your wallet, and before had **${money}**")
            e.set_thumbnail(url="http://www.skillifynow.com/wp-content/uploads/2017/03/money3.jpg")
            await ctx.send(embed=e)

    @commands.command()
    @commands.cooldown(1, 60, BucketType.user)
    async def rob(self, ctx, user: discord.User, amount: int):
        """Rob a member for a chance to lose or gain money"""

        data = await self.bot.db.fetchrow(f"SELECT balance FROM economy WHERE userid={ctx.author.id}")
        if not data:
            self.bot.get_command("rob").reset_cooldown(ctx)
            await ctx.send(f"**{user.name}** does not have an account! Use the register command `{ctx.prefix}register` to create an account.")
            return
        money = data['balance']

        rob = randint(1, 100)

        usermoney = await self.bot.db.fetchrow(f"SELECT balance FROM economy WHERE userid={user.id}")
        user_money = usermoney['balance']

        if amount < 100:
            self.bot.get_command("rob").reset_cooldown(ctx)
            em = discord.Embed(color=16720640)
            em.add_field(name="Error <:no:473312284148498442>", value=f"The minimum amount of money you can rob is **$100**")
            await ctx.send(embed=em)
            return
        elif user_money < amount:
            self.bot.get_command("rob").reset_cooldown(ctx)
            e = discord.Embed(color=16720640)
            e.add_field(name="Error <:no:473312284148498442>", value=f"<@{user.id}> does not have enough money for you to rob them for **${amount}**. They only have **${user_money}**")
            await ctx.send(embed=e)
            return


        elif rob < 50:
            await self.bot.db.execute(f"UPDATE economy SET balance = balance - $1 WHERE userid = {ctx.author.id};", amount)
            await self.bot.db.execute(f"UPDATE economy SET balance = balance + $1 WHERE userid = {user.id};", amount)
            e = discord.Embed(color=16720640)
            e.set_author(name=f"{ctx.author.name}'s Rob", icon_url=ctx.author.avatar_url)
            e.add_field(name="Robbing", value=f"You have unsuccessfully robbed <@{user.id}> and lost **${amount}**")
            e.set_thumbnail(url="http://www.skillifynow.com/wp-content/uploads/2017/03/money3.jpg")
            await ctx.send(embed=e)
            return
        elif rob > 50:
            await self.bot.db.execute(f"UPDATE economy SET balance = balance + $1 WHERE userid = {ctx.author.id};", amount)
            await self.bot.db.execute(f"UPDATE economy SET balance = balance - $1 WHERE userid = {user.id};", amount)
            e = discord.Embed(color=discord.Color.green())
            e.set_author(name=f"{ctx.author.name}'s Rob", icon_url=ctx.author.avatar_url)
            e.add_field(name="Robbing", value=f"You have successfully robbed <@{user.id}> and taken their **${amount}**!")
            e.set_thumbnail(url="http://www.skillifynow.com/wp-content/uploads/2017/03/money3.jpg")
            await ctx.send(embed=e)
            return

    @rob.error
    async def rob_handler(self, ctx, error):
        import traceback; traceback.print_exception(type(error), error, error.__traceback__)
        if isinstance(error, commands.CommandOnCooldown):
            seconds = error.retry_after
            seconds = round(seconds, 2)
            hours, remainder = divmod(int(seconds), 3600)
            minutes, seconds = divmod(remainder, 60)
            await ctx.send(f"You are on cooldown! Please try again in **{seconds} seconds**")

    @commands.command(aliases=['day'])
    @commands.cooldown(1, 86400, BucketType.user)
    async def daily(self, ctx):
        """Collect your daily amount of money"""

        amount = randint(1500, 2500)

        data = await self.bot.db.fetchrow(f"SELECT balance FROM economy WHERE userid={ctx.author.id}")
        if not data:
            self.bot.get_command("daily").reset_cooldown(ctx)
            await ctx.send(f"**{ctx.author.name}** does not have an account! Use the register command `{ctx.prefix}register` to create an account.")
            return

        money = data['balance']

        await self.bot.db.execute(f"UPDATE economy SET balance = balance + $1 WHERE userid={ctx.author.id};", amount)
        e = discord.Embed(color=discord.Color.green())
        e.add_field(name="Daily <:yes:473312268998803466>", value=f"You have retrieved your **daily** amount of money. You have recieved **${amount}** and has been **added** to your balance")
        e.set_thumbnail(url="http://www.skillifynow.com/wp-content/uploads/2017/03/money3.jpg")
        await ctx.send(embed=e)

    @daily.error
    async def daily_handler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            seconds = error.retry_after
            seconds = round(seconds, 2)
            hours, remainder = divmod(int(seconds), 3600)
            minutes, seconds = divmod(remainder, 60)
            await ctx.send(f"You are on cooldown! Please try again in **{hours} hours, {minutes} minutes, {seconds} seconds**")

    @commands.command(aliases=['hour'])
    @commands.cooldown(1, 86400, BucketType.user)
    async def hourly(self, ctx):
        """Collect your daily amount of money"""

        amount = randint(250, 500)

        data = await self.bot.db.fetchrow(f"SELECT balance FROM economy WHERE userid={ctx.author.id}")
        if not data:
            self.bot.get_command("hourly").reset_cooldown(ctx)
            await ctx.send(f"**{ctx.author.name}** does not have an account! Use the register command `{ctx.prefix}register` to create an account.")
            return

        money = data['balance']

        await self.bot.db.execute(f"UPDATE economy SET balance = balance + $1 WHERE userid = {ctx.author.id};", amount)
        e = discord.Embed(color=discord.Color.green())
        e.add_field(name="Hourly <:yes:473312268998803466>", value=f"You have retrieved your **hourly** amount of money. You have recieved **${amount}** and has been **added** to your balance")
        e.set_thumbnail(url="http://www.skillifynow.com/wp-content/uploads/2017/03/money3.jpg")
        await ctx.send(embed=e)

    @hourly.error
    async def hourly_handler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            seconds = error.retry_after
            seconds = round(seconds, 2)
            hours, remainder = divmod(int(seconds), 3600)
            minutes, seconds = divmod(remainder, 60)
            await ctx.send(f"You are on cooldown! Please try again in **{minutes} minutes, {seconds} seconds**")

    @commands.command(aliases=['add'])
    @checks.has_permissions(manage_guild=True)
    async def update(self, ctx, user: discord.User, amount: int):
        """Updates an amount of money from your balance

         You must have Manage Server permission to use this command"""

        data = await self.bot.db.fetchrow(f"SELECT balance FROM economy WHERE userid={user.id}")
        money = data['balance']
        
        await self.bot.db.execute("UPDATE economy SET balance = balance + $1 WHERE userid = $2;", amount, ctx.author.id)
        e = discord.Embed(color=discord.Color.green())
        e.add_field(name="Updated <:yes:473312268998803466>", value=f"I have added **${amount}** into <@{user.id}>'s Wallet. They now have **${money+amount}**, and before had **${money}**")
        e.set_thumbnail(url="http://www.skillifynow.com/wp-content/uploads/2017/03/money3.jpg")
        await ctx.send(embed=e)

    @commands.command(aliases=['set_money', 'set_bal', 'bal_adjust'])
    @checks.has_permissions(manage_guild=True)
    async def set_amount(self, ctx, user: discord.User, amount: int):
        """Sets an amount of money for a user

        You must have Manage Server permission to use this command"""

        data = await self.bot.db.fetchrow("SELECT balance FROM economy WHERE userid=$1;", userid)
        money = data['balance']   

        await self.bot.db.execute("UPDATE economy SET balance = 0 + $1 WHERE userid = $2;", amount, userid)
        e = discord.Embed(color=discord.Color.green())
        e.add_field(name="Set Amount <:yes:473312268998803466>", value=f"<@{user.id}> now has **${amount}** in their wallet, and before had **${money}**")
        e.set_thumbnail(url="http://www.skillifynow.com/wp-content/uploads/2017/03/money3.jpg")
        await ctx.send(embed=e)

    @commands.command(aliases=['subtract'])
    @checks.has_permissions(manage_guild=True)
    async def remove(self, ctx, user: discord.User, amount: int):
        """Removes an amount of money fror your balance"""

        data = await self.bot.db.fetchrow(f"SELECT balance FROM economy WHERE userid={user.id}")
        money = data['balance']
        
        await self.bot.db.execute(f"UPDATE economy SET balance = balance - $1 WHERE userid = {user.id};", amount)
        e = discord.Embed(color=discord.Color.green())
        e.add_field(name="Removed <:yes:473312268998803466>", value=f"I have removed **${amount}** from <@{user.id}>'s Wallet. They now have **${money-amount}**, and before had **${money}**")
        e.set_thumbnail(url="http://www.skillifynow.com/wp-content/uploads/2017/03/money3.jpg")
        await ctx.send(embed=e)

    @commands.command(aliases=['lb'])
    async def leaderboard(self, ctx, type="global"):
        """Shows the Wallet Money leaderboard"""
        
        available_types = 'global'
        if type not in available_types:
            raise await ctx.send("Please specify what leaderboard type you would like to choose. Choices are: **global**")

        lb = await self.bot.db.fetch("SELECT * FROM economy ORDER BY balance DESC LIMIT 15")
        lbnum = await self.bot.db.fetch("SELECT * FROM economy ORDER BY balance DESC LIMIT 100000;")

        if type == 'global':
            desc = [f"{a+1}. **{self.bot.get_user(lb[a]['userid'])}** - ${lb[a]['balance']}\n" for a in range(len(lb))]
        
        embed = discord.Embed(color=discord.Colour.blurple())
        embed.add_field(name="Global Wallet Money Leaderboard", value=''.join(desc))
        embed.add_field(name="Total Users:", value=len(lbnum), inline=False)
        embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['flower'], hidden=True)
    async def plant(self, ctx, flower: str, amount: int):
        """Plant a hot or cold flower"""

        available_types = 'hot', 'cold'
        if flower not in available_types:
            raise await ctx.send("Please specify what flower you would like to pick. Choices are: **hot** and **cold**")

        data = await self.bot.db.fetchrow(f"SELECT balance FROM economy WHERE userid={ctx.author.id}")
        if not data:
            await ctx.send(f"**{ctx.author.name}** does not have an account! Use the register command `{ctx.prefix}register` to create an account.")
            return

        flowers = random.choice(['Red', 'Yellow', 'Orange', 'Blue', 'Pastel', 'Purple', 'Rainbow'])
        hotflowers = random.choice(['Red', 'Yellow', 'Orange'])
        coldflowers = random.choice(['Blue', 'Pastel', 'Purple'])
        userchoice = random.choice(['hot', 'cold'])

        money = data['balance']

        if amount > money:
            em = discord.Embed(color=16720640)
            em.add_field(name="Error <:no:473312284148498442>", value=f"You don't have enough money for that bet! You have **${money}**")
            await ctx.send(embed=em)
            return
        if amount < 100:
            em = discord.Embed(color=16720640)
            em.add_field(name="Error <:no:473312284148498442>", value=f"The minimum amount of money you can bet is **$100**")
            await ctx.send(embed=em)
            return

        if flowers == 'Red':
            flowerurl = "https://vignette.wikia.nocookie.net/runescape2/images/6/6c/Red_flowers_detail.png/revision/latest?cb=20160918221431"
            flowercolour = 16720640

        elif flowers == 'Orange':
            flowerurl = "https://vignette.wikia.nocookie.net/runescape2/images/9/99/Orange_flowers_detail.png/revision/latest?cb=20160918221429"
            flowercolour = discord.Color.orange()

        elif flowers == 'Blue':
            flowerurl = "https://vignette.wikia.nocookie.net/runescape2/images/d/d6/Blue_flowers_detail.png/revision/latest?cb=20160918221426"
            flowercolour = 0x0042F3

        elif flowers == 'Yellow':
            flowerurl = 'https://cdn.discordapp.com/attachments/381963689470984203/481207196227469333/kriXGoogle.png'
            flowercolour = 0xE9F40B

        elif flowers == 'Pastel':
            flowerurl = 'https://vignette.wikia.nocookie.net/runescape2/images/5/55/Flowers_%28pastel%29_detail.png/revision/latest?cb=20160918221429'
            flowercolour = 0x96A4DA

        elif flowers == 'Purple':
            flowerurl = 'https://cdn.discordapp.com/attachments/381963689470984203/481206682437943326/kriXGoogle.png'
            flowercolour = 0x9663F5

        if flowers == userchoice:
            await self.bot.db.execute(f"UPDATE economy SET balance=balance+{amount} WHERE userid={ctx.author.id};")
            e = discord.Embed(color=flowercolour)
            e.add_field(name=f"A {flowers} flower has been drawn!", value=f"You have guessed **correctly**, and won **${amount*2}**!")
            e.set_thumbnail(url=flowerurl)
            e.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=e)
            return
        else: 
            await self.bot.db.execute(f"UPDATE economy SET balance=balance-{amount} WHERE userid={ctx.author.id};")
            e = discord.Embed(color=flowercolour)
            e.add_field(name=f"A {flowers} flower has been drawn!", value=f"You have guessed **incorrectly**, and lost **${amount}**")
            e.set_thumbnail(url=flowerurl)
            e.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=e)
            return
        if flowers != userchoice:
            await self.bot.db.execute(f"UPDATE economy SET balance=balance+{amount} WHERE userid={ctx.author.id};")
            e = discord.Embed(color=flowercolour)
            e.add_field(name=f"A {flowers} flower has been drawn!", value=f"You have guessed **correctly**, and won **${amount*2}**!")
            e.set_thumbnail(url=flowerurl)
            e.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=e)
            return  
        else: 
            await self.bot.db.execute(f"UPDATE economy SET balance=balance-{amount} WHERE userid={ctx.author.id};")
            e = discord.Embed(color=flowercolour)
            e.add_field(name=f"A {flowers} flower has been drawn!", value=f"You have guessed **incorrectly**, and lost **${amount}**")
            e.set_thumbnail(url=flowerurl)
            e.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=e)
            return


def setup(bot):
    bot.add_cog(Economy(bot))