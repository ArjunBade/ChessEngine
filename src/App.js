import React, { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [board, setBoard] = useState([]);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    axios.post("http://localhost:8000/new-game").then((response) => {
      setBoard(response.data.board);
    });
  }, []);

  const handleCellClick = (rowIndex, colIndex) => {
    if (!selected) {
      setSelected({ row: rowIndex, col: colIndex });
    } else {
      axios
        .post("http://localhost:8000/make-move", {
          from_row: selected.row,
          from_col: selected.col,
          to_row: rowIndex,
          to_col: colIndex,
        })
        .then((response) => {
          setBoard(response.data.board);
          setSelected(null);
        })
        .catch((error) => {
          console.error("Error making move:", error);
          setSelected(null);
        });
    }
  };

  return (
    <div className="App">
      <h1>Chess Game</h1>
      <table style={{ borderCollapse: "collapse", margin: "20px auto" }}>
        <tbody>
          {board.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {row.map((cell, colIndex) => (
                <td
                  key={colIndex}
                  onClick={() => handleCellClick(rowIndex, colIndex)}
                  style={{
                    width: "60px",
                    height: "60px",
                    textAlign: "center",
                    border: "1px solid black",
                    backgroundColor:
                      selected &&
                      selected.row === rowIndex &&
                      selected.col === colIndex
                        ? "lightgreen"
                        : (rowIndex + colIndex) % 2 === 0
                        ? "#f0d9b5"
                        : "#b58863",
                    fontSize: "24px",
                    cursor: "pointer",
                  }}
                >
                  {cell !== "." ? cell : ""}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
