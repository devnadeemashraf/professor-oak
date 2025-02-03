import os
from dotenv import load_dotenv

# Load Env Variables
load_dotenv()


class Config:
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

    DEBUG_MODE = os.getenv("DEBUG_MODE", "True") == "True"

    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

    DATABASE_FILE = os.getenv("DATABASE_FILE", "pokemon_sets_data.db")
    DATABASE_URL = os.getenv("DATABASE_URL")

    COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!oak")

    LOGGER_NAME = "pokemon_bot"
    LOGGER_FILE_NAME = "logs/pokemon_bot.log"


config = Config()
