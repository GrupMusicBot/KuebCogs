from .leveling import Level

def setup(bot):
    cog = Level(bot)
    bot.add_cog(cog)