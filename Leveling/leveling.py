import time
import random
import discord
from pymongo import MongoClient
import pymongo
from redbot.core import Config, bank, commands, errors, checks


class Level(commands.Cog):
    """Leveling Command"""

    def __init__(self, bot):
        self.config = Config.get_conf(self, identifier=1072001)
        default_guild = {"Max_XP" : 25, "Min_XP" : 1}
        self.bot = bot

    async def _requiredXP(self, lvl):
        requiredXP = pow(lvl, 1.75)
        return requiredXP * 50

    @commands.command(name="xptest")
    async def xptest(self, ctx : commands.Context, Rank : int):
        """test command dont mind"""
        curr_time = 1612124276.8165956 - 1612124216.5104718
        await ctx.send(curr_time)

    @commands.group(name="levelsettings")
    @checks.mod_or_permissions()
    async def settings(self, ctx):
        """Settings for Leveling Command"""
        pass

    @settings.group(name="ranks")
    @checks.admin()
    async def ranks(self, ctx):
        """Add Levelup Ranks"""
        pass

    @ranks.command(name="add")
    @checks.admin()
    async def add(self, ctx : commands.Context, Role : discord.Role, Level : int):
        """Add a Level Rankup Role"""
        file = open("/home/discord/1360Cogs/Leveling/ranks.txt", "a")
        file.write(f"[{Role.id}:{Level}],")
        file.close()

        await ctx.send("Done, Added {} to Rank File".format(Role.name))

    @settings.group(name="xp")
    @checks.mod_or_permissions()
    async def xp(self, ctx):
        """XP Leveling Settings"""
        pass

    @xp.command(name="min")
    @checks.admin()
    async def min_XP(self, ctx : commands.Context, Value : int):
        """Minimum XP Value"""
        await self.config.guild(ctx.guild).Min_XP.set(Value)
        await ctx.send("The Minimum XP Value has been set to : **{Value}**")

    @xp.command(name="max")
    @checks.admin()
    async def max_XP(self, ctx: commands.Context, Value: int):
        """Minimum XP Value"""
        await self.config.guild(ctx.guild).Max_XP.set(Value)
        await ctx.send("The Maximum XP Value has been set to : **{Value}**")

    @commands.command(name="rank")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def rank(self, ctx : commands.Context, User : discord.Member = None):
        mongo_url = "MongoURLHere"
        cluster = MongoClient(mongo_url)
        db = cluster["TheLounge"]
        DBCollection = db["Levels"]
        if User is None:
            User = ctx.author

        try:
            insertData = DBCollection.insert_one({"_id" : User.id, "Rank" : 1, "XP" : 10, "LastMessage" : "None", "LastTime" : time.time()})

            Result = DBCollection.find({"_id": User.id})
            for results in Result:
                Rank = (results['Rank'])
                XP = (results['XP'])
            embed = discord.Embed(title=f"{User.display_name}'s Level", color=discord.Color.gold())
            embed.add_field(name="Current Level", value=f"**{Rank}**")
            requiredXP = await self._requiredXP(Rank)
            # This is only for the experience bar at the bottom on the embed
            getNum = (XP / requiredXP) * 100
            getNearstNum = (round(getNum / 10) * 10) / 10
            Bars = "▋"
            for x in range(0, int(getNearstNum - 1)):
                Bars = Bars + "▋"
            RemainingBars = "#"
            Meth = 10 - int(getNearstNum)
            for i in range(0, Meth - 1):
                RemainingBars = RemainingBars + "#"
            embed.add_field(name="XP %", value=f"[{Bars}{RemainingBars}] {round(getNum, 2)} % to the next level", inline=False)
            await ctx.send(embed=embed)
            # This actually works really well, and it looks good.

        except pymongo.errors.PyMongoError:
            # Literally if anything with PyMongo throws an error
            Result = DBCollection.find({"_id": User.id})
            for results in Result:
                Rank = (results['Rank'])
                XP = (results['XP'])

            embed = discord.Embed(title=f"{User.display_name}'s Level", color=discord.Color.gold())
            embed.add_field(name="Current Level", value=f"**{Rank}**")
            requiredXP = await self._requiredXP(Rank)
            getNum = (XP / requiredXP) * 100
            getNearstNum = (round(getNum / 10) * 10) / 10
            Bars = "▋"
            for x in range(0, int(getNearstNum - 1)):
                Bars = Bars + "▋"
            RemainingBars = "▁"
            Meth = 10 - int(getNearstNum)
            for i in range(0, Meth - 1):
                RemainingBars = RemainingBars + "▁"
            embed.add_field(name="XP %", value=f"[{Bars}{RemainingBars}] {round(getNum, 2)} % to the next level", inline=False)
            await ctx.send(embed=embed)
            
        # Need to add an
        # except Exception as e:
        # here

    @commands.Cog.listener("on_message_without_command")
    async def on_message(self, message: discord.Message):
        mongo_url = "MongoURL"
        cluster = MongoClient(mongo_url)
        db = cluster["TheLounge"]
        DBCollection = db["Levels"]
        author = message.author
        if len(message.content) <= 8:
            return

        if author.bot:
            return
        curr_time = time.time()
        # Compare the current time to the last message time

        MinXP = await self.config.guild(message.guild).Min_XP()
        MaxXP = await self.config.guild(message.guild).Max_XP()
        XPGive = random.randint(1, 25)

        try:
            insertData = DBCollection.insert_one({"_id": author.id, "Rank": 1, "XP": XPGive, "LastMessage": message.content, "LastTime" : time.time()})
        except pymongo.errors.PyMongoError:
            results = DBCollection.find({"_id" : author.id})
            for result in results:
                Rank = (result['Rank'])
                CurrentXP = (result["XP"])
                PrevMessage = (result["LastMessage"])
                LastTime = (result["LastTime"])
               
            # If 60 seconds hasn't past since the last message. Return
            if not curr_time - LastTime >= 60:
                return

            if message.content == PrevMessage:
                return

            RequiredXP = await self._requiredXP(Rank)
            if (CurrentXP >= RequiredXP):
                await message.channel.send(f"{author.mention} **you have leveled up to Level {Rank + 1}!**")
                UpdateRank = DBCollection.update_one({"_id" : author.id}, {"$inc" : {"Rank" : 1}})
                XPUpdate = DBCollection.update_one({"_id": author.id}, {"$set": {"XP": 0}})
                pass
            else:
                pass

            UpdateXP = DBCollection.update_one({"_id" : author.id}, {"$inc" : {"XP" : XPGive}})
            UpdateMessage = DBCollection.update_one({"_id" : author.id}, {"$set" : {"LastMessage" : message.content}})
            return


