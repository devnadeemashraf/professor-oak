# Professor Oak - A Discord Bot for Pokemon Battle Sets

Professor Oak is a Python-based Discord bot that helps users manage and track random Pokémon sets used in different Pokémon Battle Simulators. Users can easily store, retrieve, and delete sets for specific Pokémon using simple commands.

## Features

- Store random Pokémon sets (moves, items, etc.)
- Retrieve stored Pokémon sets
- Delete Pokémon sets
- Admin commands for database management
- Simple and clean interface for interacting with the bot
- Custom error handling and logging utilities

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

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/devnadeemashraf/professor-oak.git
   cd professor-oak
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env`

   ```bash
   cp .env.example ..env
   ```

## Usage

    ```bash
    python run.py
    ```

### **LICENSE**

```text
MIT License

Copyright (c) 2025 <Your Name or Organization>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
