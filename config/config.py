import os
from dotenv import load_dotenv

# Load Env Variables
load_dotenv()

class Config:
    DEBUG_MODE = os.getenv("DEBUG_MODE", "True") == "True"

    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

    DATABASE_FILE = os.getenv("DATABASE_FILE", "pokemon_sets_data.db")
    DATABASE_URL = os.getenv("DATABASE_URL")

    COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "^oak")

    LOGGER_NAME = os.getenv("LOGGER_NAME", "professor_oak")
    LOGGER_FILE_NAME = os.getenv("LOGGER_FILE_NAME", "professor_oak_bot_logs.log")

config = Config()