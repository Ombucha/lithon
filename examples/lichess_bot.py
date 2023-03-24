import lichess
import stockfish

bot = lichess.Bot("token")
engine = stockfish.Stockfish("path/to/stockfish.exe")

@bot.on_new_event
def on_new_event(event):

    if event.type == "challenge" and event.challenge.challenger.id != bot.get_profile().id:
        bot.accept_challenge(event.challenge.id)

    if event.type == "gameStart":                

        @bot.on_new_game_state(event.game.full_id)
        def on_new_game_state(state):
            if state.type == "gameState":
                moves = state.moves.split()
                stockfish.set_position(moves)
                if state.status == "started" and ((moves % 2 == 0 and event.game.color == "white") or (moves % 2 == 1 and event.game.color == "black")):
                    best_move = engine.get_best_move()
                    bot.make_board_move(event.game.game_id, best_move)

        if event.game.is_my_turn:
            best_move = engine.get_best_move()
            bot.make_board_move(event.game.game_id, best_move)
