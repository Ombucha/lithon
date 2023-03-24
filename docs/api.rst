Usage
=====

Reading the official  `Lichess API documentation <https://lichess.org/api>`_ before working with this library is recommended.
Response schemata are not available here as they are already present at the aforementioned URL.


Client
------

.. autoclass:: lichess.Client
    :members:
    :exclude-members: on_game_move, on_game_status_change, on_new_event, on_new_game_state, on_new_tv_game

    .. autodecorator:: lichess.Client.on_new_game_state(game_id: str)
    .. autodecorator:: lichess.Client.on_game_status_change(user_ids: Set[str], *, with_current_games: Optional[bool] = None)
    .. autodecorator:: lichess.Client.on_new_event()
    .. autodecorator:: lichess.Client.on_new_game_state(game_id: str)
    .. autodecorator:: lichess.Client.on_new_tv_game()

Bot
----

.. note::

    All methods of this class are overrides of corresponding methods in :class:`Client`.

.. autoclass:: lichess.Bot
    :members:
    :exclude-members: on_new_game_state

    .. autodecorator:: lichess.Bot.on_new_game_state(game_id: str)
