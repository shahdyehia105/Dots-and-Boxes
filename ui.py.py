import pygame
from typing import Tuple, Optional
from board import Board, Move
from ai import HumanPlayer, MinimaxAI, PlayerBase




CELL_SIZE_BASE = 80
PADDING_BASE = 40
DOT_RADIUS = 6
LINE_WIDTH = 6
FPS = 30
AI_MOVE_DELAY_MS = 250


WHITE = (255, 255, 255)
BLACK = (12, 12, 12)
RED = (252, 91, 122)
BLUE = (78, 139, 246)
GRAY = (90, 90, 90)
BG = (20, 20, 20)
YELLOW = (240, 200, 60)




class GameUI:
    def __init__(self, box_rows: int, box_cols: int, mode: str, ai_depth: int = 4):
        # layout scaling
        self.box_rows = box_rows
        self.box_cols = box_cols
        self.cell_size = CELL_SIZE_BASE
        self.padding = PADDING_BASE
        # screen size based on board
        self.screen_w = self.box_cols * self.cell_size + 2 * self.padding
        self.screen_h = self.box_rows * self.cell_size + 2 * self.padding
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))
        pygame.display.set_caption("Dots & Boxes")
        self.clock = pygame.time.Clock()

        
        self.board = Board(box_rows, box_cols)
        self.mode = mode
        self.ai_depth = ai_depth
        
        self.players: dict[str, PlayerBase] = {}
        
        if mode == "AI_AI":
            self.players = {
                "A": MinimaxAI("AI_A", "A", max_depth=ai_depth),
                "B": MinimaxAI("AI_B", "B", max_depth=ai_depth)
            }
        elif mode == "HUMAN_AI":
            
            self.players = {
                "A": HumanPlayer("Human", "A"),
                "B": MinimaxAI("AI_B", "B", max_depth=ai_depth)
            }
        else:  
            self.players = {
                "A": HumanPlayer("Human A", "A"),
                "B": HumanPlayer("Human B", "B")
            }

        self.players["A"].symbol = "A"
        self.players["B"].symbol = "B"
        self.current = "A"
        self.hover_edge: Optional[Tuple[Move, Tuple[int,int]]] = None
        self.font = pygame.font.SysFont(None, 22)
        self.running = True
        self.last_ai_move_time = 0

    def dot_pos(self, r: int, c: int) -> Tuple[int, int]:
        x = self.padding + c * self.cell_size
        y = self.padding + r * self.cell_size
        return x, y

    def edge_center_pos(self, move: Move) -> Tuple[int, int]:
        if move.kind == "H":
            x1, y1 = self.dot_pos(move.r, move.c)
            x2, y2 = self.dot_pos(move.r, move.c + 1)
        else:
            x1, y1 = self.dot_pos(move.r, move.c)
            x2, y2 = self.dot_pos(move.r + 1, move.c)
        return ((x1 + x2) // 2, (y1 + y2) // 2)

    def detect_edge_from_pos(self, pos: Tuple[int,int]) -> Optional[Move]:
        x, y = pos
        threshold = self.cell_size // 3
        
        for r in range(self.box_rows + 1):
            for c in range(self.box_cols):
                x1, y1 = self.dot_pos(r, c)
                x2, y2 = self.dot_pos(r, c + 1)
                minx, maxx = min(x1, x2) - 6, max(x1, x2) + 6
                miny, maxy = y1 - threshold, y1 + threshold
                if minx <= x <= maxx and miny <= y <= maxy:
                    return Move(r, c, "H")
        
        for r in range(self.box_rows):
            for c in range(self.box_cols + 1):
                x1, y1 = self.dot_pos(r, c)
                x2, y2 = self.dot_pos(r + 1, c)
                minx, maxx = x1 - threshold, x1 + threshold
                miny, maxy = min(y1, y2) - 6, max(y1, y2) + 6
                if minx <= x <= maxx and miny <= y <= maxy:
                    return Move(r, c, "V")
        return None

    def draw(self):
        self.screen.fill(BG)
        
        for r in range(self.box_rows):
            for c in range(self.box_cols):
                owner = self.board.boxes[r][c]
                if owner is not None:
                    x, y = self.dot_pos(r, c)
                    rect = pygame.Rect(x + LINE_WIDTH//2, y + LINE_WIDTH//2,
                                       self.cell_size - LINE_WIDTH, self.cell_size - LINE_WIDTH)
                    color = BLUE if owner == "A" else RED
                    pygame.draw.rect(self.screen, color, rect)

        
        for r in range(self.box_rows + 1):
            for c in range(self.box_cols):
                x1, y1 = self.dot_pos(r, c)
                x2, y2 = self.dot_pos(r, c + 1)
                if self.board.h_edges[r][c]:
                    color = WHITE
                    width = LINE_WIDTH
                else:
                    color = GRAY
                    width = 2
                pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), width)

        
        for r in range(self.box_rows):
            for c in range(self.box_cols + 1):
                x1, y1 = self.dot_pos(r, c)
                x2, y2 = self.dot_pos(r + 1, c)
                if self.board.v_edges[r][c]:
                    color = WHITE
                    width = LINE_WIDTH
                else:
                    color = GRAY
                    width = 2
                pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), width)

        
        for r in range(self.box_rows + 1):
            for c in range(self.box_cols + 1):
                x, y = self.dot_pos(r, c)
                pygame.draw.circle(self.screen, WHITE, (x, y), DOT_RADIUS)

        
        if self.hover_edge:
            move, snap = self.hover_edge
            if self.board.is_valid_move(move):
                if move.kind == "H":
                    x1, y1 = self.dot_pos(move.r, move.c)
                    x2, y2 = self.dot_pos(move.r, move.c + 1)
                    pygame.draw.line(self.screen, YELLOW, (x1, y1), (x2, y2), LINE_WIDTH)
                else:
                    x1, y1 = self.dot_pos(move.r, move.c)
                    x2, y2 = self.dot_pos(move.r + 1, move.c)
                    pygame.draw.line(self.screen, YELLOW, (x1, y1), (x2, y2), LINE_WIDTH)

        
        a_score, b_score = self.board.get_scores()
        txt = self.font.render(f"A: {a_score}   B: {b_score}    Turn: {self.current}", True, WHITE)
        self.screen.blit(txt, (10, self.screen_h - 28))
        pygame.display.flip()

    def handle_human_click(self, move: Move):
        if not move: 
            return False
        if not self.board.is_valid_move(move):
            return False
        num, assigned = self.board.apply_move(move, self.current)
        return num, assigned

    def ai_move_once(self):
        ai_player: MinimaxAI = self.players[self.current] 
        move = ai_player.choose_move(self.board)
        num, assigned = self.board.apply_move(move, self.current)
        return move, num, assigned

    def show_game_over(self):
        a, b = self.board.get_scores()
        winner = "Draw"
        if a > b:
            winner = "A wins"
        elif b > a:
            winner = "B wins"
        overlay = pygame.Surface((self.screen_w, self.screen_h))
        overlay.set_alpha(220)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        big = pygame.font.SysFont(None, 48)
        txt = big.render(f"Game Over - {winner}", True, WHITE)
        self.screen.blit(txt, (self.screen_w//2 - txt.get_width()//2, self.screen_h//2 - 40))
        small = pygame.font.SysFont(None, 28)
        txt2 = small.render(f"Final Score A: {a}   B: {b}", True, WHITE)
        self.screen.blit(txt2, (self.screen_w//2 - txt2.get_width()//2, self.screen_h//2 + 10))
        pygame.display.flip()
        waiting = True
        while waiting:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    waiting = False
                elif ev.type == pygame.KEYDOWN or ev.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
            pygame.time.wait(50)

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            
            if isinstance(self.players[self.current], MinimaxAI):
                
                now = pygame.time.get_ticks()
                if now - self.last_ai_move_time < AI_MOVE_DELAY_MS:
                    
                    for e in pygame.event.get():
                        if e.type == pygame.QUIT:
                            self.running = False
                    self.draw()
                    continue
                self.last_ai_move_time = now
                move, num, assigned = self.ai_move_once()
                if num == 0:
                    self.current = "B" if self.current == "A" else "A"
                if self.board.is_terminal():
                    self.draw()
                    self.show_game_over()
                    break
                self.draw()
                continue

            
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.running = False
                    break
                elif ev.type == pygame.MOUSEMOTION:
                    pos = ev.pos
                    det = self.detect_edge_from_pos(pos)
                    if det and self.board.is_valid_move(det):
                        snap = self.edge_center_pos(det)
                        self.hover_edge = (det, snap)
                    else:
                        self.hover_edge = None
                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    pos = ev.pos
                    det = self.detect_edge_from_pos(pos)
                    if det and self.board.is_valid_move(det) and isinstance(self.players[self.current], HumanPlayer):
                        num, assigned = self.board.apply_move(det, self.current)
                        if num == 0:
                            self.current = "B" if self.current == "A" else "A"
                        if self.board.is_terminal():
                            self.draw()
                            self.show_game_over()
                            self.running = False
               

            self.draw()