import React, { useEffect, useState } from "react";
import axios from "axios";

const Chessboard = () => {
  const [board, setBoard] = useState([]);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    startNewGame();
  }, []);

  const startNewGame = async () => {
    const res = await axios.post("http://localhost:8000/new-game");
    setBoard(res.data.board);
    setSelected(null);
  };

  const handleSquareClick = (r, c) => {
    if (selected) {
      makeMove(selected, { row: r, col: c });
      setSelected(null);
    } else {
      setSelected({ row: r, col: c });
    }
  };

  const makeMove = async (from, to) => {
    await axios.post("http://localhost:8000/make-move", {
      start_row: from.row,
      start_col: from.col,
      end_row: to.row,
      end_col: to.col,
    });
    const response = await axios.get("http://localhost:8000/engine-move");
    setBoard(response.data.board);
  };

  return (
    <div>
      <h1>React Chess vs Python Engine</h1>
      <div className="board">
        {board.map((row, r) =>
          row.map((piece, c) => {
            const isWhite = (r + c) % 2 === 0;
            const isSelected =
              selected && selected.row === r && selected.col === c;
            return (
              <div
                key={${r}-${c}}
                className={square ${isWhite ? "white" : "black"} ${
                  isSelected ? "selected" : ""
                }}
                onClick={() => handleSquareClick(r, c)}
              >
                {piece !== "." ? piece : ""}
              </div>
            );
          })
        )}
      </div>
      <button onClick={startNewGame}>New Game</button>
    </div>
  );
};

export default Chessboard;
