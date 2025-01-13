from typing import Optional

from src.core.api.client import GameAPI
from src.core.models.beauty_procedure import BeautyProcedure, Profile


class BeautyManager:
    def __init__(self, api: GameAPI):
        self.api = api
        self.procedure_ids = [1, 2, 3]

    def _parse_profile(self, data: dict) -> Optional[Profile]:
        if not data or not data.get("success"):
            return None

        profile_data = data.get("data", {}).get("profile", {})
        return Profile(
            attempts=profile_data.get("attempts", 0),
            score=profile_data.get("score", 0),
            money=profile_data.get("money", 0),
            level=profile_data.get("level", 1),
            attempts_cooldown=profile_data.get("attemptsCooldown", 0),
            attempts_restored_at=profile_data.get("attemptsRestoredAt", 0),
            beauty_procedures=[
                BeautyProcedure(
                    id=proc.get("id"),
                    title=proc.get("title"),
                    action=proc.get("action"),
                    cost=proc.get("cost"),
                    score=proc.get("score"),
                    multiplier=proc.get("multiplier"),
                    multiplier_user_money=proc.get("multiplierUserMoney"),
                    is_new=proc.get("isNew"),
                    description=proc.get("description")
                )
                for proc in profile_data.get("beautyProcedures", [])
            ]
        )

    def get_profile(self) -> Optional[Profile]:
        """Получает профиль игрока с информацией о бьюти процедурах"""
        result = self.api.get_profile()
        return self._parse_profile(result)

    def perform_procedures(self) -> None:
        """Выполняет каждую бьюти процедуру по одному разу"""
        profile = self.get_profile()
        if not profile:
            print("Не удалось получить профиль")
            return

        for procedure_id in self.procedure_ids:
            # Находим процедуру в списке доступных
            procedure = next(
                (p for p in profile.beauty_procedures if p.id == procedure_id),
                None
            )

            if not procedure:
                print(f"Процедура с ID {procedure_id} не найдена")
                continue

            if profile.can_afford_procedure(procedure.cost):
                result = self.api.perform_beauty_procedure(procedure_id)
                if result and result.get("success"):
                    print(f"Успешно выполнена процедура: {procedure.title}")
                    profile.money -= procedure.cost
                else:
                    print(f"Не удалось выполнить процедуру: {procedure.title}")
            else:
                print(f"Недостаточно денег для процедуры: {procedure.title}")