import os
from bot.bot import ProfessorOak

from config.config import config

def run_bot(token: str, base_path: str):
    bot = ProfessorOak(base_path)
    bot.run(token)

if __name__ == "__main__":
    if config.DISCORD_TOKEN is not None:
        BASE_PATH = os.path.dirname(os.path.abspath(__file__))
        run_bot(config.DISCORD_TOKEN, BASE_PATH)
    else:
        print("Environment Variable that holds 'Discord Token' not found!")