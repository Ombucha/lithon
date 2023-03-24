"""
MIT License

Copyright (c) 2022 Omkaar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


from __future__ import annotations

from typing import Iterator, Union, Optional, Literal, List, Callable, TYPE_CHECKING
from json import loads, JSONDecodeError
from threading import Thread
from warnings import warn

from .exceptions import UncallableError, LichessException
from .models import Game, LichessObject
from .client import Client
from .utils import _get, _post

if TYPE_CHECKING:
    from requests import Session


class Bot(Client):

    """
    A class that represents a Bot account.
    """

    def __init__(self, token: Optional[str] = "", *, session: Optional[Session] = None) -> None:
        super().__init__(token, session = session)
        try:
            if getattr(self.get_profile(), "title", None) != "BOT":
                warn("It is advisable to use the 'Client' class instead of this class for user accounts. Many critical methods of this class cannot be accessed through user accounts.", UserWarning, stacklevel = 2)
        except LichessException as error:
            raise LichessException("invalid authorization token.") from error

    def stream_board_state(self, game_id: str) -> Iterator[Union[Game, LichessObject]]:
        """
        Streams changes in the state of a game being played.

        :param game_id: The ID of the game.
        :type game_id: :class:`str`
        """
        response = _get(f"/api/bot/game/stream/{game_id}", self, ndjson = True, stream = True)
        for item in response.iter_lines():
            try:
                try:
                    yield Game(item)
                except AttributeError:
                    yield LichessObject(item)
            except JSONDecodeError:
                pass

    def on_new_game_state(self, game_id: str) -> Callable:
        """
        Event that is called when there is a new game state.

        .. note::

            The first response is always of type ``gameFull``.

        :param game_id: The ID of the game.
        :type game_id: :class:`str`
        """
        def decorator(function: Callable):

            def process():

                response = _get(f"/api/bot/game/stream/{game_id}", self, ndjson = True, stream = True)

                for item in response.iter_lines():
                    try:
                        try:
                            function(state = Game(loads(item.decode("utf-8"))))
                        except AttributeError:
                            function(state = LichessObject(loads(item.decode("utf-8"))))
                    except JSONDecodeError:
                        pass

            thread = Thread(target = process)
            thread.start()

            def error():
                raise UncallableError("functions used for events are not callable.")

            return error

        return decorator

    def make_board_move(self, game_id: str, move: str, *, with_draw_offering: Optional[bool] = None) -> bool:
        """
        Makes a move in a game being played.

        :param game_id: The ID of the game.
        :type game_id: :class:`str`
        :param move: The move to play, in the UCI format.
        :type move: :class:`str`
        :param with_draw_offering: Whether to offer (or agree to) a draw or not.
        :type with_draw_offering: Optional[:class:`bool`]
        """
        data = _post(f"/api/bot/game/{game_id}/move/{move}", self, data = {"offeringDraw": with_draw_offering})
        return data["ok"]

    def post_chat_message(self, game_id: str, room: Literal["player", "spectator"], text: str) -> bool:
        """
        Posts a message to the player or spectator chat, in a game being played.

        :param game_id: The ID of the game.
        :type game_id: :class:`str`
        :param room: The room to post the message in.
        :type room: Literal["player", "spectator"]
        :param text: The contents of the message to post.
        :type text: :class:`str`
        """
        data = _post(f"/api/bot/game/{game_id}/chat", self, data = {"room": room, "text": text})
        return data["ok"]

    def get_game_chat(self, game_id: str) -> List[LichessObject]:
        """
        Fetches a game's chat history.

        :param game_id: The ID of the game.
        :type game_id: :class:`str`
        """
        data = _get(f"/api/bot/game/{game_id}/chat", self, ndjson = True)
        return [LichessObject(item) for item in data]

    def abort_game(self, game_id: str) -> bool:
        """
        Aborts an ongoing game.

        :param game_id: The ID of the game.
        :type game_id: :class:`str`
        """
        data = _post(f"/api/bot/game/{game_id}/abort", self)
        return data["ok"]

    def resign_game(self, game_id: str) -> bool:
        """
        Resigns an ongoing game.

        :param game_id: The ID of the game.
        :type game_id: :class:`str`
        """
        data = _post(f"/api/bot/game/{game_id}/resign", self)
        return data["ok"]
