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

from datetime import datetime
from re import sub
from typing import Union

from .utils import _replace


class LichessObject:

    """
    A class that represents a custom object for the library.
    """

    def __init__(self, _data: Union[dict, list, tuple]):
        self._data = _data
        if isinstance(self._data, dict):
            for key, value in self._data.items():
                _key = type(key)(sub(r"(?<!^)(?=[A-Z])", "_", str(key)).lower())
                if isinstance(value, (list, tuple)):
                    self.__setattr__(_key, [LichessObject(index) if isinstance(index, (dict, list, tuple)) else index for index in value])
                elif isinstance(value, dict):
                    self.__setattr__(_key, LichessObject(value))
                else:
                    self.__setattr__(_key, value)
        else:
            self.__getitem__ = lambda index: [LichessObject(index) if isinstance(index, (dict, list, tuple)) else index for index in value][index]

    def __eq__(self, __o: object) -> bool:
        for attribute in dir(self):
            if attribute.startswith("_"):
                continue
            if getattr(self, attribute, None) != getattr(__o, attribute, None):
                return False
        return True


class Player:

    """
    A class that represents a player.
    """

    def __init__(self, _data: dict) -> None:
        self._data = _data
        player = LichessObject(self._data)
        player.created_at, player.seen_at = datetime.fromtimestamp(player.created_at / 1000), datetime.fromtimestamp(player.seen_at / 1000)
        self.__dict__.update(player.__dict__)


class RatingList:

    """
    A class that represents a list of ratings.
    """

    def __init__(self, _data: list) -> None:
        self._data = _data

    def __getitem__(self, index: int) -> LichessObject:
        rating = LichessObject({})
        rating.date = datetime(self._data[index][0], self._data[index][1] + 1, self._data[index][2])
        rating.rating = self._data[index][3]
        return rating


class RatingHistory:

    """
    A class that represents a user's rating history.
    """

    def __init__(self, _data: list) -> None:
        self._data = {}

        for item in _data:
            self._data[item["name"]] = item["points"]

        self.ultra_bullet = RatingList(self._data["UltraBullet"])
        self.bullet = RatingList(self._data["Bullet"])
        self.blitz = RatingList(self._data["Blitz"])
        self.rapid = RatingList(self._data["Rapid"])
        self.classical = RatingList(self._data["Classical"])
        self.chess960 = RatingList(self._data["Chess960"])
        self.crazyhouse = RatingList(self._data["Crazyhouse"])
        self.antichess = RatingList(self._data["Antichess"])
        self.atomic = RatingList(self._data["Atomic"])
        self.horde = RatingList(self._data["Horde"])
        self.king_of_the_hill = RatingList(self._data["King of the Hill"])
        self.racing_kings = RatingList(self._data["Racing Kings"])
        self.three_check = RatingList(self._data["Three-check"])


class GamesList:

    """
    A class that represents a list of games.
    """

    def __init__(self, _data: list) -> None:
        self._data = _data

    def __getitem__(self, index: int) -> LichessObject:
        game = LichessObject(self._data[index])
        game.at = datetime.strptime(game.at, "%Y-%m-%dT%H:%M:%S.%fZ")
        return game


class PerformanceStatistic:

    """
    A class that represents a performance statistic.
    """

    def __init__(self, _data: list) -> None:
        self._data = _replace(_data, "at", lambda item: datetime.strptime(item, "%Y-%m-%dT%H:%M:%S.%fZ"))
        self.__dict__.update(LichessObject(self._data).__dict__)


class Game:

    """
    A class that represents a game.
    """

    def __init__(self, _data: dict) -> None:
        self._data = _data
        game = LichessObject(self._data)
        game.created_at = datetime.fromtimestamp(game.created_at / 1000)
        try:
            game.last_move_at = datetime.fromtimestamp(game.last_move_at / 1000)
        except AttributeError:
            pass
        self.__dict__.update(game.__dict__)


class TvGamesList:

    """
    A class that represents a list of TV games.
    """

    def __init__(self, _data: list) -> None:
        self._data = _data
        self.ultra_bullet = LichessObject(self._data["UltraBullet"])
        self.bullet = LichessObject(self._data["Bullet"])
        self.blitz = LichessObject(self._data["Blitz"])
        self.rapid = LichessObject(self._data["Rapid"])
        self.classical = LichessObject(self._data["Classical"])
        self.chess960 = LichessObject(self._data["Chess960"])
        self.crazyhouse = LichessObject(self._data["Crazyhouse"])
        self.antichess = LichessObject(self._data["Antichess"])
        self.atomic = LichessObject(self._data["Atomic"])
        self.horde = LichessObject(self._data["Horde"])
        self.king_of_the_hill = LichessObject(self._data["King of the Hill"])
        self.racing_kings = LichessObject(self._data["Racing Kings"])
        self.three_check = LichessObject(self._data["Three-check"])
        self.bot = LichessObject(self._data["Bot"])
        self.computer = LichessObject(self._data["Computer"])
        self.top_rated = LichessObject(self._data["Top Rated"])


class Puzzle:

    """
    A class that represents a puzzle.
    """

    def __init__(self, _data: dict) -> None:
        self._data = _data
        puzzle = LichessObject(self._data)
        puzzle.date = datetime.fromtimestamp(puzzle.date)
        self.__dict__.update(puzzle.__dict__)


class SwissTournament:

    """
    A class that represents a Swiss tournament.
    """

    def __init__(self, _data: dict) -> None:
        self._data = _data
        tournament = LichessObject(self._data)
        tournament.next_round.at, tournament.starts_at = datetime.strptime(tournament.next_round_at, "%Y-%m-%dT%H:%M:%S.%fZ"), datetime.strptime(tournament.starts_at, "%Y-%m-%dT%H:%M:%S.%fZ")
        self.__dict__.update(tournament.__dict__)


class ArenaTournament:

    """
    A class that represents an Arena tournament.
    """

    def __init__(self, _data: dict) -> None:
        self._data = _data
        tournament = LichessObject(self._data)
        tournament.starts_at = datetime.strptime(tournament.starts_at, "%Y-%m-%dT%H:%M:%S.%fZ")
        self.__dict__.update(tournament.__dict__)


class RequestList:

    """
    A class that represents a list of requests.
    """

    def __init__(self, _data: list) -> None:
        self._data = _data

    def __getitem__(self, index: int) -> LichessObject:
        request = LichessObject({})
        request.request = LichessObject(self._data[index]["request"])
        request.request.date = datetime.fromtimestamp(request.request.date / 1000)
        request.user = Player(self._data[index]["user"])
        return request
