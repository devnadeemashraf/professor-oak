### Folder Structure

```
~root/
│
├── bot/
│   ├── __init__.py
│   ├── bot.py  # Main bot logic
│   ├── cogs/   # Cog files (for commands)
│   │   ├── __init__.py
│   │   ├── commands.py  # Commands for Pokemon
│   │   └── db.py  # Database interaction
│   ├── data/
│   │   └── national_dex.json  # Pokemon data file
│   └── utils/
│       ├── error_handling.py  # Error handling utilities
│       └── logger.py  # Custom logger
│
├── assets/
│   └── sprites/  # Pokemon Sprite Assets
│       ├── Bulbasaur.png
│       ├── Ivysaur.png
│       └── ... more
│
├── config/
│   └── config.py  # Bot configuration (token, database URL, etc.)
│
├── requirements.txt  # List of dependencies
└── run.py  # Entry point for starting the bot
```
