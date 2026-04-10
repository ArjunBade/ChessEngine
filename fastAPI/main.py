from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Material values (centipawns, from white's perspective)
PIECE_VALUES = {
    'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000,
    'p': -100, 'n': -320, 'b': -330, 'r': -500, 'q': -900, 'k': -20000,
}

INITIAL_BOARD = [
    ["r", "n", "b", "q", "k", "b", "n", "r"],
    ["p", "p", "p", "p", "p", "p", "p", "p"],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    ["P", "P", "P", "P", "P", "P", "P", "P"],
    ["R", "N", "B", "Q", "K", "B", "N", "R"],
]

chess_board = [row[:] for row in INITIAL_BOARD]
turn = "white"
game_over = False
game_winner = None


class Move(BaseModel):
    from_row: int
    from_col: int
    to_row: int
    to_col: int


# Move generation

def _sliding(board, row, col, directions, is_white):
    moves = []
    for dr, dc in directions:
        nr, nc = row + dr, col + dc
        while 0 <= nr < 8 and 0 <= nc < 8:
            t = board[nr][nc]
            if t == ".":
                moves.append((row, col, nr, nc))
            elif (is_white and t.islower()) or (not is_white and t.isupper()):
                moves.append((row, col, nr, nc))
                break
            else:
                break
            nr += dr
            nc += dc
    return moves


def get_piece_moves(board, row, col):
    """Pseudo-legal moves for the piece at (row, col) — does not check for leaving king in check."""
    piece = board[row][col]
    if piece == ".":
        return []
    is_white = piece.isupper()
    p = piece.lower()
    moves = []

    def reachable(nr, nc):
        if not (0 <= nr < 8 and 0 <= nc < 8):
            return False
        t = board[nr][nc]
        return t == "." or (is_white and t.islower()) or (not is_white and t.isupper())

    if p == "p":
        direction = -1 if is_white else 1
        start_row = 6 if is_white else 1
        nr = row + direction
        if 0 <= nr < 8 and board[nr][col] == ".":
            moves.append((row, col, nr, col))
            nr2 = row + 2 * direction
            if row == start_row and board[nr2][col] == ".":
                moves.append((row, col, nr2, col))
        for dc in (-1, 1):
            nr, nc = row + direction, col + dc
            if 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] != ".":
                t = board[nr][nc]
                if (is_white and t.islower()) or (not is_white and t.isupper()):
                    moves.append((row, col, nr, nc))

    elif p == "n":
        for dr, dc in ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)):
            if reachable(row + dr, col + dc):
                moves.append((row, col, row + dr, col + dc))

    elif p == "r":
        moves.extend(_sliding(board, row, col, ((0,1),(0,-1),(1,0),(-1,0)), is_white))

    elif p == "b":
        moves.extend(_sliding(board, row, col, ((1,1),(1,-1),(-1,1),(-1,-1)), is_white))

    elif p == "q":
        moves.extend(_sliding(board, row, col,
            ((0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)), is_white))

    elif p == "k":
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                if reachable(row + dr, col + dc):
                    moves.append((row, col, row + dr, col + dc))

    return moves


def get_all_pseudo_moves(board, is_white):
    moves = []
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece == "." or (piece.isupper() != is_white):
                continue
            moves.extend(get_piece_moves(board, r, c))
    return moves


# Board helpers

def apply_move(board, from_row, from_col, to_row, to_col):
    """Return a new board with the move applied (with pawn promotion to queen)."""
    b = [row[:] for row in board]
    piece = b[from_row][from_col]
    b[from_row][from_col] = "."
    b[to_row][to_col] = piece
    if piece == "P" and to_row == 0:
        b[to_row][to_col] = "Q"
    elif piece == "p" and to_row == 7:
        b[to_row][to_col] = "q"
    return b


def find_king(board, is_white):
    king = "K" if is_white else "k"
    for r in range(8):
        for c in range(8):
            if board[r][c] == king:
                return r, c
    return None


def is_in_check(board, is_white):
    pos = find_king(board, is_white)
    if not pos:
        return True
    kr, kc = pos
    for move in get_all_pseudo_moves(board, not is_white):
        if move[2] == kr and move[3] == kc:
            return True
    return False


