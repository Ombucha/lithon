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
from json import JSONDecodeError, loads
from typing import Callable, Iterator, List, Tuple, Literal, Optional, Set, Union
from threading import Thread
from warnings import warn

from requests import Session

from lichess.exceptions import UncallableError

from .exceptions import LichessException
from .models import (
    ArenaTournament,
    Game,
    LichessObject,
    PerformanceStatistic,
    Player,
    Puzzle,
    RatingHistory,
    RequestList,
    SwissTournament,
    TvGamesList
    )
from .utils import _get, _post, Range


class Client:

    """
    A class that represents a client.

    :param token: The Lichess API token.
    :type token: Optional[:class:`str`]

    .. note::

        Providing an invalid token will only expose public endpoints.

    :param session: The session to use.
    :type session: Optional[:class:`requests.Session`]
    """

    def __init__(self, token: str = "", *, session: Optional[Session] = None) -> None:
        self.session = session if session else Session()
        self.session.headers = {"Authorization": f"Bearer {token}"}

        try:
            if self.__class__ == Client and getattr(self.get_profile(), "title", None) == "BOT":
                warn("It is advisable to use the 'Bot' class instead of this class for Bot accounts. Many critical methods of this class cannot be accessed through Bot accounts.", UserWarning, stacklevel = 2)
        except LichessException:
            pass

    def get_profile(self) -> Player:
        """
        Gets public information about the logged in user.
        """
        data = _get("/api/account", self)
        return Player(data)

    def get_email_address(self) -> str:
        """
        Gets the email address of the logged in user.
        """
        data = _get("/api/account/email", self)
        return data["email"]

    def get_kid_mode_status(self) -> bool:
        """
        Gets the kid mode status of the logged in user.
        """
        data = _get("/api/account/kid", self)
        return data["kid"]

    def get_preferences(self) -> LichessObject:
        """
        Gets the preferences of the logged in user.
        """
        data = _get("/api/account/preferences", self)
        return LichessObject(data)

    def set_kid_mode_status(self, value: bool) -> bool:
        """
        Sets the kid mode status of the logged in user.
        """
        data = _post("/api/account/kid", self, data = {"v": value})
        return data["ok"]

    def get_user_statuses(self, user_ids: List[str], *, with_game_ids: Optional[bool] = None) -> LichessObject:
        """
        Gets the statuses of given users.

        :param user_ids: The list of user IDs.
        :type user_ids: List[:class:`str`]
        :param with_game_ids: Whether to return the ID of the game being played, or not.
        :type with_game_ids: Optional[:class:`bool`]
        """
        data = _get("/api/users/status", self, params = {"ids": ",".join(item.lower() for item in user_ids), "withGameIds": with_game_ids})
        return LichessObject(data)

    def get_top_10(self) -> LichessObject:
        """
        Gets the top 10 players for each speed and variant.
        """
        data = _get("/api/player", self)
        return LichessObject(data)

    def get_leaderboard(self, number: Range[1, 200], performance: Literal["ultraBullet", "bullet", "blitz", "rapid", "classical", "chess960", "crazyhouse", "antichess", "atomic", "horde", "kingOfTheHill", "racingKings", "threeCheck"]) -> LichessObject:
        """
        Gets the leaderboard for a single speed or variant.

        .. note::

            There is no leaderboard for correspondence or puzzles.

        :param number: The number of users to fetch.
        :type number: Range[1, 200]
        :param performance: The speed or variant.
        :type performance: Literal["ultraBullet", "bullet", "blitz", "rapid", "classical", "chess960", "crazyhouse", "antichess", "atomic", "horde", "kingOfTheHill", "racingKings", "threeCheck"]
        """
        if number not in Range[1, 200]:
            raise ValueError("'number' must be greater than or equal to 1 and less than or equal to 200.")
        if performance.lower() not in ("ultrabullet", "bullet", "blitz", "rapid", "classical", "correspondence", "chess960", "crazyhouse", "antichess", "atomic", "horde", "kingofthehill", "racingkings", "threecheck"):
            raise ValueError("'performance' is not a valid speed or variant.")
        data = _get(f"/api/player/top/{number}/{performance}", self)
        return LichessObject(data)

    def get_user(self, username: str, *, with_trophies: Optional[bool] = None) -> Player:
        """
        Gets the leaderboard for a single speed or variant.

        .. note::

            There is no leaderboard for correspondence or puzzles.

        :param username: The username of the user.
        :type username: :class:`str`
        :param with_trophies: Whether to include user trophies, or not.
        :type with_trophies: Optional[:class:`bool`]
        """
        data = _get(f"/api/user/{username}", self, params = {"trophies": with_trophies})
        return Player(data)

    def get_rating_history(self, username: str) -> RatingHistory:
        """
        Gets the rating history of a user, for all speeds and variants.

        :param username: The username of the user.
        :type username: :class:`str`
        """
        data = _get(f"/api/user/{username}/rating-history", self)
        return RatingHistory(data)

    def get_performance_statistic(self, username: str, performance: Literal["ultraBullet", "bullet", "blitz", "rapid", "classical", "correspondence", "chess960", "crazyhouse", "antichess", "atomic", "horde", "kingOfTheHill", "racingKings", "threeCheck"]) -> PerformanceStatistic:
        """
        Gets the performance statistic of a user, for a single performance.

        :param username: The username of the user.
        :type username: :class:`str`
        :param performance: The speed or variant.
        :type performance: Literal["ultraBullet", "bullet", "blitz", "rapid", "classical", "correspondence", "chess960", "crazyhouse", "antichess", "atomic", "horde", "kingOfTheHill", "racingKings", "threeCheck"]
        """
        if performance.lower() not in ("ultrabullet", "bullet", "blitz", "rapid", "classical", "correspondence", "chess960", "crazyhouse", "antichess", "atomic", "horde", "kingofthehill", "racingkings", "threecheck"):
            raise ValueError("'performance' is not a valid speed or variant.")
        data = _get(f"/api/user/{username}/perf/{performance}", self)
        return PerformanceStatistic(data)

    def get_users(self, user_ids: List[str]) -> List[Player]:
        """
        Gets up to 300 users by their IDs.

        .. note::

            Users are returned in the same order as the IDs.

        :param user_ids: The list of user IDs.
        :type user_ids: List[:class:`str`]
        """
        data = _post("/api/users", self, data = ",".join(item.lower() for item in user_ids))
        return [Player(item) for item in data]

    def get_team_members(self, team_id: str) -> Iterator[Union[LichessObject, Player]]:
        """
        Gets members of a team.

        .. note::

            Members are sorted in reverse chronological order of joining the team (most recent first).

        :param team_id: The ID of the team.
        :type team_id: :class:`str`
        """
        response = _get(f"/api/team/{team_id}/users", self, ndjson = True, stream = True)
        for item in response.iter_lines():
            try:
                yield Player(loads(item.decode("utf-8")))
            except KeyError:
                yield LichessObject(loads(item.decode("utf-8")))

    def get_live_streamers(self) -> List[LichessObject]:
        """
        Gets basic info about currently streaming users.
        """
        data = _get("/api/streamer/live", self)
        return [LichessObject(item) for item in data]

    def get_crosstable(self, user_1: str, user_2: str, *, with_current_match_data: Optional[bool] = None) -> LichessObject:
        """
        Gets the total number of games, and current score, of any two users.

        :param user_1: The first user.
        :type user_1: :class:`str`
        :param user_2: The second user.
        :type user_2: :class:`str`
        :param with_current_match_data: Whether to get the current match data, or not, if any.
        :type with_current_match_data: :class:`bool`
        """
        data = _get(f"/api/crosstable/{user_1}/{user_2}", self, params = {"matchup": with_current_match_data})
        return LichessObject(data)

    def get_followed_players(self) -> Iterator[Player]:
        """
        Gets users followed by the logged in user.
        """
        response = _get("/api/rel/following", self, ndjson = True, stream = True)
        for item in response:
            yield Player(loads(item.decode("utf-8")))

    def follow(self, username: str) -> None:
        """
        Follows a player, adding them to the logged in user's list of Lichess friends.

        :param username: The username of the user.
        :type username: :class:`str`
        """
        _post(f"/api/rel/follow/{username}", self)

    def unfollow(self, username: str) -> None:
        """
        Unfollows a player, removing them to the logged in user's list of Lichess friends.

        :param username: The username of the user.
        :type username: :class:`str`
        """
        _post(f"/api/rel/unfollow/{username}", self)

    def export_game(
        self,
        game_id: str,
        *,
        with_pgn_moves: Optional[bool] = None,
        with_pgn: Optional[bool] = None,
        with_pgn_tags: Optional[bool] = None,
        with_clock_comments: Optional[bool] = None,
        with_evaluation: Optional[bool] = None,
        with_opening: Optional[bool] = None,
        with_annotations: Optional[bool] = None,
        players: Optional[str] = None
        ) -> Game:
        """
        Exports a game.

        .. note::

            Ongoing games have their last 3 moves omitted after move 5.

        :param game_id: The ID of the game.
        :type game_id: :class:`str`
        :param with_pgn_moves: Whether to include the PGN moves, or not.
        :type with_pgn_moves: Optional[:class:`bool`]
        :param with_pgn: Whether to include the full PGN, or not.
        :type with_pgn: Optional[:class:`bool`]
        :param with_pgn_tags: Whether to include the PGN tags, or not.
        :type with_pgn_tags: Optional[:class:`bool`]
        :param with_clock_comments: Whether to include clock comments, or not, when available.
        :type with_clock_comments: Optional[:class:`bool`]
        :param with_evaluation: Whether to include the analysis evaluation comments in the PGN, or not, when available.
        :type with_evaluation: Optional[:class:`bool`]
        :param with_opening: Whether to include the opening name, or not.
        :type with_opening: Optional[:class:`bool`]
        :param with_annotations: Whether to insert textual annotations in the PGN about the opening, analysis variations, mistakes, and game termination, or not.
        :type with_annotations: Optional[:class:`bool`]
        :param players: URL of a text file containing real names and ratings, to replace Lichess usernames and ratings in the PGN. =
        :type players: Optional[:class:`str`]
        """
        data = _get(
            f"/game/export/{game_id}",
            self,
            params = {
                "moves": with_pgn_moves,
                "pgnInJson": with_pgn,
                "tags": with_pgn_tags,
                "clocks": with_clock_comments,
                "evals": with_evaluation,
                "opening": with_opening,
                "literate": with_annotations,
                "players": players
                }
            )
        return Game(data)

    def export_latest_game(
        self,
        username: str,
        *,
        with_pgn_moves: Optional[bool] = None,
        with_pgn: Optional[bool] = None,
        with_pgn_tags: Optional[bool] = None,
        with_clock_comments: Optional[bool] = None,
        with_evaluation: Optional[bool] = None,
        with_opening: Optional[bool] = None,
        with_annotations: Optional[bool] = None,
        players: Optional[str] = None
        ) -> Game:
        """
        Exports the ongoing game, or the last game played, of a user.

        .. note::

            If the game is ongoing, the last 3 moves are omitted.

        :param username: The username of the user.
        :type username: :class:`str`
        :param with_pgn_moves: Whether to include the PGN moves, or not.
        :type with_pgn_moves: Optional[:class:`bool`]
        :param with_pgn: Whether to include the full PGN, or not.
        :type with_pgn: Optional[:class:`bool`]
        :param with_pgn_tags: Whether to include the PGN tags, or not.
        :type with_pgn_tags: Optional[:class:`bool`]
        :param with_clock_comments: Whether to include clock comments, or not, when available.
        :type with_clock_comments: Optional[:class:`bool`]
        :param with_evaluation: Whether to include the analysis evaluation comments in the PGN, or not, when available.
        :type with_evaluation: Optional[:class:`bool`]
        :param with_opening: Whether to include the opening name, or not.
        :type with_opening: Optional[:class:`bool`]
        :param with_annotations: Whether to insert textual annotations in the PGN about the opening, analysis variations, mistakes, and game termination, or not.
        :type with_annotations: Optional[:class:`bool`]
        :param players: URL of a text file containing real names and ratings, to replace Lichess usernames and ratings in the PGN. =
        :type players: Optional[:class:`str`]
        """
        data = _get(
            f"/api/user/{username}/current-game",
            self,
            params = {
                "moves": with_pgn_moves,
                "pgnInJson": with_pgn,
                "tags": with_pgn_tags,
                "clocks": with_clock_comments,
                "evals": with_evaluation,
                "opening": with_opening,
                "literate": with_annotations,
                "players": players
                }
            )
        return Game(data)

    def export_user_games(
        self,
        username: str,
        *,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: Optional[int] = None,
        opponent: Optional[str] = None,
        rated: Optional[bool] = None,
        performances: Optional[List[Literal["ultraBullet" ,"bullet" ,"blitz" ,"rapid" ,"classical" ,"correspondence" ,"chess960" ,"crazyhouse" ,"antichess" ,"atomic" ,"horde" ,"kingOfTheHill" ,"racingKings" ,"threeCheck"]]] = None,
        color: Optional[Literal["white", "black"]] = None,
        analysed: Optional[bool] = None,
        with_pgn_moves: Optional[bool] = None,
        with_pgn: Optional[bool] = None,
        with_pgn_tags: Optional[bool] = None,
        with_clock_comments: Optional[bool] = None,
        with_evaluation: Optional[bool] = None,
        with_opening: Optional[bool] = None,
        with_ongoing: Optional[bool] = None,
        with_finished: Optional[bool] = None,
        with_annotations: Optional[bool] = None,
        players: Optional[str] = None,
        reverse: Optional[bool] = None
        ) -> Iterator[Game]:
        """
        Exports all games of a user.

        .. note::

            Games are sorted in reverse chronological order (most recent first).

        :param username: The username of the user.
        :type username: :class:`str`
        :param since: Games played since this timestamp.
        :type since: Optional[:class:`datetime`]
        :param until: Games played until this timestamp.
        :type until: Optional[:class:`datetime`]
        :param limit: The maximum number of games to include.
        :type limit: Optional[:class:`int`]
        :param opponent: The username of the opponent.
        :type opponent: Optional[:class:`str`]
        :param rated: Whether to  only include rated games, or not.
        :type rated: Optional[:class:`bool`]
        :param performances: The speed or variant of the game.
        :type performances: Optional[List[Literal["ultraBullet" ,"bullet" ,"blitz" ,"rapid" ,"classical" ,"correspondence" ,"chess960" ,"crazyhouse" ,"antichess" ,"atomic" ,"horde" ,"kingOfTheHill" ,"racingKings" ,"threeCheck"]]]
        :param color: The color played by the user.
        :type color: Optional[Literal["white", "black"]]
        :param analysed: Whether to only include games with a computer analysis available, or not.
        :type analysed: Optional[:class:`bool`]
        :param with_pgn_moves: Whether to include the PGN moves, or not.
        :type with_pgn_moves: Optional[:class:`bool`]
        :param with_pgn: Whether to include the full PGN, or not.
        :type with_pgn: Optional[:class:`bool`]
        :param with_pgn_tags: Whether to include the PGN tags, or not.
        :type with_pgn_tags: Optional[:class:`bool`]
        :param with_clock_comments: Whether to include clock comments, or not, when available.
        :type with_clock_comments: Optional[:class:`bool`]
        :param with_evaluation: Whether to include the analysis evaluation comments in the PGN, or not, when available.
        :type with_evaluation: Optional[:class:`bool`]
        :param with_opening: Whether to include the opening name, or not.
        :type with_opening: Optional[:class:`bool`]
        :param ongoing: Whether to include ongoing games, or not.
        :type ongoing: Optional[:class:`bool`]
        :param finished: Whether to include finished games, or not.
        :type finished: Optional[:class:`bool`]
        :param with_annotations: Whether to insert textual annotations in the PGN about the opening, analysis variations, mistakes, and game termination, or not.
        :type with_annotations: Optional[:class:`bool`]
        :param players: URL of a text file containing real names and ratings, to replace Lichess usernames and ratings in the PGN. =
        :type players: Optional[:class:`str`]
        :param reverse: Whether to reverse the order of games, or not.
        :type reverse: Optional[:class:`bool`]
        """
        if since is not None and since.timestamp() < 1356998400070:
            raise ValueError("the timestamp of 'since' must be greater than or equal to 1356998400070.")
        if until is not None and until.timestamp() < 1356998400070:
            raise ValueError("the timestamp of 'until' must be greater than or equal to 1356998400070.")
        if limit is not None and limit < 1:
            raise ValueError("'limit' must be greater than or equal to 1.")
        if color is not None and color.lower() not in ("white", "black"):
            raise ValueError("'color' should be either 'white' or 'black'.")
        if performances is not None and not {item.lower() for item in performances}.issubset({"ultrabullet", "bullet", "blitz", "rapid", "classical", "correspondence", "chess960", "crazyhouse", "antichess", "atomic", "horde", "kingofthehill", "racingkings", "threecheck"}):
            raise ValueError("an element of 'performances' is not a valid speed or variant.")

        sort = None
        if reverse is True:
            sort = "dateAsc"
        elif reverse is False:
            sort = "dateDesc"

        response = _get(
            f"/api/games/user/{username}",
            self,
            params = {
                "since": since.timestamp() if since else None,
                "until": until.timestamp() if until else None,
                "max": limit,
                "vs": opponent,
                "rated": rated,
                "perfType": ",".join(performances) if performances else None,
                "color": color,
                "analysed": analysed,
                "moves": with_pgn_moves,
                "pgnInJson": with_pgn,
                "tags": with_pgn_tags,
                "clocks": with_clock_comments,
                "evals": with_evaluation,
                "opening": with_opening,
                "ongoing": with_ongoing,
                "finished": with_finished,
                "literate": with_annotations,
                "players": players,
                "sort": sort
                },
            ndjson = True,
            stream = True
            )

        for item in response.iter_lines():
            yield Game(loads(item.decode("utf-8")))

    def export_games(
        self,
        game_ids: List[str],
        *,
        with_pgn_moves: Optional[bool] = None,
        with_pgn: Optional[bool] = None,
        with_pgn_tags: Optional[bool] = None,
        with_clock_comments: Optional[bool] = None,
        with_evaluation: Optional[bool] = None,
        with_opening: Optional[bool] = None,
        with_annotations: Optional[bool] = None,
        players: Optional[str] = None
        ) -> List[Game]:
        """
        Exports up to 300 games by their IDs.

        .. note::

            Games are sorted in reverse chronological order (most recent first).

        .. note::

            Ongoing games have their last 3 moves omitted after move 5.

        :param game_ids: A list of game IDs.
        :type game_ids: List[:class:`str`]
        :param with_pgn_moves: Whether to include the PGN moves, or not.
        :type with_pgn_moves: Optional[:class:`bool`]
        :param with_pgn: Whether to include the full PGN, or not.
        :type with_pgn: Optional[:class:`bool`]
        :param with_pgn_tags: Whether to include the PGN tags, or not.
        :type with_pgn_tags: Optional[:class:`bool`]
        :param with_clock_comments: Whether to include clock comments, or not, when available.
        :type with_clock_comments: Optional[:class:`bool`]
        :param with_evaluation: Whether to include the analysis evaluation comments in the PGN, or not, when available.
        :type with_evaluation: Optional[:class:`bool`]
        :param with_opening: Whether to include the opening name, or not.
        :type with_opening: Optional[:class:`bool`]
        :param with_annotations: Whether to insert textual annotations in the PGN about the opening, analysis variations, mistakes, and game termination, or not.
        :type with_annotations: Optional[:class:`bool`]
        :param players: URL of a text file containing real names and ratings, to replace Lichess usernames and ratings in the PGN. =
        :type players: Optional[:class:`str`]
        """
        response = _post(
            "/api/games/export/_ids",
            self,
            data = ",".join(game_ids),
            params = {
                "moves": with_pgn_moves,
                "pgnInJson": with_pgn,
                "tags": with_pgn_tags,
                "clocks": with_clock_comments,
                "evals": with_evaluation,
                "opening": with_opening,
                "literate": with_annotations,
                "players": players
                },
            ndjson = True,
            stream = True
            )
        for item in response:
            yield Game(loads(item.decode("utf-8")))

    def stream_games_among_users(self, user_ids: Set[str], *, with_current_games: Optional[bool] = None) -> Iterator[Game]:
        """
        Emits an event when a game starts or finishes among the pool of users.

        :param user_ids: The pool of users' IDs.
        :type user_ids: Set[:class:`str`]
        :param with_current_games: Whether to include the already started games, or not.
        :type with_current_games: Optional[:class:`bool`]
        """
        response = _post("/api/stream/games-by-users", self, data = ",".join(item.lower() for item in user_ids), params = {"withCurrentGames": with_current_games}, ndjson = True, stream = True)
        for item in response.iter_lines():
            yield Game(loads(item.decode("utf-8")))

    def stream_games(self, game_ids: List[str], stream_id: str) -> Iterator[Game]:
        """
        First outputs the games that already exists, then emits an event each time a game is started or finished.

        :param game_ids: The list of game IDs.
        :type game_ids: List[:class:`str`]
        :param stream_id: Arbitrary stream ID that you can later use to add game IDs to the stream.
        :type stream_id: :class:`str`
        """
        response = _post(f"/api/stream/games/{stream_id}", self, data = ",".join(game_ids), ndjson = True, stream = True)
        for item in response.iter_lines():
            yield Game(loads(item.decode("utf-8")))

    def on_game_status_change(self, user_ids: Set[str], *, with_current_games: Optional[bool] = None) -> Callable:
        """
        Event that is called when a game starts or finishes among the pool of users.

        :param user_ids: The pool of users.
        :type user_ids: Set[:class:`str`]
        :param with_current_games: Whether to include the already started games, or not.
        :type with_current_games: Optional[:class:`bool`]
        """
        def decorator(function: Callable):

            def process():

                response = _post("/api/stream/games-by-users", self, data = ",".join(item.lower() for item in user_ids), params = {"withCurrentGames": with_current_games}, ndjson = True, stream = True)

                for item in response.iter_lines():
                    function(game = Game(loads(item.decode("utf-8"))))

            thread = Thread(target = process)
            thread.start()

            def error():
                raise UncallableError("functions used for events are not callable.")

            return error

        return decorator

    def add_games_to_stream(self, game_ids: List[str], stream_id: str) -> None:
        """
        Adds games to an existing stream.

        :param game_ids: The list of game IDs.
        :type game_ids: List[:class:`str`]
        :param stream_id: Whether to include the already started games, or not.
        :type stream_id: :class:`str`
        """
        _post(f"/api/stream/games/{stream_id}/add", self, data = ",".join(game_ids))

    def get_ongoing_games(self, *, limit: Optional[Range[1, 50]] = None) -> List[LichessObject]:
        """
        Gets ongoing games of the logged in user.

        .. note::

            The most urgent games are listed first.

        :param limit: The maximum number of games to fetch.
        :type game_ids: Optional[:class:`int`]
        """
        if limit is not None and limit not in Range[1, 50]:
            raise ValueError("'limit' should be greater than or equal to 1 and less than or equal to 50.")
        data = _get("/api/account/playing", self)
        return [LichessObject(item) for item in data["nowPlaying"]]

    def stream_game_moves(self, game_id: str) -> List[Union[Game, LichessObject]]:
        """
        Emits an event when a move is made.

        .. note::

            After move 5, the stream intentionally remains 3 moves behind the game status, to prevent cheat bots from using this API.

        .. note::

            No more than 8 game streams can be opened at the same time from the same IP address.

        :param game_id: The game ID.
        :type game_id: :class:`str`
        """
        response = _get(f"/api/stream/game/{game_id}", self, ndjson = True, stream = True)
        for item in response.iter_lines():
            try:
                yield Game(loads(item.decode("utf-8")))
            except KeyError:
                yield LichessObject(loads(item.decode("utf-8")))

    def on_game_move(self, game_id: str) -> Callable:
        """
        Emits an event when a move is made.

        .. note::

            After move 5, the stream intentionally remains 3 moves behind the game status, to prevent cheat bots from using this API.

        .. note::

            No more than 8 game streams can be opened at the same time from the same IP address.

        :param game_id: The game ID.
        :type game_id: :class:`str`
        """
        def decorator(function: Callable):

            def process():

                response = _get(f"/api/stream/game/{game_id}", self, ndjson = True, stream = True)

                run = False
                for item in response.iter_lines():
                    data = loads(item.decode("utf-8"))
                    if "id" in data.keys():
                        last_move = data["lastMove"]
                    elif "lm" in data.keys():
                        if run:
                            function(move = LichessObject(data))
                        if last_move == data["lm"]:
                            run = True

            thread = Thread(target = process)
            thread.start()

            def error():
                raise UncallableError("functions used for events are not callable.")

            return error

        return decorator

    def import_game(self, pgn: str) -> LichessObject:
        """
        Imports a game using its PGN.

        :param pgn: The PGN.
        :type pgn: :class:`str`
        """
        data = _post("/api/import", self, data = pgn)
        return LichessObject(data)

    def get_tv_games(self) -> TvGamesList:
        """
        Gets current TV games.
        """
        data = _get("/api/tv/channels", self)
        return TvGamesList(data)

    def stream_tv_game(self) -> Iterator[LichessObject]:
        """
        Streams the current TV game.
        """
        response = _get("/api/tv/feed", self, ndjson = True, stream = True)
        for item in response.iter_lines():
            yield LichessObject(loads(item.decode("utf-8")))

    def on_new_tv_game(self, function: Callable) -> Callable:
        """
        Event that is called when a new game is displayed on TV.
        """
        def process():

            response = _get("/api/tv/feed", self, ndjson = True, stream = True)

            for item in response.iter_lines():
                data = loads(item.decode("utf-8"))
                if "id" in data["d"].keys():
                    function(game = LichessObject(data))

        thread = Thread(target = process)
        thread.start()

        def error():
            raise UncallableError("functions used for events are not callable.")

        return error

    def get_tv_channel_games(
        self,
        channel: str,
        *,
        number: Optional[Range[1, 30]] = None,
        with_pgn_moves: Optional[bool] = None,
        with_pgn: Optional[bool] = None,
        with_pgn_tags: Optional[bool] = None,
        with_clock_comments: Optional[bool] = None,
        with_opening: Optional[bool] = None,
        ) -> Iterator[Game]:
        """
        Gets a list of ongoing TV games for a given channel.

        :param channel: The name of the channel in camel case.
        :type channel: :class:`str`
        :param number: The number of games to fetch.
        :type number: Optional[Range[1, 30]]
        :param with_pgn_moves: Whether to include the PGN moves, or not.
        :type with_pgn_moves: Optional[:class:`bool`]
        :param with_pgn: Whether to include the full PGN, or not.
        :type with_pgn: Optional[:class:`bool`]
        :param with_pgn_tags: Whether to include the PGN tags, or not.
        :type with_pgn_tags: Optional[:class:`bool`]
        :param with_clock_comments: Whether to include clock comments, or not, when available.
        :type with_clock_comments: Optional[:class:`bool`]
        :param with_opening: Whether to include the opening name, or not.
        :type with_opening: Optional[:class:`bool`]
        """
        if number not in Range[1, 30]:
            raise ValueError("'number' must be greater than or equal to 1 and less than or equal to 30.")
        response = _get(
            f"/api/tv/{channel}",
            self,
            params = {
                "nb": number,
                "moves": with_pgn_moves,
                "pgnInJson": with_pgn,
                "tags": with_pgn_tags,
                "clocks": with_clock_comments,
                "opening": with_opening,
                },
            ndjson = True,
            stream = True
            )
        for item in response.iter_lines():
            yield Game(loads(item.decode("utf-8")))

    def get_daily_puzzle(self) -> Iterator[LichessObject]:
        """
        Gets the daily puzzle.
        """
        response = _get("/api/puzzle/daily", self, ndjson = True, stream = True)
        for item in response.iter_lines():
            yield LichessObject(loads(item.decode("utf-8")))

    def get_puzzle(self, puzzle_id: str) -> Iterator[LichessObject]:
        """
        Gets a puzzle using its ID.

        :param puzzle_id: The ID of the puzzle.
        :type puzzle_id: :class:`str`
        """
        response = _get(f"/api/puzzle/{puzzle_id}", self, ndjson = True, stream = True)
        for item in response.iter_lines():
            yield LichessObject(loads(item.decode("utf-8")))

    def get_puzzle_activity(self, *, limit: Optional[int] = None) -> Iterator[Puzzle]:
        """
        Gets the puzzle activity of the logged in user.

        :param limit: The maximum number of puzzles to fetch.
        :type limit: Optional[:class:`int`]
        """
        if limit < 1:
            raise ValueError("'limit' must be greater than or equal to 1.")
        response = _get("/api/puzzle/activity", self, params = {"max": limit}, ndjson = True, stream = True)
        for item in response.iter_lines():
            yield Puzzle(loads(item.decode("utf-8")))

    def get_puzzle_dashboard(self, days: int) -> LichessObject:
        """
        Gets the puzzle dashboard of the logged in user.

        :param days: The number of days to look back when aggregating puzzle results.
        :type days: :class:`int`
        """
        if days < 1:
            raise ValueError("'days' must be greater than or equal to 1.")
        data = _get(f"/api/puzzle/dashboard/{days}", self)
        return LichessObject(data)

    def get_storm_dashboard(self, username: str, *, days: Optional[Range[0, 365]]) -> LichessObject:
        """
        Gets the storm dashboard of a user.

        :param username: The username of the user.
        :type username: :class:`str`
        :param days: The number of days of history to return.
        :type days: Optional[Range[0, 365]]

        .. note::

            Set ``days`` to ``0`` if you only care about high scores.
        """
        if days not in Range[0, 365]:
            raise ValueError("'days' must be greater than or equal to 0 and less than or equal to 365.")
        data = _get(f"/api/storm/dashboard/{username}", self, params = {"days": days})
        return LichessObject(data)

    def create_puzzle_race(self) -> LichessObject:
        """
        Creates a new private puzzle race.

        ..note ::

            The user who creates the race must join the race page, and manually start the race when enough players have joined.
        """
        data = _post("/api/racer", self)
        return LichessObject(data)

    def get_swiss_tournaments(self, team_id: str, *, limit: Optional[int] = None) -> Iterator[SwissTournament]:
        """
        Gets all the Swiss tournaments of a team.

        .. note::

            Tournaments are sorted in reverse chronological order (most recent first).

        :param team_id: The ID of the team.
        :type team_id: :class:`str`
        :param limit: The maximum number of tournaments to fetch.
        :type limit: Optional[:class:`int`]
        """
        if limit < 1:
            raise ValueError("'limit' must be greater than or equal to 1.")
        response = _get(f"/api/team/{team_id}/swiss", self, params = {"max": limit}, ndjson = True, stream = True)
        for item in response.iter_lines():
            yield SwissTournament(loads(item.decode("utf-8")))

    def get_team(self, team_id: str) -> LichessObject:
        """
        Gets information about a single team.

        :param team_id: The ID of the team.
        :type team_id: :class:`str`
        """
        data = _get(f"/api/team/{team_id}", self)
        return LichessObject(data)

    def get_popular_teams(self, *, page: Optional[int] = None) -> LichessObject:
        """
        Gets popular teams.

        :param page: The page number.
        :type page: Optional[:class:`int`]
        """
        data = _get("/api/team/all", self, params = {"page": page})
        return LichessObject(data)

    def get_user_teams(self, username: str) -> List[LichessObject]:
        """
        Gets a user's teams.

        :param username: The user's username.
        :type username: :class:`str`
        """
        data = _get(f"/api/team/all/of/{username}", self)
        return [LichessObject(item) for item in data]

    def search_team(self, *, text: Optional[str] = None, page: Optional[int] = None) -> LichessObject:
        """
        Searches for teams.

        :param text: The query text.
        :type text: Optional[:class:`str`]
        :param page: The page number.
        :type page: Optional[:class:`int`]
        """
        data = _get("/api/team/search", self, params = {"text": text, "page": page})
        return LichessObject(data)

    def get_arena_tournaments(self, team_id: str, *, limit: Optional[int] = None) -> Iterator[ArenaTournament]:
        """
        Gets all the Arena tournaments of a team.

        .. note::

            Tournaments are sorted in reverse chronological order (most recent first).

        :param team_id: The ID of the team.
        :type team_id: :class:`str`
        :param limit: The maximum number of tournaments to fetch.
        :type limit: Optional[:class:`int`]
        """
        if limit < 1:
            raise ValueError("'limit' must be greater than or equal to 1.")
        response = _get(f"/api/team/{team_id}/arena", self, params = {"max": limit}, ndjson = True, stream = True)
        for item in response.iter_lines():
            yield ArenaTournament(loads(item.decode("utf-8")))

    def join_team(self, team_id: str, *, message: Optional[str] = None, password: Optional[str] = None) -> None:
        """
        Joins a team.

        :param team_id: The ID of the team.
        :type team_id: :class:`str`
        :param message: The request message, if the team requires one.
        :type message: Optional[:class:`str`]
        :param password: The password, if the team requires one.
        :type password: Optional[:class:`str`]
        """
        _post(f"/team/{team_id}/join", self, params = {"message": message, "password": password})

    def leave_team(self, team_id: str) -> None:
        """
        Leaves a team.

        :param team_id: The ID of the team.
        :type team_id: :class:`str`
        """
        _post(f"/team/{team_id}/quit", self)

    def get_join_requests(self, team_id: str) -> RequestList:
        """
        Gets pending join requests of a team.

        :param team_id: The ID of the team.
        :type team_id: :class:`str`
        """
        data = _get(f"/api/team/{team_id}/requests", self)
        return RequestList(data)

    def accept_join_request(self, team_id: str, user_id: str) -> bool:
        """
        Accepts a user's join request for a team.

        :param team_id: The ID of the team.
        :type team_id: :class:`str`
        :param user_id: The ID of the user.
        :type user_id: :class:`str`
        """
        data = _get(f"/api/team/{team_id}/request/{user_id}/accept", self)
        return data["ok"]

    def decline_join_request(self, team_id: str, user_id: str) -> bool:
        """
        Declines a user's join request for a team.

        :param team_id: The ID of the team.
        :type team_id: :class:`str`
        :param user_id: The ID of the user.
        :type user_id: :class:`str`
        """
        data = _get(f"/api/team/{team_id}/request/{user_id}/decline", self)
        return data["ok"]

    def kick_team_member(self, team_id: str, user_id: str) -> bool:
        """
        Kicks a user from a team.

        :param team_id: The ID of the team.
        :type team_id: :class:`str`
        :param user_id: The ID of the user.
        :type user_id: :class:`str`
        """
        data = _get(f"/api/team/{team_id}/kick/{user_id}", self)
        return data["ok"]

    def message_team_members(self, team_id: str, message: Optional[str] = None) -> bool:
        """
        Messages all members of a team.

        :param team_id: The ID of the team.
        :type team_id: :class:`str`
        :param message: The message to post.
        :type message: Optional[:class:`str`]
        """
        data = _get(f"/api/team/{team_id}/pm-all", self, params = {"message": message})
        return data["ok"]

    def stream_incoming_events(self) -> Iterator[LichessObject]:
        """
        Streams the logged in user's incoming events.

        .. note::

            When the stream opens, all current challenges and games are sent.
        """
        response = _get("/api/stream/event", self, ndjson = True, stream = True)
        for item in response.iter_lines():
            try:
                yield LichessObject(loads(item.decode("utf-8")))
            except JSONDecodeError:
                pass

    def on_new_event(self, function: Callable) -> Callable:
        """
        Event that is called when there is a new incoming event.

        .. note::

            When the stream opens, all current challenges and games are sent.
        """
        def process():

            response = _get("/api/stream/event", self, ndjson = True, stream = True)

            for item in response.iter_lines():
                try:
                    function(event = LichessObject(loads(item.decode("utf-8"))))
                except JSONDecodeError:
                    pass

        thread = Thread(target = process)
        thread.start()

        def error():
            raise UncallableError("functions used for events are not callable.")

        return error

    def create_seek(
            self,
            *,
            rated: Optional[bool] = None,
            time: Optional[Range[0, 180]] = None,
            increment: Optional[Range[0, 180]] = None,
            days: Optional[Literal[1, 2, 3, 5, 7, 10, 14]] = None,
            variant: Optional[Literal["standard" ,"chess960" ,"crazyhouse" ,"antichess" ,"atomic" ,"horde" ,"kingOfTheHill" ,"racingKings" ,"threeCheck", "fromPosition"]] = None,
            color: Optional[Literal["random", "white", "black"]] = None,
            rating_range: Optional[Range] = None
            ) -> Iterator[LichessObject]:
        """
        Creates a public seek to start a game with a random player.

        .. note::

            Make sure to also have the incoming events stream open, to be notified when a game starts.

        :param rated: Whether the game is rated, and impacts player ratings, or casual.
        :type rated: Optional[:class:`bool`]
        :param time: The initial clock time, in minutes.
        :type time: Optional[Range[0, 180]]

        .. note::

            This is required for real-time seeks.

        :param increment: The clock incremenet, in seconds.
        :type increment: Optional[Range[0, 180]]

        .. note::

            This is required for real-time seeks.

        :param days: The number of days per turn.
        :type days: Optional[Literal[1, 2, 3, 5, 7, 10, 14]]

        .. note::

            This is required for correspondence seeks.

        :param variant: The game variant.
        :type variant: Optional[Literal["ultraBullet" ,"bullet" ,"blitz" ,"rapid" ,"classical" ,"correspondence" ,"chess960" ,"crazyhouse" ,"antichess" ,"atomic" ,"horde" ,"kingOfTheHill" ,"racingKings" ,"threeCheck"]]
        :param color: The color to play with.
        :type color: Optional[Literal["random", "white", "black"]]
        :param rating_range: The rating range of potential opponents.
        :type rating_range: Optional[Range]

        .. warn::

            This is better left empty.
        """
        if time not in Range[0, 180]:
            raise ValueError("'time' must be greater than or equal to 0 and less than or equal to 180.")
        if increment not in Range[0, 180]:
            raise ValueError("'increment' must be greater than or equal to 0 and less than or equal to 180.")
        thread = Thread(target = lambda: _post("/api/board/seek", self, params = {"rated": rated, "time": time, "increment": increment, "days": days, "variant": variant, "color": color, "rating_range": f"{rating_range[0]}-{rating_range[-1]}" if rating_range else None},  text = True))
        thread.start()

    def stream_board_state(self, game_id: str) -> Iterator[Union[Game, LichessObject]]:
        """
        Streams changes in the state of a game being played.

        :param game_id: The ID of the game.
        :type game_id: :class:`str`
        """
        response = _get(f"/api/board/game/stream/{game_id}", self, ndjson = True, stream = True)
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

                response = _get(f"/api/board/game/stream/{game_id}", self, ndjson = True, stream = True)

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
        data = _post(f"/api/board/game/{game_id}/move/{move}", self, data = {"offeringDraw": with_draw_offering})
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
        data = _post(f"/api/board/game/{game_id}/chat", self, data = {"room": room, "text": text})
        return data["ok"]

    def get_game_chat(self, game_id: str) -> List[LichessObject]:
        """
        Fetches a game's chat history.

        :param game_id: The ID of the game.
        :type game_id: :class:`str`
        """
        data = _get(f"/api/board/game/{game_id}/chat", self, ndjson = True)
        return [LichessObject(item) for item in data]

    def abort_game(self, game_id: str) -> bool:
        """
        Aborts an ongoing game.

        :param game_id: The ID of the game.
        :type game_id: :class:`str`
        """
        data = _post(f"/api/board/game/{game_id}/abort", self)
        return data["ok"]

    def resign_game(self, game_id: str) -> bool:
        """
        Resigns an ongoing game.

        :param game_id: The ID of the game.
        :type game_id: :class:`str`
        """
        data = _post(f"/api/board/game/{game_id}/resign", self)
        return data["ok"]

    def handle_draw_offer(self, game_id: str, accept: bool) -> bool:
        """
        Handles (or creates) a draw offer from an ongoing game.

        :param game_id: The ID of the game.
        :type game_id: :class:`str`
        :param accept: Whether to accept (or to create) the draw offer or not.
        :type accept: :class:`bool`
        """
        accept = ["no", "yes"][accept]
        data = _post(f"/api/board/game/{game_id}/draw/{accept}", self)
        return data["ok"]

    def handle_takeback_offer(self, game_id: str, accept: bool) -> bool:
        """
        Handles (or creates) a takeback offer from an ongoing game.

        :param game_id: The ID of the game.
        :type game_id: :class:`str`
        :param accept: Whether to accept (or to create) the takeback or not.
        :type accept: :class:`bool`
        """
        accept = ["no", "yes"][accept]
        data = _post(f"/api/board/game/{game_id}/takeback/{accept}", self)
        return data["ok"]

    def claim_victory(self, game_id: str) -> bool:
        """
        Claim victory when the opponent has left an ongoing game.

        :param game_id: The ID of the game.
        :type game_id: :class:`str`
        """
        data = _post(f"/api/board/game/{game_id}/claim-victory", self)
        return data["ok"]

    def berserk_game(self, game_id: str) -> bool:
        """
        Berserks a tournament game, which halves the clock time, grants an extra point upon winning.

        .. note::
            This feature is only available in arena tournaments that allow berserks, and before each player has made a move.

        :param game_id: The ID of the game.
        :type game_id: :class:`str`
        """
        data = _post(f"/api/board/game/{game_id}/berserk", self)
        return data["ok"]

    def get_online_bots(self) -> Iterator[Player]:
        """
        Fetches a list of online bots.
        """
        response = _get("/api/bot/online", self, ndjson = True, stream = True)
        for item in response.iter_lines():
            yield Player(loads(item.decode("utf-8")))

    def upgrade_to_bot_account(self) -> bool:
        """
        Upgrades the account of the logged in user to a Bot account.

        .. warn::
            This action is irrevocable.

        .. note::
            The account cannot have played any game before becoming a Bot account.
        """
        data = _post("/api/bot/account/upgrade", self)
        return data["ok"]

    def get_challenges(self) -> LichessObject:
        """
        Gets a list of challenges created by or target at the logged in user.
        """
        data = _get("/api/challenge", self)
        return LichessObject(data)

    def create_challenge(
            self,
            username: str,
            *,
            rated: Optional[bool] = None,
            time: Optional[Range[0, 10800]] = None,
            increment: Optional[Range[0, 180]] = None,
            days: Optional[Literal[1, 2, 3, 5, 7, 10, 14]] = None,
            color: Optional[Literal["random", "white", "black"]] = None,
            variant: Optional[Literal["standard" ,"chess960" ,"crazyhouse" ,"antichess" ,"atomic" ,"horde" ,"kingOfTheHill" ,"racingKings" ,"threeCheck", "fromPosition"]] = None,
            fen: Optional[str] = None,
            keep_alive: Optional[bool] = None,
            acceptance_token: Optional[str] = None,
            message: Optional[str] = None,
            rules: Optional[Literal["noAbort", "noRematch", "noGiveTime", "noClaimWin"]] = None
            ) -> None:
        """
        Challenges a user to play.

        .. note::

            Make sure to also have the incoming events stream open, to be notified when the game starts.

        :param username: The username of the player.
        :type username: :class:`str`
        :param rated: Whether the game is rated, and impacts player ratings, or casual.
        :type rated: Optional[:class:`bool`]
        :param time: The initial clock time, in seconds.
        :type time: Optional[Range[0, 10800]]

        .. note::

            If empty, a correspondence game is created.

        :param increment: The clock incremenet, in seconds.
        :type increment: Optional[Range[0, 180]]

        .. note::

            If empty, a correspondence game is created.

        :param days: The number of days per turn.
        :type days: Optional[Literal[1, 2, 3, 5, 7, 10, 14]]

        .. note::

            This is required for correspondence seeks.

        :param variant: The game variant.
        :type variant: Optional[Literal["ultraBullet" ,"bullet" ,"blitz" ,"rapid" ,"classical" ,"correspondence" ,"chess960" ,"crazyhouse" ,"antichess" ,"atomic" ,"horde" ,"kingOfTheHill" ,"racingKings" ,"threeCheck"]]
        :param color: The color to play with.
        :type color: Optional[Literal["random", "white", "black"]]
        :param fen: The custom initial position using FEN.
        :type fen: Optional[:class:`str`]

        .. note::

            The variant must be "standard", "fromPosition", or "chess960", and the game cannot be rated.
            Castling moves will use UCI_Chess960 notation.

        :param keep_alive: Whether to keep the challenge alive infinitely or not.
        :type keep_alive: Optional[:class:`bool`]

        .. note::

            If set to ``False`` or if left empty, the response is not streamed, and the challenge expires after 20 seconds if not accepted by the opponent.

        :param acceptance_token: The token of the receiving user, which access to the ``challenge:write`` scope.
        :type acceptance_token: Optional[:class:`bool`]

        .. note::

            Providing a valid token immediately accepts the challenge and starts the game.

        :param message: The message that is sent to each player, when the game starts.
        :type message: Optional[:class:`str`]

        .. warn::

            The ``acceptance_token`` parameter must be set to ``True`` if you want to set this.

        :param rules: Extra games properties, restricting one's capabilities during the game.
        :type rules: Optional[Literal["noAbort", "noRematch", "noGiveTime", "noClaimWin"]]
        """
        if time not in Range[0, 10800]:
            raise ValueError("'time' must be greater than or equal to 0 and less than or equal to 10800.")
        if increment not in Range[0, 180]:
            raise ValueError("'increment' must be greater than or equal to 0 and less than or equal to 180.")
        if message is not None and acceptance_token is None:
            raise ValueError("'message' can only be set if 'acceptance_token' is provided.")

        result = None
        def post_and_save():
            nonlocal result
            result = _post(f"/api/challenge/{username}", self, params = {"rated": rated, "clock.limit": time, "clock.increment": increment, "days": days, "color": color, "variant": variant, "fen": fen, "keepAliveStream": keep_alive, "acceptByToken": acceptance_token, "message": message, "rules": rules})

        thread = Thread(target = post_and_save)
        thread.start()
        return LichessObject(result)

    def accept_challenge(self, challenge_id: str) -> bool:
        """
        Accepts an incoming challenge.

        :param challenge_id: The ID of the challenge.
        :type challenge_id: :class:`str`
        """
        data = _post(f"/api/challenge/{challenge_id}/accept", self)
        return data["ok"]

    def decline_challenge(self, challenge_id: str, *, reason: Optional[Literal["generic", "later", "tooFast", "tooSlow", "timeControl", "rated", "casual", "standard", "variant", "noBot", "onlyBot"]] = None) -> bool:
        """
        Declines an incoming challenge.

        :param challenge_id: The ID of the challenge.
        :type challenge_id: :class:`str`
        :param reason: The reason for the rejection.
        :type reason: Optional[Literal["generic", "later", "tooFast", "tooSlow", "timeControl", "rated", "casual", "standard", "variant", "noBot", "onlyBot"]]
        """
        data = _post(f"/api/challenge/{challenge_id}/decline", self, params = {"reason": reason})
        return data["ok"]

    def cancel_challenge(self, challenge_id: str, *, opponent_token: Optional[str] = None) -> bool:
        """
        Cancels an incoming challenge.

        :param challenge_id: The ID of the challenge.
        :type challenge_id: :class:`str`
        :param opponent_token: The opponents API token with the ``challenge:write`` scope enabled.
        :type opponent_token: Optional[:class:`str`]

        .. note::
            If provided, the game can be cancelled even if both players have made a move.
        """
        data = _post(f"/api/challenge/{challenge_id}/cancel", self, params = {"opponentToken": opponent_token})
        return data["ok"]

    def challenge_ai(
            self,
            *,
            level: Range[1, 8] = None,
            rated: Optional[bool] = None,
            time: Optional[Range[0, 10800]] = None,
            increment: Optional[Range[0, 60]] = None,
            days: Optional[Literal[1, 2, 3, 5, 7, 10, 14]] = None,
            color: Optional[Literal["random", "white", "black"]] = None,
            variant: Optional[Literal["standard" ,"chess960" ,"crazyhouse" ,"antichess" ,"atomic" ,"horde" ,"kingOfTheHill" ,"racingKings" ,"threeCheck", "fromPosition"]] = None,
            fen: Optional[str] = None,
            ) -> Game:
        """
        Starts a game with the Lichess AI.

        .. note::

            Make sure to also have the incoming events stream open, to be notified when the game starts.

        :param level: The strength of the AI.
        :type level: Optional[Range[1, 8]]
        :param rated: Whether the game is rated, and impacts player ratings, or casual.
        :type rated: Optional[:class:`bool`]
        :param time: The initial clock time, in seconds.
        :type time: Optional[Range[0, 10800]]

        .. note::

            If empty, a correspondence game is created.

        :param increment: The clock incremenet, in seconds.
        :type increment: Optional[Range[0, 60]]

        .. note::

            If empty, a correspondence game is created.

        :param days: The number of days per turn.
        :type days: Optional[Literal[1, 2, 3, 5, 7, 10, 14]]

        .. note::

            This is required for correspondence seeks.

        :param variant: The game variant.
        :type variant: Optional[Literal["ultraBullet" ,"bullet" ,"blitz" ,"rapid" ,"classical" ,"correspondence" ,"chess960" ,"crazyhouse" ,"antichess" ,"atomic" ,"horde" ,"kingOfTheHill" ,"racingKings" ,"threeCheck"]]
        :param color: The color to play with.
        :type color: Optional[Literal["random", "white", "black"]]
        :param fen: The custom initial position using FEN.
        :type fen: Optional[:class:`str`]

        .. note::

            The variant must be "standard", "fromPosition", or "chess960", and the game cannot be rated.
            Castling moves will use UCI_Chess960 notation.
        """
        if level not in Range[1, 8]:
            raise ValueError("'level' must be greater than or equal to 1 and less than or equal to 8.")
        if time not in Range[0, 10800]:
            raise ValueError("'time' must be greater than or equal to 0 and less than or equal to 10800.")
        if increment not in Range[0, 60]:
            raise ValueError("'increment' must be greater than or equal to 0 and less than or equal to 60.")

        result = None
        def post_and_save():
            nonlocal result
            result = _post("/api/challenge/ai", self, params = {"level": level, "rated": rated, "clock.limit": time, "clock.increment": increment, "days": days, "color": color, "variant": variant, "fen": fen})

        thread = Thread(target = post_and_save)
        thread.start()
        return LichessObject(result)

    def create_open_challenge(
            self,
            *,
            rated: Optional[bool] = None,
            time: Optional[Range[0, 10800]] = None,
            increment: Optional[Range[0, 60]] = None,
            days: Optional[Literal[1, 2, 3, 5, 7, 10, 14]] = None,
            variant: Optional[Literal["standard" ,"chess960" ,"crazyhouse" ,"antichess" ,"atomic" ,"horde" ,"kingOfTheHill" ,"racingKings" ,"threeCheck", "fromPosition"]] = None,
            fen: Optional[str] = None,
            rules: Optional[Literal["noAbort", "noRematch", "noGiveTime", "noClaimWin"]] = None,
            users: Optional[Tuple[str, str]] = None
            ) -> None:
        """
        Creates an open-ended challenge that any two players can join.

        .. note::

            These challenges expire after 24 hours.

        :param rated: Whether the game is rated, and impacts player ratings, or casual.
        :type rated: Optional[:class:`bool`]
        :param time: The initial clock time, in seconds.
        :type time: Optional[Range[0, 10800]]

        .. note::

            If empty, a correspondence game is created.

        :param increment: The clock incremenet, in seconds.
        :type increment: Optional[Range[0, 60]]

        .. note::

            If empty, a correspondence game is created.

        :param days: The number of days per turn.
        :type days: Optional[Literal[1, 2, 3, 5, 7, 10, 14]]

        .. note::

            This is required for correspondence seeks.

        :param variant: The game variant.
        :type variant: Optional[Literal["ultraBullet" ,"bullet" ,"blitz" ,"rapid" ,"classical" ,"correspondence" ,"chess960" ,"crazyhouse" ,"antichess" ,"atomic" ,"horde" ,"kingOfTheHill" ,"racingKings" ,"threeCheck"]]
        :param fen: The custom initial position using FEN.
        :type fen: Optional[:class:`str`]

        .. note::

            The variant must be "standard", "fromPosition", or "chess960", and the game cannot be rated.
            Castling moves will use UCI_Chess960 notation.

        :param keep_alive: Whether to keep the challenge alive infinitely or not.
        :type keep_alive: Optional[:class:`bool`]

        .. note::

            If set to ``False`` or if left empty, the response is not streamed, and the challenge expires after 20 seconds if not accepted by the opponent.

        :param rules: Extra games properties, restricting one's capabilities during the game.
        :type rules: Optional[Literal["noAbort", "noRematch", "noGiveTime", "noClaimWin"]]
        :param users: The usernames of a pair of users who will be playing the game.
        :type users: Optional[Tuple[str, str]]

        .. note::

            The first username gets the white pieces.
        """
        if time not in Range[0, 10800]:
            raise ValueError("'time' must be greater than or equal to 0 and less than or equal to 10800.")
        if increment not in Range[0, 60]:
            raise ValueError("'increment' must be greater than or equal to 0 and less than or equal to 60.")

        result = None
        def post_and_save():
            nonlocal result
            result = _post("/api/challenge/open", self, params = {"rated": rated, "clock.limit": time, "clock.increment": increment, "days": days, "variant": variant, "fen": fen, "rules": rules, "users": ",".join(users)})

        thread = Thread(target = post_and_save)
        thread.start()
        return LichessObject(result)

    def start_game_clocks(self, game_id: str, *, token_1: Optional[str] = None, token_2: Optional[str] = None) -> bool:
        """
        Starts the clocks of a game immediately, even if a player has not made a move.

        .. note::

            If the clocks have already started, this call will have no effect.

        :param game_id: The game ID.
        :type game_id: :class:`str`
        :param token_1: The token of one player.
        :type token_1: Optional[:class:`str`]
        :param token_2: The token of the other player.
        :type token_2: Optional[:class:`str`]

        .. note::

            Both tokens need to have the ``challenge:write`` scope enabled.
        """
        data = _post(f"/api/challenge/{game_id}/start-clocks", self, params = {"token1": token_1, "token2": token_2})
        return data["ok"]

    def add_time_to_clock(self, game_id: str, time: Range[1, 86400]) -> bool:
        """
        Adds extra time to the opponent's clock.

        :param game_id: The game ID.
        :type game_id: :class:`str`
        :param time: The number of seconds to add.
        :type time: Range[1, 86400]
        """
        data = _post(f"/api/round/{game_id}/add-time/{time}", self)
        return data["ok"]

    def create_challenge_tokens(self, users: List[str], description: str) -> bool:
        """
        Creates and obtains ``challenge:write`` tokens for multiple users.

        .. warn::
        
            This endpoint can only be used by Lichess administrators. It will not work if you do not have the appropriate permissions.

        .. note::

            If a similar token already exists for a user, it is reused.

        :param users: The list of usernames of users.
        :type users: List[:class:`str`]
        :param description: The description of the tokens.
        :type description: :class:`str`
        """
        data = _post("/api/token/admin-challenge", self, params = {"users": ",".join(users), "description": description})
        return LichessObject(data)
