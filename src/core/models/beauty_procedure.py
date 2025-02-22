from dataclasses import dataclass
from typing import Optional

@dataclass
class BeautyProcedure:
    id: int
    title: str
    action: str
    cost: int
    score: int
    multiplier: float
    multiplier_user_money: float
    is_new: bool
    description: Optional[str] = None

@dataclass
class Profile:
    attempts: int
    score: int
    money: int
    level: int
    attempts_cooldown: int
    attempts_restored_at: int
    beauty_procedures: list[BeautyProcedure]
    username: str

@dataclass
class UserRating:
    score: int
    position: int

    def can_afford_procedure(self, procedure_cost: int) -> bool:
        return self.money >= procedure_cost