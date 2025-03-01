import asyncio
import random
from typing import Optional

from aiogram.enums import ParseMode
from aiogram.types import Message

from src.bot.keyboards import get_stop_autoplay_keyboard, get_back_profile_keyboard
from src.core.api.client import GameAPI
from src.core.models.game import GameSession, Game, Drop
from src.utils.logger import set_user_context, logger, clear_user_context


class GameManager:
    def __init__(self, api: GameAPI, user_info: Optional[dict] = None):
        self.api = api
        self.user_info = user_info or {}

    def _parse_user_energy(self, data: dict) -> int:
        if not data or not data.get("success"):
            return 0

        return data.get("data", {}).get("profile", {}).get("attempts", 0)

    def _parse_box_drop(self, data: dict) -> Optional[Drop]:
        if not data or not data.get("success"):
            return None

        prizes = data.get("data", {}).get("prizes", [])
        if not prizes or len(prizes) == 0:
            return None

        drop_data = prizes[0]  # Берем первый элемент из списка prizes
        return Drop(
            title=drop_data.get("title", "unknown"),
            attempts=drop_data.get("attempts", 0),
            money=drop_data.get("money", 0),
            score=drop_data.get("score", 0)
        )

    def _parse_box_limit(self, data: dict) -> Optional[int]:
        if not data or not data.get("success"):
            return None

        items = data.get("data", {}).get("items", [])
        return items[0].get("limit", 0) if items else 0

    async def get_user_energy(self) -> int:
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
        """
        Парсит данные игровой сессии
        :param session_data:
        :return: GameSession - данные об игровой сессии
        """
        log = session_data.get("data", {}).get("log", {})
        return GameSession(
            game_type=log.get("type"),
            max_score=log.get("max_score", 0)
        )

    # async def get_available_games(self) -> List[Game]:
    #     """Получает список доступных игр"""
    #     result = self.api.get_games_list()
    #     if not result or not result.get("success"):
    #         return []
    #
    #     games = result.get("data", {}).get("games", [])
    #     return [self._parse_game(game) for game in games]

    async def _play_game(self, game_name: str, message: Message) -> bool:
        """
        Базовый метод для запуска и игры в любую игру
        :param game_name: название игры
        :return: bool - успешность выполнения
        """
        if self.user_info:
            set_user_context(self.user_info.get("id"), self.user_info.get("username"))

        try:
            logger.info(f"Начинаем игру {game_name}")

            # Начинаем игру
            result = self.api.start_game(game_name)
            if not result or not result.get("success"):
                logger.error(f"Не удалось начать игру {game_name}")
                await message.edit_text(f"🎮 <b>{game_name}</b> не удалось начать!", parse_mode=ParseMode.HTML)
                return False

            # Парсим данные сессии
            session = self._parse_game_session(result)
            if not session:
                logger.error("Не удалось получить данные игровой сессии")
                await message.edit_text("❌ Не удалось получить данные игровой сессии", parse_mode=ParseMode.HTML)
                return False

            # Имитируем реальную игру с задержкой
            delay = random.uniform(7, 11)
            await asyncio.sleep(delay)

            # Получаем соответствующий метод для завершения конкретной игры
            end_game_method = getattr(self.api, f"end_{game_name.lower()}_game")

            # Завершаем игру
            end_result = end_game_method(50)
            if end_result and end_result.get("success"):
                logger.info(f"Игра {game_name} завершена со счетом {50}")
                await message.edit_text(f"🎮 <b>{game_name}</b> успешно завершена! Счет: {50}",
                                        parse_mode=ParseMode.HTML)
                return True
            else:
                logger.error(f"Не удалось завершить игру {game_name}")
                await message.edit_text(f"🎮 <b>{game_name}</b> не удалось завершить!", parse_mode=ParseMode.HTML)
                return False
        finally:
            if self.user_info:
                clear_user_context()


    async def enough_user_energy(self, message: Message) -> bool:
        """Проверяет энергию пользователя"""
        user_energy = await self.get_user_energy()

        if user_energy < 1:
            logger.info(f"Недостаточно энергии: {user_energy}")
            await message.edit_text(f"⚡ <b>Недостаточно энергии: {user_energy}</b>",
                                    parse_mode=ParseMode.HTML)
            return False
        elif not user_energy:
            logger.error("Не удалось получить энергию пользователя")
            await message.edit_text("❌ <b>Не удалось получить энергию пользователя</b>",
                                    parse_mode=ParseMode.HTML)
            return False
        return True

    async def play_jumper(self, message: Message, tg_logging: bool = True) -> bool:
        """Играет в Jumper"""
        if self.user_info:
            set_user_context(self.user_info.get("id"), self.user_info.get("username"))
        try:
            logger.info(f"Начинаем игру Jumper")

            # Начинаем игру
            result = self.api.start_game("Jumper")
            if not result or not result.get("success"):
                logger.error(f"Не удалось начать игру Jumper")
                await message.edit_text(f"🎮 <b>Прыжки</b> не удалось начать!", parse_mode=ParseMode.HTML)
                return False

            # Парсим данные сессии
            session = self._parse_game_session(result)
            if not session:
                logger.error("Не удалось получить данные игровой сессии")
                await message.edit_text("❌ Не удалось получить данные игровой сессии", parse_mode=ParseMode.HTML)
                return False

            # Имитируем реальную игру с задержкой
            # TODO выбор длительности для бесконечных игр
            delay = random.uniform(15, 21)
            await asyncio.sleep(delay)

            # Завершаем игру
            end_result = self.api.end_jumper_game(random.randint(200, 220), 100)
            if end_result and end_result.get("success"):
                logger.info(f"Игра Jumper завершена! Счет: {end_result.get('data').get('log').get('score', 0)}")
                if tg_logging:
                    await message.edit_text(
                        f"🎮 <b>Прыжки</b> успешно завершены! Счет: {end_result.get('data').get('log').get('score', 0)}"
                        f"\n Получено монет: {end_result.get('data').get('log').get('money_collected', 0)}",
                        parse_mode=ParseMode.HTML)
                return True
            else:
                logger.error(f"Не удалось завершить игру Jumper")
                if tg_logging:
                    await message.edit_text(f"🎮 <b>Прыжки</b> не удалось завершить!", parse_mode=ParseMode.HTML)
                return False
        finally:
            if self.user_info:
                clear_user_context()


    # TODO runner
    async def play_runner(self, message: Message, tg_logging: bool = True) -> bool:
        """Играет в Runner"""
        if self.user_info:
            set_user_context(self.user_info.get("id"), self.user_info.get("username"))
        try:
            logger.info(f"Начинаем игру Runner")

            # Начинаем игру
            result = self.api.start_game("Runner")
            if not result or not result.get("success"):
                logger.error(f"Не удалось начать игру Runner")
                await message.edit_text(f"🎮 <b>Бьюти-пад</b> не удалось начать!", parse_mode=ParseMode.HTML)
                return False

            # Парсим данные сессии
            session = self._parse_game_session(result)
            if not session:
                logger.error("Не удалось получить данные игровой сессии")
                await message.edit_text("❌ Не удалось получить данные игровой сессии", parse_mode=ParseMode.HTML)
                return False

            # Имитируем реальную игру с задержкой
            # TODO выбор длительности для бесконечных игр
            delay = random.uniform(15, 21)
            await asyncio.sleep(delay)

            # Завершаем игру
            end_result = self.api.end_runner_game(random.randint(180, 220), 100)
            if end_result and end_result.get("success"):
                logger.info(f"Игра Runner завершена! Счет: {end_result.get('data').get('log').get('score', 0)}")
                if tg_logging:
                    await message.edit_text(
                        f"🎮 <b>Бьюти-пад</b> успешно завершен! Счет: {end_result.get('data').get('log').get('score', 0)}"
                        f"\n Получено монет: {end_result.get('data').get('log').get('money_collected', 0)}",
                        parse_mode=ParseMode.HTML)
                return True
            else:
                logger.error(f"Не удалось завершить игру Runner")
                if tg_logging:
                    await message.edit_text(f"🎮 <b>Бьюти-пад</b> не удалось завершить!", parse_mode=ParseMode.HTML)
                return False
        finally:
            if self.user_info:
                clear_user_context()

    async def play_match3(self, message: Message) -> bool:
        """Играет в Match3"""
        return await self._play_game("Match3", message)

    async def play_memories(self, message: Message) -> bool:
        """Играет в Memories"""
        return await self._play_game("Memories", message)


    # TODO make games different
    async def auto_play_games(self, message: Message) -> None:
        """
        Автоматически играет в Jumper столько раз, сколько позволяет энергия игрока.
        Делает перерыв между играми в 1 секунду и показывает прогресс.
        Имеет кнопку для остановки процесса.
        """
        # Флаг для отслеживания остановки процесса
        self.auto_play_running = True

        try:
            # Получаем текущую энергию игрока
            energy = await self.get_user_energy()

            if energy <= 0:
                await message.edit_text("❌ Недостаточно энергии для игры", parse_mode=ParseMode.HTML)
                return

            logger.info(f"Начинаем автоматическую игру в Jumper. Доступно энергии: {energy}")
            await message.edit_text(f"🎮 <b>Авто-игра Jumper</b> запущена!\nДоступно энергии: {energy}",
                                    parse_mode=ParseMode.HTML)

            games_played = 0
            total_games = energy

            # Создаем сообщение для статуса с кнопкой остановки
            keyboard = get_stop_autoplay_keyboard()
            status_message = await message.answer(
                f"⏳ Прогресс: [{games_played}/{total_games}]",
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )

            # Для предотвращения ошибки "message is not modified"
            last_status_text = f"⏳ Прогресс: [{games_played}/{total_games}]"

            while games_played < total_games and self.auto_play_running:
                # Запускаем игру с tg_logging=False
                success = await self.play_jumper(message, tg_logging=False)

                if success:
                    games_played += 1
                    logger.info(f"Успешно сыграна игра {games_played} из {total_games}")
                else:
                    logger.error(f"Ошибка при игре {games_played + 1} из {total_games}")

                # Обновляем статус только если текст изменился
                new_status_text = f"⏳ Прогресс: [{games_played}/{total_games}]"
                if new_status_text != last_status_text:
                    try:
                        await status_message.edit_text(
                            new_status_text,
                            parse_mode=ParseMode.HTML,
                            reply_markup=keyboard
                        )
                        last_status_text = new_status_text
                    except Exception as e:
                        if "message is not modified" not in str(e):
                            logger.error(f"Ошибка при обновлении статуса: {str(e)}")

                # Делаем перерыв в 1 секунду между играми
                if games_played < total_games and self.auto_play_running:
                    await asyncio.sleep(1)

            # Финальное сообщение
            if self.auto_play_running:  # Если процесс не был остановлен пользователем
                final_status = f"✅ Авто-игра завершена! Сыграно игр: [{games_played}/{total_games}]"
                if final_status != last_status_text:
                    try:
                        await status_message.edit_text(
                            final_status,
                            parse_mode=ParseMode.HTML,
                            reply_markup=get_back_profile_keyboard()
                        )
                    except Exception as e:
                        if "message is not modified" not in str(e):
                            logger.error(f"Ошибка при обновлении финального статуса: {str(e)}")

                await message.edit_text(
                    f"🎮 <b>Авто-игра Jumper</b> завершена!\nСыграно игр: <b>{games_played}</b>",
                    parse_mode=ParseMode.HTML
                )

        except Exception as e:
            logger.error(f"Ошибка в auto_play_games: {str(e)}")
            await message.edit_text(f"❌ Ошибка при автоматической игре: {str(e)}", parse_mode=ParseMode.HTML)

        finally:
            # Сбрасываем флаг запуска
            self.auto_play_running = False

    async def start_jumper(self, message: Message):
        if self.user_info:
            set_user_context(self.user_info.get("id"), self.user_info.get("username"))

        try:
            if not await self.enough_user_energy(message):
                return

            if not await self.play_jumper(message):
                await message.edit_text("❌ Не смогли сыграть в Прыжки", parse_mode=ParseMode.HTML)
                return
        finally:
            if self.user_info:
                clear_user_context()

    async def start_runner(self, message: Message):
        if self.user_info:
            set_user_context(self.user_info.get("id"), self.user_info.get("username"))

        try:
            if not await self.enough_user_energy(message):
                return

            if not await self.play_runner(message):
                await message.edit_text("❌ Не смогли сыграть в Бьюти-пад", parse_mode=ParseMode.HTML)
                return
        finally:
            if self.user_info:
                clear_user_context()

    async def start_match3(self, message: Message):
        if self.user_info:
            set_user_context(self.user_info.get("id"), self.user_info.get("username"))

        try:
            if not await self.enough_user_energy(message):
                return

            if not await self.play_match3(message):
                await message.edit_text("❌ Не смогли сыграть в Три в ряд", parse_mode=ParseMode.HTML)
                return
        finally:
            if self.user_info:
                clear_user_context()

    async def start_memories(self, message: Message):
        if self.user_info:
            set_user_context(self.user_info.get("id"), self.user_info.get("username"))

        try:
            if not await self.enough_user_energy(message):
                return

            if not await self.play_memories(message):
                await message.edit_text("❌ Не смогли сыграть в карточки", parse_mode=ParseMode.HTML)
                return
        finally:
            if self.user_info:
                clear_user_context()

    async def open_box(self, message: Message):
        """Открывает обычный бокс за 300 монет"""
        if self.user_info:
            set_user_context(self.user_info.get("id"), self.user_info.get("username"))
        try:
            logger.info("Открытие обычного бокса")

            result = self.api.open_standard_box()
            if not result or not result.get("success"):
                logger.error("Не удалось открыть ящик")
                msg = "❌ Не удалось открыть ящик\n"
                msg += f"🎁 Можно открыть боксов сегодня: <b>{await self.get_limit(message)}</b>"
                await message.edit_text(msg, parse_mode=ParseMode.HTML)
                return False

            result = self._parse_box_drop(result)
            logger.info(f"Открыл бокс [{result}]")
            msg = f"🎊 Выпало: <b>{result.title}</b>\n"
            msg += f"⚡️ Получено энергии: <b>{result.attempts}</b>\n" if result.attempts is not None else ""
            msg += f"🪙 Получено монет: <b>{result.money}</b>\n" if result.money is not None else ""
            msg += f"🌟 Получено опыта: <b>{result.score}</b>\n" if result.score is not None else ""

            # TODO get limit from list
            msg += f"\n🎁 Можно открыть боксов сегодня: <b>{await self.get_limit(message)}</b>"

            await message.edit_text(
                f"{msg}",
                parse_mode=ParseMode.HTML
            )
            return
        finally:
            if self.user_info:
                clear_user_context()

    async def get_limit(self, message: Message) -> int:
        if self.user_info:
            set_user_context(self.user_info.get("id"), self.user_info.get("username"))
        try:
            logger.info("Получение лимита")
            result = self.api.get_limit()
            if not result or not result.get("success"):
                logger.error("Не удалось получить лимит")
                await message.edit_text("❌ Не удалось получить лимит", parse_mode=ParseMode.HTML)
                return False
            return self._parse_box_limit(result)
        finally:
            if self.user_info:
                clear_user_context()
