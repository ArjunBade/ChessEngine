from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Allow all origins
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chessboard setup
chess_board = [
    ["r", "n", "b", "q", "k", "b", "n", "r"],
    ["p", "p", "p", "p", "p", "p", "p", "p"],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    ["P", "P", "P", "P", "P", "P", "P", "P"],
    ["R", "N", "B", "Q", "K", "B", "N", "R"]
]

turn = "white"  # White starts

class Move(BaseModel):
    from_row: int
    from_col: int
    to_row: int
    to_col: int

def is_valid_move(move: Move):
    piece = chess_board[move.from_row][move.from_col]
    target = chess_board[move.to_row][move.to_col]

    if piece == ".":
        return False, "No piece at the selected square."

    is_white = piece.isupper()

    # Turn enforcement
    if (turn == "white" and not piece.isupper()) or (turn == "black" and piece.isupper()):
        return False, f"It's {turn}'s turn."

    # Cannot capture your own piece
    if target != "." and (target.isupper() == is_white):
        return False, "Cannot capture your own piece."

    # Example: Pawn movement rules
    if piece == "P":
        # Pawn capture
        if move.to_row == move.from_row - 1 and abs(move.to_col - move.from_col) == 1 and target != ".":
            return True, "Valid move."
        # Regular pawn move
        if move.to_row == move.from_row - 1 and move.from_col == move.to_col and target == ".":
            return True, "Valid move."
        # Initial two-square pawn move
        if move.from_row == 6 and move.to_row == 4 and move.from_col == move.to_col and target == ".":
            return True, "Valid move."
    elif piece == "p":
        # Pawn capture
        if move.to_row == move.from_row + 1 and abs(move.to_col - move.from_col) == 1 and target != ".":
            return True, "Valid move."
        # Regular pawn move
        if move.to_row == move.from_row + 1 and move.from_col == move.to_col and target == ".":
            return True, "Valid move."
        # Initial two-square pawn move
        if move.from_row == 1 and move.to_row == 3 and move.from_col == move.to_col and target == ".":
            return True, "Valid move."
    elif piece == "R" or piece == "r":
        # Rook moves: horizontally or vertically
        if move.from_row == move.to_row or move.from_col == move.to_col:
            return True, "Valid move."
    elif piece == "N" or piece == "n":
        # Knight moves: "L" shape (2x1)
        if abs(move.from_row - move.to_row) == 2 and abs(move.from_col - move.to_col) == 1:
            return True, "Valid move."
        if abs(move.from_row - move.to_row) == 1 and abs(move.from_col - move.to_col) == 2:
            return True, "Valid move."
    elif piece == "B" or piece == "b":
        # Bishop moves: diagonally
        if abs(move.from_row - move.to_row) == abs(move.from_col - move.to_col):
            return True, "Valid move."
    elif piece == "Q" or piece == "q":
        # Queen moves: horizontally, vertically, or diagonally
        if abs(move.from_row - move.to_row) == abs(move.from_col - move.to_col) or move.from_row == move.to_row or move.from_col == move.to_col:
            return True, "Valid move."
    elif piece == "K" or piece == "k":
        # King moves: one square in any direction
        if abs(move.from_row - move.to_row) <= 1 and abs(move.from_col - move.to_col) <= 1:
            return True, "Valid move."

    return False, "Invalid move for this piece."

def check_winner():
    # Check for checkmate or stalemate (basic logic)
    black_king = any("k" in row for row in chess_board)
    white_king = any("K" in row for row in chess_board)

    if not black_king:
        return "white wins!"
    if not white_king:
        return "black wins!"
    return None  # No winner yet

@app.post("/new-game")
def new_game():
    global chess_board, turn
    turn = "white"  # Reset turn to white
    chess_board = [
        ["r", "n", "b", "q", "k", "b", "n", "r"],
        ["p", "p", "p", "p", "p", "p", "p", "p"],
        [".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", "."],
        ["P", "P", "P", "P", "P", "P", "P", "P"],
        ["R", "N", "B", "Q", "K", "B", "N", "R"]
    ]
    return {"board": chess_board}

@app.post("/make-move")
def make_move(move: Move):
    global chess_board, turn
    valid, message = is_valid_move(move)

    if not valid:
        return {"status": "Invalid move", "message": message, "board": chess_board}

    # Move piece
    piece = chess_board[move.from_row][move.from_col]
    chess_board[move.from_row][move.from_col] = "."
    chess_board[move.to_row][move.to_col] = piece

    # Check winner (checkmate)
    winner = check_winner()

    if winner:
        return {"status": "Game Over", "winner": winner, "board": chess_board}

    # Switch turn
    turn = "black" if turn == "white" else "white"
    return {"status": "Move applied", "board": chess_board}

@app.get("/engine-move")
def engine_move():
    return {"board": chess_board}
