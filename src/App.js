import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";

const API = "http://localhost:8000";

const SYMBOLS = {
  K: "♔", Q: "♕", R: "♖", B: "♗", N: "♘", P: "♙",
  k: "♚", q: "♛", r: "♜", b: "♝", n: "♞", p: "♟",
};

const STATUS_COLOR = {
  ongoing: "#2c3e50",
  check: "#e67e22",
  checkmate: "#c0392b",
  stalemate: "#8e44ad",
  game_over: "#c0392b",
};

function App() {
  const [board, setBoard] = useState([]);
  const [selected, setSelected] = useState(null);
  const [status, setStatus] = useState("ongoing");
  const [turn, setTurn] = useState("white");
  const [winner, setWinner] = useState(null);
  const [engineThinking, setEngineThinking] = useState(false);

  const applyResponse = (data) => {
    setBoard(data.board);
    setTurn(data.turn);
    setStatus(data.status);
    if (data.winner) setWinner(data.winner);
  };

  const startNewGame = useCallback(async () => {
    const res = await axios.post(`${API}/new-game`);
    setBoard(res.data.board);
    setTurn(res.data.turn);
    setStatus("ongoing");
    setWinner(null);
    setSelected(null);
    setEngineThinking(false);
  }, []);

  useEffect(() => {
    startNewGame();
  }, [startNewGame]);

  const callEngine = useCallback(async () => {
    setEngineThinking(true);
    try {
      const res = await axios.get(`${API}/engine-move`);
      applyResponse(res.data);
    } finally {
      setEngineThinking(false);
    }
  }, []);

  const handleCellClick = async (row, col) => {
    const isOver = status === "checkmate" || status === "stalemate" || status === "game_over";
    if (isOver || engineThinking || turn !== "white") return;

    if (!selected) {
      const piece = board[row]?.[col];
      // Only allow selecting white pieces (uppercase)
      if (piece && piece !== "." && piece === piece.toUpperCase()) {
        setSelected({ row, col });
      }
      return;
    }

    // Clicking the same square deselects
    if (selected.row === row && selected.col === col) {
      setSelected(null);
      return;
    }

    // Clicking another own piece reselects
    const piece = board[row]?.[col];
    if (piece && piece !== "." && piece === piece.toUpperCase()) {
      setSelected({ row, col });
      return;
    }

    try {
      const res = await axios.post(`${API}/make-move`, {
        from_row: selected.row,
        from_col: selected.col,
        to_row: row,
        to_col: col,
      });
      setSelected(null);
      const data = res.data;

      if (data.status === "invalid") return;

      applyResponse(data);

      const isGameOver = data.status === "checkmate" || data.status === "stalemate";
      if (!isGameOver) {
        await callEngine();
      }
    } catch (err) {
      console.error(err);
      setSelected(null);
    }
  };

  const statusText = () => {
    if (winner) return `Game Over — ${winner.charAt(0).toUpperCase() + winner.slice(1)}`;
    if (status === "stalemate") return "Stalemate — Draw";
    if (engineThinking) return "Engine is thinking...";
    if (status === "check") return turn === "white" ? "Check — Your turn (White)" : "Check — Engine's turn (Black)";
    return turn === "white" ? "Your turn (White)" : "Engine's turn (Black)";
  };

  return (
    <div style={{ fontFamily: "'Segoe UI', sans-serif", textAlign: "center", padding: "30px", background: "#f3f4f6", minHeight: "100vh" }}>
      <h1 style={{ fontSize: "30px", marginBottom: "6px", color: "#2c3e50" }}>Chess vs Engine</h1>
      <p style={{ color: "#7f8c8d", marginBottom: "16px", fontSize: "14px" }}>You play White — Engine plays Black (depth 3 minimax)</p>

      <div style={{
        marginBottom: "16px",
        fontSize: "17px",
        fontWeight: "600",
        color: STATUS_COLOR[status] ?? "#2c3e50",
        minHeight: "26px",
      }}>
        {statusText()}
      </div>

      {/* Board */}
      <div style={{ display: "inline-block", border: "3px solid #2c3e50", borderRadius: "4px", overflow: "hidden" }}>
        {/* Column labels */}
        <div style={{ display: "flex", paddingLeft: "28px" }}>
          {"abcdefgh".split("").map(l => (
            <div key={l} style={{ width: "70px", textAlign: "center", fontSize: "12px", color: "#7f8c8d", padding: "2px 0" }}>{l}</div>
          ))}
        </div>

        {board.map((row, rowIndex) => (
          <div key={rowIndex} style={{ display: "flex", alignItems: "center" }}>
            {/* Row label */}
            <div style={{ width: "28px", textAlign: "center", fontSize: "12px", color: "#7f8c8d" }}>{8 - rowIndex}</div>

            {row.map((cell, colIndex) => {
              const isLight = (rowIndex + colIndex) % 2 === 0;
              const isSelected = selected?.row === rowIndex && selected?.col === colIndex;
              const isWhitePiece = cell !== "." && cell === cell.toUpperCase();

              return (
                <div
                  key={colIndex}
                  onClick={() => handleCellClick(rowIndex, colIndex)}
                  style={{
                    width: "70px",
                    height: "70px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    backgroundColor: isSelected
                      ? "#7fc97f"
                      : isLight ? "#f0d9b5" : "#b58863",
                    fontSize: "44px",
                    cursor: "pointer",
                    userSelect: "none",
                    lineHeight: 1,
                    color: isWhitePiece ? "#ffffff" : "#1a1a1a",
                    textShadow: isWhitePiece
                      ? "0 0 2px #555, 0 0 2px #555"
                      : "0 0 2px #ccc",
                    transition: "background-color 0.1s",
                  }}
                >
                  {cell !== "." ? (SYMBOLS[cell] ?? cell) : ""}
                </div>
              );
            })}
          </div>
        ))}
      </div>

      <div style={{ marginTop: "20px" }}>
        <button
          onClick={startNewGame}
          style={{
            padding: "10px 28px",
            fontSize: "15px",
            backgroundColor: "#2c3e50",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
            fontWeight: "600",
            letterSpacing: "0.5px",
          }}
        >
          New Game
        </button>
      </div>
    </div>
  );
}

export default App;
