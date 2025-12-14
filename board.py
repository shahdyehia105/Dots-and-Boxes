from dataclasses import dataclass
from typing import List, Tuple, Optional

# -----------------------------
# Dataclass Move
# -----------------------------
@dataclass(frozen=True)
class Move:
    r: int
    c: int
    kind: str  # "H" or "V"

    def __str__(self):
        return f"{self.kind}({self.r},{self.c})"

# -----------------------------
# Board (global edges + boxes)
# -----------------------------
class Board:
    def __init__(self, rows: int, cols: int):
        self.rows = rows  # number of boxes vertically
        self.cols = cols  # number of boxes horizontally
        self.h_edges = [[False for _ in range(cols)] for _ in range(rows + 1)]
        self.v_edges = [[False for _ in range(cols + 1)] for _ in range(rows)]
        self.boxes: List[List[Optional[str]]] = [[None for _ in range(cols)] for _ in range(rows)]
        self.score = {"A": 0, "B": 0}
        self.total_edges = (rows + 1) * cols + rows * (cols + 1)
        self.filled_edges = 0

    def clone(self) -> "Board":
        b = Board(self.rows, self.cols)
        b.h_edges = [row[:] for row in self.h_edges]
        b.v_edges = [row[:] for row in self.v_edges]
        b.boxes = [row[:] for row in self.boxes]
        b.score = dict(self.score)
        b.filled_edges = self.filled_edges
        return b

    def is_valid_move(self, move: Move) -> bool:
        r, c, k = move.r, move.c, move.kind
        if k == "H":
            if not (0 <= r <= self.rows and 0 <= c < self.cols):
                return False
            return not self.h_edges[r][c]
        else:
            if not (0 <= r < self.rows and 0 <= c <= self.cols):
                return False
            return not self.v_edges[r][c]

    def get_valid_moves(self) -> List[Move]:
        moves = []
        for r in range(self.rows + 1):
            for c in range(self.cols):
                if not self.h_edges[r][c]:
                    moves.append(Move(r, c, "H"))
        for r in range(self.rows):
            for c in range(self.cols + 1):
                if not self.v_edges[r][c]:
                    moves.append(Move(r, c, "V"))
        return moves

    def _check_box_complete(self, br: int, bc: int) -> bool:
        top = self.h_edges[br][bc]
        bottom = self.h_edges[br + 1][bc]
        left = self.v_edges[br][bc]
        right = self.v_edges[br][bc + 1]
        return top and bottom and left and right

    def apply_move(self, move: Move, player_symbol: str) -> Tuple[int, List[Tuple[int,int]]]:
        if not self.is_valid_move(move):
            raise ValueError("Invalid move: " + str(move))
        r, c, k = move.r, move.c, move.kind
        if k == "H":
            self.h_edges[r][c] = True
        else:
            self.v_edges[r][c] = True
        self.filled_edges += 1
        completed = []
        if k == "H":
            if r > 0 and self.boxes[r-1][c] is None and self._check_box_complete(r-1, c):
                self.boxes[r-1][c] = player_symbol
                self.score[player_symbol] += 1
                completed.append((r-1, c))
            if r < self.rows and self.boxes[r][c] is None and self._check_box_complete(r, c):
                self.boxes[r][c] = player_symbol
                self.score[player_symbol] += 1
                completed.append((r, c))
        else:
            if c > 0 and self.boxes[r][c-1] is None and self._check_box_complete(r, c-1):
                self.boxes[r][c-1] = player_symbol
                self.score[player_symbol] += 1
                completed.append((r, c-1))
            if c < self.cols and self.boxes[r][c] is None and self._check_box_complete(r, c):
                self.boxes[r][c] = player_symbol
                self.score[player_symbol] += 1
                completed.append((r, c))
        return len(completed), completed

    def undo_move(self, move: Move, assigned_boxes: List[Tuple[int,int]]):
        r, c, k = move.r, move.c, move.kind
        if k == "H":
            self.h_edges[r][c] = False
        else:
            self.v_edges[r][c] = False
        self.filled_edges -= 1
        for (br, bc) in assigned_boxes:
            owner = self.boxes[br][bc]
            if owner is not None:
                self.score[owner] -= 1
            self.boxes[br][bc] = None

    def is_terminal(self) -> bool:
        return self.filled_edges >= self.total_edges

    def get_scores(self) -> Tuple[int, int]:
        return self.score["A"], self.score["B"]