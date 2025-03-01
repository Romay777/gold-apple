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


@dataclass
class Drop:
   title: str
   attempts: int # если энергия
   money: int # если деньги
   score: int # если exp

