import os
import json
import sqlite3
from typing import Dict, Any, List

from bot.models import PokemonData, PokemonSet
from bot.utils.logger import get_logger


class DatabaseManager:
    def __init__(self, db_file: str = "pokemon_sets_data.db"):
        """
        Initialize the database manager with logging and connection handling.

        Args:
            db_file (str): Path to the SQLite database file
        """
        self.db_file = db_file
        self.logger = get_logger(__name__)
        self._connection = None
        self._cursor = None

    def _establish_connection(self):
        """
        Establish a database connection with error handling.

        Returns:
            sqlite3.Connection: Database connection
        """
        try:
            self._connection = sqlite3.connect(self.db_file)
            self._cursor = self._connection.cursor()
            return self._connection
        except sqlite3.Error as e:
            self.logger.error(f"Database connection error: {e}")
            raise

    def _close_connection(self):
        """
        Safely close the database connection.
        """
        try:
            if self._connection:
                self._connection.close()
                self._connection = None
                self._cursor = None
        except sqlite3.Error as e:
            self.logger.error(f"Error closing database connection: {e}")

    def create_database_schema(self):
        """
        Create the database schema if it doesn't exist.
        """
        try:
            self._establish_connection()
            self._cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS pokemon (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    sprite_url TEXT NOT NULL,
                    random_sets TEXT DEFAULT '[]'
                )
                """
            )
            self._connection.commit()
            self.logger.info("Database schema created successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Schema creation error: {e}")
            raise
        finally:
            self._close_connection()

    def load_pokemon_data_from_json(self, base_path: str):
        """
        Load Pokemon data from a JSON file into the database.

        Args:
            base_path (str): Base path for sprite images
        """
        try:
            # Validate JSON file exists
            json_path = "bot/data/national_dex.json"
            if not os.path.exists(json_path):
                raise FileNotFoundError(f"Pokemon data file not found: {json_path}")

            # Read JSON data
            with open(json_path, "r") as f:
                pokemon_data = json.load(f)

            # Establish connection
            self._establish_connection()

            # Insert Pokemon data
            for name, data in pokemon_data.items():
                try:
                    # Construct absolute sprite path
                    relative_path = data["image_path"].replace("\\", "/")
                    absolute_path = os.path.join(base_path, relative_path)

                    # Validate sprite exists
                    if not os.path.exists(absolute_path):
                        self.logger.warning(
                            f"Sprite not found for {name}: {absolute_path}"
                        )
                        continue

                    # Insert or ignore Pokemon
                    self._cursor.execute(
                        """
                        INSERT OR IGNORE INTO pokemon 
                        (id, name, sprite_url, random_sets) 
                        VALUES (?, ?, ?, ?)
                        """,
                        (data["id"], name, absolute_path, "[]"),
                    )
                except sqlite3.IntegrityError:
                    self.logger.warning(f"Duplicate entry for {name}")

            # Commit and close
            self._connection.commit()
            self.logger.info("Pokemon data loaded successfully.")
        except Exception as e:
            self.logger.error(f"Error loading Pokemon data: {e}")
            raise
        finally:
            self._close_connection()

    async def get_pokemon_data(self, pokemon_name: str) -> PokemonData:
        """
        Retrieve Pokemon data by name.

        Args:
            pokemon_name (str): Name of the Pokemon

        Returns:
            PokemonData: Pokemon information

        Raises:
            ValueError: If Pokemon not found
        """
        try:
            self._establish_connection()
            self._cursor.execute(
                """
                SELECT id, name, sprite_url, random_sets
                FROM pokemon
                WHERE LOWER(name) = LOWER(?)
                """,
                (pokemon_name,),
            )

            result = self._cursor.fetchone()
            if not result:
                raise ValueError(f"Pokemon '{pokemon_name}' not found!")

            id, name, sprite_url, random_sets_json = result
            random_sets = json.loads(random_sets_json)

            return PokemonData(id, name, sprite_url, random_sets)
        except sqlite3.Error as e:
            self.logger.error(f"Database retrieval error: {e}")
            raise
        finally:
            self._close_connection()

    async def add_pokemon_set(self, pokemon_name: str, new_set: PokemonSet):
        """
        Add a new Pokemon set to the database.

        Args:
            pokemon_name (str): Name of the Pokemon
            new_set (PokemonSet): Set to be added
        """
        try:
            # Retrieve existing Pokemon data
            pokemon_data = await self.get_pokemon_data(pokemon_name)

            # Establish connection
            self._establish_connection()

            # Update sets
            random_sets = pokemon_data.random_sets
            random_sets.append(vars(new_set))

            # Update database
            self._cursor.execute(
                """
                UPDATE pokemon
                SET random_sets = ?
                WHERE id = ?
                """,
                (json.dumps(random_sets), pokemon_data.id),
            )
            self._connection.commit()
            self.logger.info(f"Added new set for {pokemon_name}")
        except Exception as e:
            self.logger.error(f"Error adding Pokemon set: {e}")
            raise
        finally:
            self._close_connection()

    async def delete_pokemon_set(self, pokemon_name: str, set_index: int):
        """
        Delete a specific Pokemon set.

        Args:
            pokemon_name (str): Name of the Pokemon
            set_index (int): Index of the set to delete

        Raises:
            ValueError: If set index is invalid
        """
        try:
            # Retrieve existing Pokemon data
            pokemon_data = await self.get_pokemon_data(pokemon_name)

            # Validate set index
            if set_index < 0 or set_index >= len(pokemon_data.random_sets):
                raise ValueError(f"Invalid set index for {pokemon_name}")

            # Establish connection
            self._establish_connection()

            # Remove the set
            random_sets = pokemon_data.random_sets
            del random_sets[set_index]

            # Update database
            self._cursor.execute(
                """
                UPDATE pokemon
                SET random_sets = ?
                WHERE id = ?
                """,
                (json.dumps(random_sets), pokemon_data.id),
            )
            self._connection.commit()
            self.logger.info(f"Deleted set {set_index} for {pokemon_name}")
        except Exception as e:
            self.logger.error(f"Error deleting Pokemon set: {e}")
            raise
        finally:
            self._close_connection()

    async def reset_database(self):
        """
        Reset the entire database by dropping and recreating the schema.
        """
        try:
            self._establish_connection()

            # Drop existing table
            self._cursor.execute("DROP TABLE IF EXISTS pokemon")

            # Recreate schema
            self.create_database_schema()

            self.logger.info("Database reset successfully.")
        except Exception as e:
            self.logger.error(f"Database reset error: {e}")
            raise
        finally:
            self._close_connection()
