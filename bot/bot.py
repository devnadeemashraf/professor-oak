import discord
from discord.ext import commands
from bot.cogs.db import Database
from bot.utils.logger import setup_logger
from bot.utils.error_handling import setup_error_handling

from config.config import config

class ProfessorOak(commands.Bot):
    def __init__(self, base_path: str, db_file: str = config.DATABASE_FILE):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=config.COMMAND_PREFIX, intents=intents)
        
        self.base_path = base_path
        self.db_file = db_file

        self.db = Database(db_file)
        self.logger = setup_logger()

        self.setup_database()
        self.load_pokemon_data()

        setup_error_handling(self)

    def setup_database(self):
        # Make sure to handle potential database setup errors
        try:
            self.db.setup_database()
        except Exception as e:
            self.logger.error(f"Error during database setup: {e}")
            raise

    def load_pokemon_data(self):
        try:
            self.db.load_pokemon_data(self.base_path)
            self.logger.info("Pokémon data loaded successfully.")
        except Exception as e:
            self.logger.error(f"Error loading Pokémon data: {e}")
    
    async def setup_hook(self):
        await self.load_extension('bot.cogs.commands')

    async def on_ready(self):
        self.logger.info(f'Logged in as {self.user}')
