import random
import time
from typing import List, Optional

from game import GameSession, Game
from src.core.api.client import GameAPI
from src.core.models.beauty_procedure import Profile


class GameManager:
    def __init__(self, api: GameAPI):
        self.api = api

    def _parse_user_energy(self, data: dict) -> int:
        if not data or not data.get("success"):
            return None

        profile_data = data.get("data", {}).get("profile", {})
        return profile_data.get("attempts", 0)


    def get_user_energy(self) -> int:
        """Получает профиль игрока с информацией о бьюти процедурах"""
        result = self.api.get_profile()
        return self._parse_user_energy(result)

    def _parse_game(self, game_data: dict) -> Game:
        return Game(
            name=game_data.get("name"),
            is_available=game_data.get("isAvailable", False),
            timeout=game_data.get("timeout", 0),
            energy=game_data.get("energy", 0)
        )

    def _parse_game_session(self, session_data: dict) -> Optional[GameSession]:
        log = session_data.get("data", {}).get("log", {})
        return GameSession(
            game_type=log.get("type"),
            max_score=log.get("max_score", 0)
        )

    def get_available_games(self) -> List[Game]:
        """Получает список доступных игр"""
        result = self.api.get_games_list()
        if not result or not result.get("success"):
            return []

        games = result.get("data", {}).get("games", [])
        return [self._parse_game(game) for game in games]

    def play_jumper(self) -> bool:
        """Играет в Jumper"""
        # Начинаем игру
        print("\033[33m    - Начинаем игру Jumper\033[0m")
        result = self.api.start_game("Jumper")
        if not result or not result.get("success"):
            print("Не удалось начать игру Jumper")
            return False

        # Парсим данные сессии
        session = self._parse_game_session(result)
        if not session:
            print("Не удалось получить данные игровой сессии")
            return False

        # Имитируем реальную игру с задержкой
        delay = random.uniform(9, 15)  # случайная задержка от 2 до 4 секунд
        time.sleep(delay)

        # Завершаем игру
        end_result = self.api.end_jumper_game(session.max_score)
        if end_result and end_result.get("success"):
            print(f"\033[97mУспешно завершена игра Jumper со счетом {session.max_score}\033[0m")
            return True
        else:
            print("\033[91mНе удалось завершить игру Jumper\033[0m")
            return False

    def play_match3(self) -> bool:
        """Играет в Match3"""
        # Начинаем игру
        print("\033[33m    - Начинаем игру Match3\033[0m")
        result = self.api.start_game("Match3")
        if not result or not result.get("success"):
            print("Не удалось начать игру Match3")
            return False

        # Парсим данные сессии
        session = self._parse_game_session(result)
        if not session:
            print("Не удалось получить данные игровой сессии")
            return False

        # Имитируем реальную игру с задержкой
        delay = random.uniform(9, 15)  # случайная задержка от 2 до 4 секунд
        time.sleep(delay)

        # Завершаем игру
        end_result = self.api.end_match3_game(session.max_score)
        if end_result and end_result.get("success"):
            print(f"\033[97mУспешно завершена игра Match3 со счетом {session.max_score}\033[0m")
            return True

    def play_memories(self) -> bool:
        """Играет в Memories"""
        print("\033[33m    - Начинаем игру Memories\033[0m")
        result = self.api.start_game("Memories")
        if not result or not result.get("success"):
            print("Не удалось начать игру Memories")
            return False

        # Парсим данные сессии
        session = self._parse_game_session(result)
        if not session:
            print("Не удалось получить данные игровой сессии")
            return False

        # Имитируем реальную игру с задержкой
        delay = random.uniform(9, 15)  # случайная задержка от 2 до 4 секунд
        time.sleep(delay)

        # Завершаем игру
        end_result = self.api.end_memories_game(session.max_score)
        if end_result and end_result.get("success"):
            print(f"\033[97mУспешно завершена игра Memories со счетом {session.max_score}\033[0m")
            return True


    def play_runner(self) -> bool:
        """Играет в Runner"""
        print("\033[33m    - Начинаем игру Runner\033[0m")
        result = self.api.start_game("Runner")
        if not result or not result.get("success"):
            print("Не удалось начать игру Runner")
            return False

        # Парсим данные сессии
        session = self._parse_game_session(result)
        if not session:
            print("Не удалось получить данные игровой сессии")
            return False

        # Имитируем реальную игру с задержкой
        delay = random.uniform(9, 15)  # случайная задержка от 2 до 4 секунд
        time.sleep(delay)

        # Завершаем игру
        end_result = self.api.end_runner_game(session.max_score)
        if end_result and end_result.get("success"):
            print(f"\033[97mУспешно завершена игра Runner со счетом {session.max_score}\033[0m")
            return True



    def auto_play_games(self):
        """Автоматически играет в игры по очереди, пока есть энергия"""
        print("\033[33m=== Автоматический запуск игр ===\033[0m")

        game_sequence = ["Jumper", "Match3", "Runner", "Memories"]  # Список игр в порядке очередности

        while True:
            games = self.get_available_games()
            user_energy = self.get_user_energy()

            if not user_energy:
                print("Не удалось получить данные профиля игрока")
                break

            for game_name in game_sequence:
                game = next((g for g in games if g.name == game_name), None)

                if not game or not game.is_available or user_energy < game.energy:
                    print(f"Игра {game_name} недоступна или закончилась энергия")
                    continue

                try:
                    if game_name == "Jumper":
                        if not self.play_jumper():
                            print("Ошибка при запуске игры Jumper")
                    elif game_name == "Match3":
                        if not self.play_match3():
                            print("Ошибка при запуске игры Match3")
                    elif game_name == "Runner":
                        if not self.play_runner():
                            print("Ошибка при запуске игры Runner")
                    elif game_name == "Memories":
                        if not self.play_memories():
                            print("Ошибка при запуске игры Memories")

                    # Обновляем уровень энергии после игры
                    user_energy = self.get_user_energy()
                    if not user_energy:
                        print("Энергия игрока исчерпана")
                        break

                except Exception as e:
                    print(f"Ошибка при выполнении {game_name}: {e}")
                    break

            else:
                # Если ни одна игра не может быть запущена, завершаем цикл
                print("Ни одна игра не была запущена. Завершаем автоматический запуск.")
                break

        print("\033[33m=== Автоматический запуск игр завершен ===\033[0m")

