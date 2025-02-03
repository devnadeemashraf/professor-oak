from discord.ext import commands
from discord.ext.commands import BucketType


def setup_error_handling(bot):
    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("```Missing required argument.```")
        else:
            await ctx.send("```..what do you want?```")
            raise error


def rate_limit():
    return commands.cooldown(6, 15, BucketType.user)
