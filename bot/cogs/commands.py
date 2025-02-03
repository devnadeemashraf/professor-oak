import os
import logging
from typing import List, Optional

import discord
from discord.ext import commands
import bcrypt

from bot.utils.logger import get_logger
from bot.models import PokemonSet
from bot.utils.error_handling import rate_limit
from bot.cogs.db import DatabaseManager

from config.config import config


class PokemonCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DatabaseManager()
        self.logger = get_logger(__name__)
        self.hashed_password = self._hash_admin_password()

    def _hash_admin_password(self) -> bytes:
        """
        Securely hash the admin password during initialization.

        Returns:
            bytes: Hashed password
        """
        try:
            return bcrypt.hashpw(config.ADMIN_PASSWORD.encode(), bcrypt.gensalt())
        except Exception as e:
            self.logger.error(f"Password hashing failed: {e}")
            raise

    def _validate_admin_password(self, provided_password: str) -> bool:
        """
        Validate the provided admin password.

        Args:
            provided_password (str): Password to validate

        Returns:
            bool: Whether password is valid
        """
        try:
            return bcrypt.checkpw(provided_password.encode(), self.hashed_password)
        except Exception as e:
            self.logger.error(f"Password validation error: {e}")
            return False

    def _format_pokemon_name(self, name: str) -> str:
        """
        Consistently format Pokemon names (lowercase, replace hyphens).

        Args:
            name (str): Raw Pokemon name

        Returns:
            str: Formatted Pokemon name
        """
        return name.lower().replace("-", " ")

    def _validate_moves_and_item(self, moves: List[str], item: str) -> bool:
        """
        Validate moves and item for a Pokemon set.

        Args:
            moves (List[str]): List of moves
            item (str): Item name

        Returns:
            bool: Whether moves and item are valid
        """
        # Add more sophisticated validation if needed
        if len(moves) != 4:
            return False
        if not item:
            return False
        return all(move.strip() for move in moves)

    @commands.command(name=".help")
    @rate_limit()
    async def send_help_message(self, ctx):
        """
        Display comprehensive help message for Pokemon set commands.
        """

        help_message = (
            "🌟 **Professor Oak's Pokémon Set Management** 🐾\n\n"
            "**Public Commands:**\n"
            "1. `!oak.set <pokemon> <item> <move1> <move2> <move3> <move4>`\n"
            "   Example: ```!oak.set pikachu light-ball thunderbolt quick-attack iron-tail volt-tackle```\n\n"
            "2. `!oak.get <pokemon>`\n"
            "   Example: ```!oak.get pikachu```\n\n"
            "**Admin Commands:** 🔐\n"
            "3. `!oak.delete <pokemon> <set-id> <admin-password>`\n"
            "   (Requires admin authentication)\n\n"
            "4. `!oak.clean <admin-password>`\n"
            "   (Clears all existing sets)\n\n"
            "**Quick Tips:**\n"
            "- Use hyphens for multi-word items/moves (e.g., `light-ball`)\n"
            "- Admin commands need special access 🔑\n\n"
            "[⭐ Check us out on Github](https://github.com/devnadeemashraf/professor-oak)"
        )

        await ctx.send(help_message)

    @commands.command(name=".set")
    @rate_limit()
    async def create_pokemon_set(self, ctx, pokemon: str, *args):
        """
        Add a new Pokemon set with comprehensive error handling.
        """
        try:
            # Validate input
            if len(args) != 5:
                raise ValueError("Provide: <item> <move1> <move2> <move3> <move4>")

            item, *moves = args

            # Normalize names
            pokemon = self._format_pokemon_name(pokemon)
            item = item.replace("-", " ")
            moves = [move.replace("-", " ") for move in moves]

            # Validate moves and item
            if not self._validate_moves_and_item(moves, item):
                raise ValueError("Invalid moves or item format")

            # Add Pokemon set
            new_set = PokemonSet(item=item, moves=moves)
            await self.db.add_pokemon_set(pokemon, new_set)

            # Confirmation message
            await ctx.send(
                f"✅ Added new set for {pokemon.title()}!\n"
                f"Item: {item}\n"
                f"Moves: {', '.join(moves)}"
            )

        except ValueError as ve:
            await ctx.send(f"❌ Error: {ve}")
        except Exception as e:
            self.logger.error(f"Set creation error: {e}")
            await ctx.send("❌ An unexpected error occurred while creating the set.")

    @commands.command(name=".get")
    @rate_limit()
    async def retrieve_pokemon_sets(self, ctx, pokemon: str):
        """
        Retrieve and display Pokemon sets with enhanced error handling.
        """
        try:
            # Normalize Pokemon name
            pokemon = self._format_pokemon_name(pokemon)
            pokemon_data = await self.db.get_pokemon_data(pokemon)

            if not pokemon_data.random_sets:
                await ctx.send(f"No sets found for {pokemon.title()}.")
                return

            # Create embed for better visualization
            embed = discord.Embed(
                title=f"{pokemon.title()}'s Random Sets", color=discord.Color.green()
            )

            # Add Pokemon sprite to embed
            embed.set_thumbnail(url=f"attachment://sprite.png")

            # Add sets to embed
            for i, set_data in enumerate(pokemon_data.random_sets, 1):
                set_text = (
                    f"**Item:** {set_data['item']}\n"
                    f"**Moves:**\n"
                    + "\n".join(f"• {move}" for move in set_data["moves"])
                )
                embed.add_field(name=f"Set {i}", value=set_text, inline=False)

            # Send the sprite as a file attachment
            with open(pokemon_data.sprite_url, "rb") as f:
                sprite = discord.File(f, filename="sprite.png")

            await ctx.send(file=sprite, embed=embed)

        except FileNotFoundError:
            await ctx.send(f"No data found for {pokemon.title()}.")
        except Exception as e:
            self.logger.error(f"Set retrieval error: {e}")
            await ctx.send("❌ An error occurred while retrieving sets.")

    @commands.command(name=".delete")
    @rate_limit()
    async def remove_pokemon_set(self, ctx, pokemon: str, set_id: int, password: str):
        """
        Securely delete a specific Pokemon set.
        """
        if not self._validate_admin_password(password):
            await ctx.send("❌ Invalid admin password.")
            return

        try:
            pokemon = self._format_pokemon_name(pokemon)
            await self.db.delete_pokemon_set(pokemon, set_id)
            await ctx.send(
                f"✅ Set {set_id} for {pokemon.title()} deleted successfully."
            )

        except ValueError as ve:
            await ctx.send(f"❌ Error: {ve}")
        except Exception as e:
            self.logger.error(f"Set deletion error: {e}")
            await ctx.send("❌ An unexpected error occurred while deleting the set.")

    @commands.command(name=".clean")
    @rate_limit()
    async def reset_database(self, ctx, password: str):
        """
        Securely clean/reset the entire database.
        """
        if not self._validate_admin_password(password):
            await ctx.send("❌ Invalid admin password.")
            return

        try:
            await self.db.reset_database()
            await ctx.send("✅ Database has been reset successfully.")

        except Exception as e:
            self.logger.error(f"Database reset error: {e}")
            await ctx.send("❌ An error occurred while resetting the database.")


async def setup(bot):
    await bot.add_cog(PokemonCommands(bot))
