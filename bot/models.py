from typing import List
from dataclasses import dataclass

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
