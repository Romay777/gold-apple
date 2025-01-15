from dataclasses import dataclass

@dataclass
class Game:
   name: str
   is_available: bool
   timeout: int
   energy: int

@dataclass
class GameSession:
   game_type: str
   max_score: int