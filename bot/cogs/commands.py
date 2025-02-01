import discord

from discord.ext import commands
from bot.models import PokemonSet

from bot.utils.error_handling import rate_limit

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.command(name='set')
    @rate_limit()
    async def upset(self, ctx, pokemon: str, *args):
        """
        Add a new set for a Pokemon.
        Usage: ^upset <pokemon> <item> <move1> <move2> <move3> <move4>
        """
        try:
            # Ensure that there are exactly 5 arguments after the pokemon name
            if len(args) != 5:
                raise ValueError("You must provide exactly 5 arguments: item and four moves.\nIf you are trying to enter a two letter word, join it with a hyphen (example: light-ball)")

            item, move1, move2, move3, move4 = args

            # Ensure Moves are valid (allow hyphenated moves like 'shell-smash')
            moves = [move1, move2, move3, move4]

            # Remove all '-' hyphens
            for idx, move in enumerate(moves):
                moves[idx] = move.replace('-', ' ')

            # Create a PokemonSet with the given inputs
            new_set = PokemonSet(
                item=item.replace('-', ' '),
                moves=moves
            )

            # Add the set to the Pokemon's database entry
            await self.db.add_pokemon_set(pokemon, new_set)

            # Send a confirmation message with cleaned-up text
            await ctx.send(f"Added new set for {pokemon.replace('-', ' ')}!\n"
                        f"Item: {item.replace('-', ' ')}\n"
                        f"Moves: {move1.replace('-', ' ')}, {move2.replace('-', ' ')}, "
                        f"{move3.replace('-', ' ')}, and {move4.replace('-', ' ')}.")

        except ValueError as e:
            await ctx.send(f"```{str(e)}```")

    @commands.command(name='get')
    @rate_limit()
    async def getset(self, ctx, pokemon: str):
        """
        Get all sets for a Pokemon with a formatted display.
        Usage: ^getset <pokemon>
        """
        try:
            pokemon_data = await self.db.get_pokemon_data(pokemon)

            if not pokemon_data.random_sets:  # Check if the Pokemon has no sets
                await ctx.send(f"```It seems that no random sets have been added for {pokemon_data.name} yet.```")
                return
            
            # Create an attractive embed for the response
            embed = discord.Embed(
                title=f"{pokemon_data.name}'s Random Sets",
                color=0x00FF00
            )
            embed.set_thumbnail(url=f"attachment://sprite.png")
            
            # Add each set to the embed with proper formatting
            for i, set_data in enumerate(pokemon_data.random_sets, 1):
                set_text = (
                    f"Item: {set_data['item']}\n"
                    f"Moves:\n"
                    f"- {set_data['moves'][0]}\n"
                    f"- {set_data['moves'][1]}\n"
                    f"- {set_data['moves'][2]}\n"
                    f"- {set_data['moves'][3]}"
                )
                embed.add_field(
                    name=f"Set {i}",
                    value=set_text,
                    inline=False
                )
            
            # Send the sprite as a file attachment
            with open(pokemon_data.sprite_url, 'rb') as f:
                sprite = discord.File(f, filename="sprite.png")
            
            await ctx.send(file=sprite, embed=embed)
        except ValueError as e:
            await ctx.send(f"```{str(e)}```")
        except FileNotFoundError:
            await ctx.send(f"```Sprite file not found for {pokemon}```")

async def setup(bot):
    await bot.add_cog(Commands(bot))