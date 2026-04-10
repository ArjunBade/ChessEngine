# Future Work

Planned improvements and known limitations for the Chess vs Engine project.

## Features to Add

- **Castling and en passant** — the two remaining special chess moves not yet implemented
- **Multiplayer** — currently only supports a single game session (one player vs engine)
- **Persistent game state** — engine state is stored in-memory on the server, so refreshing the browser resets the game; a database or session store would fix this

## Security & Robustness (relevant if deployed publicly)

- **Input bounds validation** — `from_row`, `from_col`, `to_row`, `to_col` should be validated to be within 0–7 before processing; an out-of-range value currently causes an index error
- **CORS hardening** — `allow_origins=["*"]` should be restricted to the actual frontend origin in a production deployment
- **Rate limiting on `/engine-move`** — minimax is compute-heavy; without rate limiting, the endpoint could be spammed to peg the server CPU
- **Per-session game state** — global mutable state means multiple browser tabs or users corrupt each other's game; should be replaced with session-scoped state

## Engine Improvements

- **Increase search depth** — currently depth 3; depth 4–5 would play significantly stronger but requires move ordering or further optimisation to stay fast
- **Positional evaluation** — current evaluation is purely material; adding piece-square tables would make the engine prefer better piece placement
- **Opening book** — hardcode common strong opening lines to avoid weak early play
