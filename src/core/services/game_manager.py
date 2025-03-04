import asyncio
import random
from typing import Optional, Dict, Any, List, Tuple, Callable

from aiogram.enums import ParseMode
from aiogram.types import Message

from src.bot.keyboards import get_stop_autoplay_keyboard, get_back_profile_keyboard
from src.core.api.client import GameAPI
from src.core.models.game import GameSession, Game, Drop
from src.utils.logger import set_user_context, logger, clear_user_context


class GameManager:
    """Manages game operations with efficient handling of API calls and game sessions."""

    # Game configurations - centralized game definitions
    GAMES = {
        "Jumper": {
            "display_name": "Прыжки",
            "score_range": (200, 220),
            "money": 100,
            "play_time": (15, 21),
            "additional_data": {
                "booster_count": 1
            }
        },
        "Runner": {
            "display_name": "Бьюти-пад",
            "score_range": (180, 220),
            "money": 100,
            "play_time": (15, 21),
            "additional_data": {}
        },
        "Match3": {
            "display_name": "Три в ряд",
            "score_range": (45, 55),
            "money": 100,
            "play_time": (7, 11),
            "additional_data": {"ram": 2, "cross": 2, "color": 2}
        },
        "Memories": {
            "display_name": "Карточки",
            "score_range": (45, 55),
            "money": 100,
            "play_time": (7, 11),
            "additional_data": {}
        }
    }

    def __init__(self, api: GameAPI, user_info: Optional[dict] = None):
        self.api = api
        self.user_info = user_info or {}
        self.auto_play_running = False

    # --- Data parsing methods ---

    def _parse_user_energy(self, data: dict) -> int:
        """Extract user energy from profile data."""
        if not data or not data.get("success"):
            return 0
        return data.get("data", {}).get("profile", {}).get("attempts", 0)

    def _parse_box_drop(self, data: dict) -> Optional[Drop]:
        """Parse box drop data into Drop object."""
        if not data or not data.get("success"):
            return None

        prizes = data.get("data", {}).get("prizes", [])
        if not prizes:
            return None

        drop_data = prizes[0]
        return Drop(
            title=drop_data.get("title", "unknown"),
            attempts=drop_data.get("attempts", 0),
            money=drop_data.get("money", 0),
            score=drop_data.get("score", 0)
        )

    def _parse_box_limit(self, data: dict) -> int:
        """Extract box opening limit from data."""
        if not data or not data.get("success"):
            return 0

        items = data.get("data", {}).get("items", [])
        return items[0].get("limit", 0) if items else 0

    def _parse_game(self, game_data: dict) -> Game:
        """Create Game object from API data."""
        return Game(
            name=game_data.get("name"),
            is_available=game_data.get("isAvailable", False),
            timeout=game_data.get("timeout", 0),
            energy=game_data.get("energy", 0)
        )

    def _parse_game_session(self, session_data: dict) -> Optional[GameSession]:
        """Create GameSession object from API data."""
        if not session_data or not session_data.get("success"):
            return None

        log = session_data.get("data", {}).get("log", {})
        return GameSession(
            game_type=log.get("type"),
            max_score=log.get("max_score", 0)
        )

    # --- Core API methods ---

    async def get_user_energy(self) -> int:
        """Get player's current energy."""
        result = self.api.get_profile()
        return self._parse_user_energy(result)

    async def get_limit(self, message: Message) -> int:
        """Get the remaining box opening limit for today."""
        with self._user_context():
            try:
                logger.info("Getting box opening limit")
                result = self.api.get_limit()
                if not result or not result.get("success"):
                    logger.error("Failed to get box limit")
                    await message.edit_text("❌ Не удалось получить лимит", parse_mode=ParseMode.HTML)
                    return 0
                return self._parse_box_limit(result)
            except Exception as e:
                logger.error(f"Error getting box limit: {str(e)}")
                return 0

    # --- Context manager for user context ---

    def _user_context(self):
        """Context manager to handle user context setting and clearing."""

        class UserContextManager:
            def __init__(self, manager):
                self.manager = manager

            def __enter__(self):
                if self.manager.user_info:
                    set_user_context(
                        self.manager.user_info.get("id"),
                        self.manager.user_info.get("username")
                    )
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.manager.user_info:
                    clear_user_context()

        return UserContextManager(self)

    # --- Game playing methods ---

    async def play_game(self, game_name: str, message: Message, tg_logging: bool = True) -> bool:
        """
        Universal method to play any game with consistent handling.

        Args:
            game_name: Name of the game to play
            message: Telegram message for updates
            tg_logging: Whether to log progress to Telegram

        Returns:
            bool: Success status
        """
        if game_name not in self.GAMES:
            logger.error(f"Unknown game: {game_name}")
            if tg_logging:
                await message.edit_text(f"❌ Неизвестная игра: {game_name}", parse_mode=ParseMode.HTML)
            return False

        game_config = self.GAMES[game_name]
        display_name = game_config["display_name"]

        with self._user_context():
            try:
                logger.info(f"Starting game {game_name}")

                # Start the game
                result = self.api.start_game(game_name)
                if not result or not result.get("success"):
                    logger.error(f"Failed to start game {game_name}")
                    if tg_logging:
                        await message.edit_text(f"🎮 <b>{display_name}</b> не удалось начать!",
                                                parse_mode=ParseMode.HTML)
                    return False

                # Parse session data
                session = self._parse_game_session(result)
                if not session:
                    logger.error("Failed to get game session data")
                    if tg_logging:
                        await message.edit_text("❌ Не удалось получить данные игровой сессии",
                                                parse_mode=ParseMode.HTML)
                    return False

                # Simulate gameplay with delay
                min_time, max_time = game_config["play_time"]
                delay = random.uniform(min_time, max_time)
                await asyncio.sleep(delay)

                # Generate random score within configured range
                min_score, max_score = game_config["score_range"]
                score = random.randint(min_score, max_score)
                money = game_config["money"]
                additional_data = game_config["additional_data"]

                # End the game with appropriate method
                method_name = f"end_{game_name.lower()}_game"
                end_game_method = getattr(self.api, method_name)

                # Call with appropriate parameters based on the game
                if game_name in ["Jumper", "Runner"]:
                    end_result = end_game_method(score, money, additional_data)
                elif game_name == "Match3":
                    end_result = end_game_method(score, additional_data)
                else:  # Memories or other games
                    end_result = end_game_method(score)

                print("end_result:" + str(end_result))

                if end_result and end_result.get("success"):
                    result_score = end_result.get("data", {}).get("log", {}).get("score", 0)
                    money_collected = end_result.get("data", {}).get("log", {}).get("money_collected", 0)

                    logger.info(f"Game {game_name} completed! Score: {result_score}")

                    if tg_logging:
                        message_text = f"🎮 <b>{display_name}</b> успешно завершен! Счет: {result_score}"
                        if money_collected:
                            message_text += f"\nПолучено монет: {money_collected}"
                        await message.edit_text(message_text, parse_mode=ParseMode.HTML)
                    return True
                else:
                    logger.error(f"Failed to end game {game_name}")
                    if tg_logging:
                        await message.edit_text(f"🎮 <b>{display_name}</b> не удалось завершить!",
                                                parse_mode=ParseMode.HTML)
                    return False
            except Exception as e:
                logger.error(f"Error playing {game_name}: {str(e)}")
                if tg_logging:
                    await message.edit_text(f"❌ Ошибка при игре в {display_name}: {str(e)}",
                                            parse_mode=ParseMode.HTML)
                return False

    async def enough_user_energy(self, message: Message) -> bool:
        """Check if user has enough energy to play."""
        user_energy = await self.get_user_energy()

        if user_energy < 1:
            logger.info(f"Not enough energy: {user_energy}")
            await message.edit_text(f"⚡ <b>Недостаточно энергии: {user_energy}</b>",
                                    parse_mode=ParseMode.HTML)
            return False
        elif not user_energy:
            logger.error("Failed to get user energy")
            await message.edit_text("❌ <b>Не удалось получить энергию пользователя</b>",
                                    parse_mode=ParseMode.HTML)
            return False
        return True

    # --- Game starter methods ---

    async def start_game(self, game_name: str, message: Message) -> bool:
        """Universal method to start any game with energy check."""
        with self._user_context():
            try:
                if not await self.enough_user_energy(message):
                    return False

                display_name = self.GAMES.get(game_name, {}).get("display_name", game_name)

                if not await self.play_game(game_name, message):
                    await message.edit_text(f"❌ Не смогли сыграть в {display_name}", parse_mode=ParseMode.HTML)
                    return False
                return True
            except Exception as e:
                logger.error(f"Error starting {game_name}: {str(e)}")
                await message.edit_text(f"❌ Ошибка при запуске {game_name}: {str(e)}",
                                        parse_mode=ParseMode.HTML)
                return False

    # Individual game starter methods for backward compatibility

    async def start_jumper(self, message: Message):
        """Start playing Jumper game."""
        return await self.start_game("Jumper", message)

    async def start_runner(self, message: Message):
        """Start playing Runner game."""
        return await self.start_game("Runner", message)

    async def start_match3(self, message: Message):
        """Start playing Match3 game."""
        return await self.start_game("Match3", message)

    async def start_memories(self, message: Message):
        """Start playing Memories game."""
        return await self.start_game("Memories", message)

    # --- Auto-play functionality ---

    async def auto_play_games(self, message: Message, game_name: str = None) -> None:
        """
        Automatically play all available games until energy is depleted.
        If game_name is provided, only that game will be played.

        Args:
            message: Telegram message for updates
            game_name: Optional name of a specific game to play
        """
        # Create list of games to play
        games_to_play = [game_name] if game_name and game_name in self.GAMES else list(self.GAMES.keys())

        self.auto_play_running = True

        try:
            # Get current player energy
            energy = await self.get_user_energy()

            if energy <= 0:
                await message.edit_text("❌ Недостаточно энергии для игры", parse_mode=ParseMode.HTML)
                return

            logger.info(f"Starting auto-play for {len(games_to_play)} games. Available energy: {energy}")

            games_display = ", ".join([self.GAMES[g]["display_name"] for g in games_to_play])
            await message.edit_text(f"🎮 <b>Авто-игра</b> запущена!\nИгры: {games_display}\nДоступно энергии: {energy}",
                                    parse_mode=ParseMode.HTML)

            games_played = 0
            total_games = energy

            # Create status message with stop button
            keyboard = get_stop_autoplay_keyboard()
            status_message = await message.answer(
                f"⏳ Прогресс: [{games_played}/{total_games}]",
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )

            # Track last status text to prevent "message not modified" errors
            last_status_text = f"⏳ Прогресс: [{games_played}/{total_games}]"

            # Track played games
            games_stats = {game: 0 for game in games_to_play}

            # Keep playing until energy is depleted
            while games_played < total_games and self.auto_play_running:
                # Round-robin selection of games
                current_game = games_to_play[games_played % len(games_to_play)]

                # Play the selected game
                success = await self.play_game(current_game, message, tg_logging=False)

                if success:
                    games_played += 1
                    games_stats[current_game] += 1
                    logger.info(f"Successfully played {current_game}: {games_played} of {total_games}")
                else:
                    logger.error(f"Error in game {current_game} ({games_played + 1} of {total_games})")
                    print("err:", success)

                # Update status only if text changed
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
                            logger.error(f"Error updating status: {str(e)}")

                # Pause between games
                if games_played < total_games and self.auto_play_running:
                    await asyncio.sleep(1)

            # Final message with detailed statistics
            if self.auto_play_running:
                # Prepare detailed stats
                stats_text = "\n".join([
                    f"- {self.GAMES[game]['display_name']}: {count}"
                    for game, count in games_stats.items() if count > 0
                ])

                try:
                    await status_message.delete()
                except Exception as e:
                    if "message is not modified" not in str(e):
                        logger.error(f"Error updating final status: {str(e)}")

                await message.edit_text(
                    f"✅ <b>Авто-игра</b> завершена!\n"
                    f"Сыграно игр: <b>{games_played}</b>\n\n"
                    f"<b>Статистика:</b>\n{stats_text}",
                    parse_mode=ParseMode.HTML,
                    reply_markup=get_back_profile_keyboard()
                )

        except Exception as e:
            logger.error(f"Error in auto_play_games: {str(e)}")
            await message.edit_text(f"❌ Ошибка при автоматической игре: {str(e)}", parse_mode=ParseMode.HTML)

        finally:
            # Reset auto-play flag
            self.auto_play_running = False

    # --- Box opening functionality ---

    async def open_box(self, message: Message):
        """Open a standard box for 300 coins."""
        with self._user_context():
            try:
                logger.info("Opening standard box")

                result = self.api.open_standard_box()
                if not result or not result.get("success"):
                    logger.error("Failed to open box")
                    msg = "❌ Не удалось открыть ящик\n"
                    msg += f"🎁 Можно открыть боксов сегодня: <b>{await self.get_limit(message)}</b>"
                    await message.edit_text(msg, parse_mode=ParseMode.HTML)
                    return False

                result = self._parse_box_drop(result)

                if not result:
                    logger.error("Failed to parse box drop")
                    await message.edit_text("❌ Не удалось распознать содержимое ящика", parse_mode=ParseMode.HTML)
                    return False

                logger.info(f"Opened box [{result}]")

                # Construct message with received items
                msg = f"🎊 Выпало: <b>{result.title}</b>\n"

                if result.attempts:
                    msg += f"⚡️ Получено энергии: <b>{result.attempts}</b>\n"
                if result.money:
                    msg += f"🪙 Получено монет: <b>{result.money}</b>\n"
                if result.score:
                    msg += f"🌟 Получено опыта: <b>{result.score}</b>\n"

                # Add remaining limit information
                box_limit = await self.get_limit(message)
                msg += f"\n🎁 Можно открыть боксов сегодня: <b>{box_limit}</b>"

                await message.edit_text(msg, parse_mode=ParseMode.HTML)
                return True
            except Exception as e:
                logger.error(f"Error opening box: {str(e)}")
                await message.edit_text(f"❌ Ошибка при открытии ящика: {str(e)}", parse_mode=ParseMode.HTML)
                return False