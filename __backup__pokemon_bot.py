import discord
from discord.ext import commands, tasks
from discord.ext.commands import BucketType
import json
import sqlite3
import os
from typing import List
from dataclasses import dataclass

# Rate limit for the upset command (1 per minute per user, adjust as needed)
def rate_limit():
    return commands.cooldown(6, 15, BucketType.user)  # 6 use per 15 seconds per user

# Data classes for type safety and better structure
@dataclass
class PokemonSet:
    """Represents a single set of moves and items for a Pokemon"""
    item: str
    moves: List[str]

@dataclass
class PokemonData:
    """Contains all information about a Pokemon, including its sets and asset locations"""
    id: int
    name: str
    sprite_url: str
    random_sets: List[PokemonSet]

class PokemonBot(commands.Bot):
    def __init__(self, base_path: str, db_file: str = 'pokemon_data.db'):
        # Initialize Discord bot with necessary intents
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='^', intents=intents)
        
        # Store the base path for assets to ensure correct file access
        self.base_path = base_path
        
        # Path to the SQLite database file
        self.db_file = db_file
        
        # Initialize the SQLite database
        self.conn = sqlite3.connect(self.db_file)
        self.setup_database()
        self.load_pokemon_data()

    def setup_database(self):
        """Initialize the SQLite database with the required schema."""
        cursor = self.conn.cursor()
        # Create the main pokemon table with all necessary fields
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS pokemon (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                sprite_url TEXT NOT NULL,
                random_sets TEXT DEFAULT '[]'  -- Store JSON array of sets
            )
        ''')
        self.conn.commit()

    def load_pokemon_data(self):
        """
        Load Pokemon data from the JSON file into the database.
        Converts relative paths from the JSON into absolute paths based on base_path.
        """
        if not os.path.exists('national_dex.json'):
            print("Error: national_dex.json file not found.")
            return
        
        with open('national_dex.json', 'r') as f:
            pokemon_data = json.load(f)

        cursor = self.conn.cursor()
        for name, data in pokemon_data.items():
            # Convert the relative path from JSON to an absolute path
            # Replace backslashes with forward slashes for consistency
            relative_path = data['image_path'].replace('\\', '/')
            absolute_path = os.path.join(self.base_path, relative_path)
            
            # Verify that the sprite file exists
            if not os.path.exists(absolute_path):
                print(f"Warning: Sprite file not found for {name}: {absolute_path}")
                continue

            cursor.execute('''
                INSERT OR IGNORE INTO pokemon (id, name, sprite_url, random_sets)
                VALUES (?, ?, ?, ?)
            ''', (data['id'], name, absolute_path, '[]'))
        self.conn.commit()

    async def get_pokemon_data(self, pokemon_name: str) -> PokemonData:
        """
        Retrieve Pokemon data from the database.
        Performs case-insensitive search for better user experience.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, name, sprite_url, random_sets
            FROM pokemon
            WHERE LOWER(name) = LOWER(?)
        ''', (pokemon_name,))
        
        result = cursor.fetchone()
        if not result:
            raise ValueError(f"Pokemon '{pokemon_name}' not found!")
        
        id, name, sprite_url, random_sets_json = result
        random_sets = json.loads(random_sets_json)
        return PokemonData(id, name, sprite_url, random_sets)

    async def add_pokemon_set(self, pokemon_name: str, new_set: PokemonSet):
        """Add a new set to a Pokemon's random_sets collection."""
        try:
            pokemon_data = await self.get_pokemon_data(pokemon_name)
            
            cursor = self.conn.cursor()
            random_sets = pokemon_data.random_sets
            random_sets.append(vars(new_set))
            
            cursor.execute('''
                UPDATE pokemon
                SET random_sets = ?
                WHERE id = ?
            ''', (json.dumps(random_sets), pokemon_data.id))
            
            self.conn.commit()
        except Exception as e:
            raise ValueError(f"Error adding set: {str(e)}")

    async def setup_hook(self):
        """Set up bot commands and their implementations."""

        @self.command(name='upset')
        @rate_limit()
        async def upset(ctx, pokemon: str, *args):
            """
            Add a new set for a Pokemon.
            Usage: ^upset <pokemon> <item> <move1> <move2> <move3> <move4>
            """
            try:
                # Ensure that there are exactly 5 arguments after the pokemon name
                if len(args) != 5:
                    raise ValueError("You must provide exactly 5 arguments: item and four moves.\nIf you are trying to enter a two letter word, join it with an '-' for example: light-ball.")

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
                await self.add_pokemon_set(pokemon, new_set)

                # Send a confirmation message with cleaned-up text
                await ctx.send(f"Successfully added new set for {pokemon.replace('-', ' ')}!\n"
                            f"Item: {item.replace('-', ' ')}\n"
                            f"Moves: {move1.replace('-', ' ')}, {move2.replace('-', ' ')}, "
                            f"{move3.replace('-', ' ')}, and {move4.replace('-', ' ')}.")

            except ValueError as e:
                await ctx.send(f"Error: {str(e)}")


        @self.command(name='getset')
        @rate_limit()
        async def getset(ctx, pokemon: str):
            """
            Get all sets for a Pokemon with a formatted display.
            Usage: ^getset <pokemon>
            """
            try:
                pokemon_data = await self.get_pokemon_data(pokemon)

                if not pokemon_data.random_sets:  # Check if the Pokemon has no sets
                    await ctx.send(f"Oops! It seems that no sets have been added for {pokemon_data.name} yet. Please add some sets using ^upset!")
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
                await ctx.send(f"Error: {str(e)}")
            except FileNotFoundError:
                await ctx.send(f"Error: Sprite file not found for {pokemon}")