def get_legal_moves(board, is_white):
    """Only moves that do not leave own king in check."""
    legal = []
    for move in get_all_pseudo_moves(board, is_white):
        nb = apply_move(board, *move)
        if not is_in_check(nb, is_white):
            legal.append(move)
    return legal


def get_game_status(board, is_white_turn):
    """Returns (status_string, winner_string_or_None)."""
    legal = get_legal_moves(board, is_white_turn)
    in_check = is_in_check(board, is_white_turn)
    if not legal:
        if in_check:
            winner = "black wins!" if is_white_turn else "white wins!"
            return "checkmate", winner
        return "stalemate", "draw"
    if in_check:
        return "check", None
    return "ongoing", None

# Engine — minimax with alpha-beta pruning

def evaluate(board):
    score = 0
    for row in board:
        for piece in row:
            score += PIECE_VALUES.get(piece, 0)
    return score


def minimax(board, depth, alpha, beta, maximizing):
    """
    Minimax with alpha-beta pruning.
    maximizing=True  → white's turn (maximise score)
    maximizing=False → black's turn (minimise score)
    Returns (score, best_move).
    """
    is_white = maximizing
    legal = get_legal_moves(board, is_white)

    if not legal:
        if is_in_check(board, is_white):
            # Checkmate — heavily penalise the side that is mated
            return (10000 if not maximizing else -10000), None
        return 0, None  # Stalemate

    if depth == 0:
        return evaluate(board), None

    best_move = None
    if maximizing:
        best = float("-inf")
        for move in legal:
            score, _ = minimax(apply_move(board, *move), depth - 1, alpha, beta, False)
            if score > best:
                best, best_move = score, move
            alpha = max(alpha, score)
            if beta <= alpha:
                break
        return best, best_move
    else:
        best = float("inf")
        for move in legal:
            score, _ = minimax(apply_move(board, *move), depth - 1, alpha, beta, True)
            if score < best:
                best, best_move = score, move
            beta = min(beta, score)
            if beta <= alpha:
                break
        return best, best_move


# API endpoints

@app.post("/new-game")
def new_game():
    global chess_board, turn, game_over, game_winner
    chess_board = [row[:] for row in INITIAL_BOARD]
    turn = "white"
    game_over = False
    game_winner = None
    return {"board": chess_board, "turn": turn, "status": "ongoing"}


@app.post("/make-move")
def make_move(move: Move):
    global chess_board, turn, game_over, game_winner

    if game_over:
        return {"status": "game_over", "winner": game_winner, "board": chess_board, "turn": turn}

    is_white = turn == "white"
    piece = chess_board[move.from_row][move.from_col]

    if piece == ".":
        return {"status": "invalid", "message": "No piece at that square.", "board": chess_board, "turn": turn}
    if piece.isupper() != is_white:
        return {"status": "invalid", "message": f"It's {turn}'s turn.", "board": chess_board, "turn": turn}

    requested = (move.from_row, move.from_col, move.to_row, move.to_col)
    if requested not in get_legal_moves(chess_board, is_white):
        return {"status": "invalid", "message": "Illegal move.", "board": chess_board, "turn": turn}

    chess_board = apply_move(chess_board, move.from_row, move.from_col, move.to_row, move.to_col)
    turn = "black" if is_white else "white"

    status, winner = get_game_status(chess_board, turn == "white")
    if status in ("checkmate", "stalemate"):
        game_over = True
        game_winner = winner

    return {"status": status, "winner": winner, "board": chess_board, "turn": turn}


@app.get("/engine-move")
def engine_move():
    global chess_board, turn, game_over, game_winner

    if game_over:
        return {"status": "game_over", "winner": game_winner, "board": chess_board, "turn": turn}
    if turn != "black":
        return {"status": "not_engine_turn", "board": chess_board, "turn": turn}

    _, best_move = minimax(chess_board, 3, float("-inf"), float("inf"), False)

    if not best_move:
        status = "checkmate" if is_in_check(chess_board, False) else "stalemate"
        game_winner = "white wins!" if status == "checkmate" else "draw"
        game_over = True
        return {"status": status, "winner": game_winner, "board": chess_board, "turn": turn}

    chess_board = apply_move(chess_board, *best_move)
    turn = "white"

    status, winner = get_game_status(chess_board, True)
    if status in ("checkmate", "stalemate"):
        game_over = True
        game_winner = winner

    return {"status": status, "winner": winner, "board": chess_board, "turn": turn}
