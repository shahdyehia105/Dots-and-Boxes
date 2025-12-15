import math
import random
from typing import List, Tuple
from board import Board, Move

class PlayerBase:
    def __init__(self, name: str, symbol: str):
        self.name = name
        self.symbol = symbol

    def choose_move(self, board: Board) -> Move:
        raise NotImplementedError

class HumanPlayer(PlayerBase):
    def choose_move(self, board: Board) -> Move:
        raise NotImplementedError

class AIPlayer(PlayerBase):
    def __init__(self, name: str, symbol: str, depth: int = 3):
        super().__init__(name, symbol)
        self.depth = depth

    def choose_move(self, board: Board) -> Move:
        best_score = -math.inf
        best_move = None

        for move in board.get_valid_moves():
            new_board = board.clone()
            new_board.apply_move(move, self.symbol)
            score = self.minimax(new_board, self.depth - 1, False)
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def minimax(self, board: Board, depth: int, is_maximizing: bool) -> float:
        if depth == 0 or board.is_game_over():
            return self.evaluate(board)

        if is_maximizing:
            best_score = -math.inf
            for move in board.get_valid_moves():
                new_board = board.clone()
                new_board.apply_move(move, self.symbol)
                score = self.minimax(new_board, depth - 1, False)
                best_score = max(best_score, score)
            return best_score
        else:
            best_score = math.inf
            opponent = board.get_opponent_symbol(self.symbol)
            for move in board.get_valid_moves():
                new_board = board.clone()
                new_board.apply_move(move, opponent)
                score = self.minimax(new_board, depth - 1, True)
                best_score = min(best_score, score)
            return best_score

    def evaluate(self, board: Board) -> float:
        score_diff = board.get_score(self.symbol) - board.get_score(
            board.get_opponent_symbol(self.symbol)
        )

        risky_penalty = 0.0
        for r in range(board.rows):
            for c in range(board.cols):
                if board.boxes[r][c] is None:
                    edges_filled = (
                        board.h_edges[r][c] +
                        board.h_edges[r + 1][c] +
                        board.v_edges[r][c] +
                        board.v_edges[r][c + 1]
                    )
                    if edges_filled == 3:
                        risky_penalty -= 6.0
                    elif edges_filled == 2:
                        risky_penalty += 0.5

        mobility = len(board.get_valid_moves()) * 0.1
        return score_diff + risky_penalty + mobility
