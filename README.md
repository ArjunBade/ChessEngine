# Chess vs Engine

A browser-based chess game where you play as White against a Python-powered chess engine. Built with a **React** frontend and a **FastAPI** backend.

---

## Features

- Full legal move validation (including path-blocking for rooks, bishops, and queens)
- Check, checkmate, and stalemate detection
- Pawn promotion (auto-promotes to queen)
- Turn enforcement
- **Minimax engine with alpha-beta pruning** (depth 3) plays as Black
- Unicode chess pieces rendered in the browser
- Board coordinates (a–h, 1–8)
- Game status bar — shows whose turn it is, check warnings, and game-over results
- New Game button to reset at any time

---

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Axios |
| Backend | Python, FastAPI, Pydantic |
| Engine | Minimax + Alpha-Beta Pruning |

---

## How the Engine Works

The engine uses **minimax search with alpha-beta pruning** at depth 3.

```
Engine's turn
│
├── Generate all legal Black moves
│   └── Filter out moves that leave Black's king in check
│
├── For each move, simulate the position (depth 3)
│   ├── Opponent (White) picks the move that maximises score
│   └── Engine (Black) picks the move that minimises score
│
├── Evaluate leaf positions by material count
│   P=100  N=320  B=330  R=500  Q=900  K=20000
│
└── Alpha-beta pruning cuts branches that can't affect the result,
    reducing the search tree significantly
```

Alpha-beta pruning means the engine evaluates far fewer positions than a plain minimax search would, while producing the same result — making depth 3 fast enough for real-time play.

---

## Architecture

```
ChessEngine/
├── fastAPI/
│   └── main.py          # Game logic, move generation, minimax engine, REST API
└── src/
    ├── App.js           # React board, click handling, engine call flow
    ├── index.js         # React entry point
    └── index.css        # Base styles
```

**API endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/new-game` | Reset board and state |
| `POST` | `/make-move` | Validate and apply player's move |
| `GET` | `/engine-move` | Compute and apply engine's best move |

---

## Getting Started

### Prerequisites

- Node.js ≥ 18
- Python ≥ 3.9
- pip

### Backend

```bash
cd fastAPI
pip install fastapi uvicorn pydantic
uvicorn main:app --reload
# API runs at http://localhost:8000
```

### Frontend

```bash
# from project root
npm install
npm start
# App runs at http://localhost:3000
```

Open [http://localhost:3000](http://localhost:3000) — you play White, the engine plays Black.

---

## How to Play

1. Click a white piece to select it (highlighted green)
2. Click a destination square to move
3. The engine responds automatically
4. Click **New Game** to reset at any time

---

## Known Limitations and Future Work

- No castling or en passant (planned)
- Engine state is stored in-memory on the server — refreshing resets the game
- Single game session (no multiplayer)
