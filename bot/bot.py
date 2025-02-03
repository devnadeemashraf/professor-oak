import os
import asyncio
import discord
from discord.ext import commands

from bot.cogs.db import DatabaseManager
from bot.utils.logger import get_logger, configure_logger
from bot.utils.error_handling import setup_error_handling

from config.config import config


class ProfessorOakBot(commands.Bot):
    """
    A Discord bot for managing Pokemon sets, inheriting from commands.Bot.

    Provides database management, logging, and extension loading capabilities.
    """

    def __init__(
        self,
        base_path: str,
        db_file: str = config.DATABASE_FILE,
        command_prefix: str = config.COMMAND_PREFIX,
    ):
        """
        Initialize the Professor Oak Discord bot.

        Args:
            base_path (str): Base path for sprite and data files
            db_file (str, optional): Path to the database file
            command_prefix (str, optional): Command prefix for bot interactions
        """
        # Configure intents
        intents = discord.Intents.default()
        intents.message_content = True

        # Initialize bot with command prefix and intents
        super().__init__(command_prefix=command_prefix, intents=intents)

        # Configuration and path setup
        self.base_path = base_path
        self.db_file = db_file

        # Logger setup
        self.logger = get_logger(__name__)

        # Database manager
        self.db = DatabaseManager(db_file)

        # Error handling setup
        setup_error_handling(self)

    async def _initialize_database(self):
        """
        Asynchronously initialize and load database.

        Handles database schema creation and data loading with comprehensive error handling.
        """
        try:
            # Create database schema
            self.db.create_database_schema()

            # Load Pokemon data
            self.db.load_pokemon_data_from_json(self.base_path)

            self.logger.info("Database initialization completed successfully.")

        except Exception as e:
            self.logger.error(f"Critical database initialization error: {e}")
            raise RuntimeError(f"Failed to initialize database: {e}")

    async def _load_bot_extensions(self):
        """
        Load bot extensions asynchronously.

        Handles loading of cogs and extensions with error tracking.
        """
        try:
            # Load commands extension
            await self.load_extension("bot.cogs.commands")
            self.logger.info("Bot extensions loaded successfully.")

        except Exception as e:
            self.logger.error(f"Error loading bot extensions: {e}")
            raise

    async def setup_hook(self):
        """
        Asynchronous setup hook called before bot starts.

        Handles database initialization and extension loading.
        """
        try:
            # Initialize database
            await self._initialize_database()

            # Load bot extensions
            await self._load_bot_extensions()

        except Exception as e:
            self.logger.critical(f"Bot setup failed: {e}")
            await self.close()

    async def on_ready(self):
        """
        Event handler for when bot successfully connects to Discord.
        """
        self.logger.info(f"Professor Oak Bot logged in as {self.user}")
        self.logger.info(f"Connected to {len(self.guilds)} guilds")


def run_bot(base_path: str):
    """
    Run the Professor Oak Discord bot.

    Args:
        base_path (str): Base path for sprite and data files
    """
    # Configure global logging
    configure_logger()

    # Initialize bot
    bot = ProfessorOakBot(base_path)

    try:
        # Run the bot with the token from config
        asyncio.run(bot.start(config.DISCORD_TOKEN))

    except Exception as e:
        bot.logger.critical(f"Bot startup failed: {e}")

    finally:
        bot.logger.info("Bot shutdown initiated.")


# Typical entry point in main.py or run.py
if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    run_bot(base_path)
