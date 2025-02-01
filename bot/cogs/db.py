import sqlite3
import json
import os
from bot.models import PokemonData, PokemonSet

class Database:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file)
        self.setup_database()

    def setup_database(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pokemon (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                sprite_url TEXT NOT NULL,
                random_sets TEXT DEFAULT '[]'
            )
        ''')
        self.conn.commit()

    def load_pokemon_data(self, base_path: str):
        if not os.path.exists('bot/data/national_dex.json'):
            print("Error: national_dex.json file not found.")
            return
        
        with open('bot/data/national_dex.json', 'r') as f:
            pokemon_data = json.load(f)

        cursor = self.conn.cursor()
        for name, data in pokemon_data.items():
            relative_path = data['image_path'].replace('\\', '/')
            absolute_path = os.path.join(base_path, relative_path)

            if not os.path.exists(absolute_path):
                print(f"Warning: Sprite file not found for {name}: {absolute_path}")
                continue

            cursor.execute('''
                INSERT OR IGNORE INTO pokemon (id, name, sprite_url, random_sets)
                VALUES (?, ?, ?, ?)
            ''', (data['id'], name, absolute_path, '[]'))
        self.conn.commit()

    async def get_pokemon_data(self, pokemon_name: str) -> PokemonData:
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
        pokemon_data = self.get_pokemon_data(pokemon_name)
        cursor = self.conn.cursor()
        random_sets = pokemon_data.random_sets
        random_sets.append(vars(new_set))
        cursor.execute('''
            UPDATE pokemon
            SET random_sets = ?
            WHERE id = ?
        ''', (json.dumps(random_sets), pokemon_data.id))
        self.conn.commit()