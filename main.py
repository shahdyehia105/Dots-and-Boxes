import pygame
from menu import Menu
from ui import GameUI

def main():
    pygame.init()
    temp_w = 640
    temp_h = 480
    screen = pygame.display.set_mode((temp_w, temp_h))
    pygame.display.set_caption("Dots & Boxes - Menu")

    mode_opts = [("Human vs AI", "HUMAN_AI"), ("AI vs AI", "AI_AI"), ("Human vs Human", "HUMAN_HUMAN")]
    mode_menu = Menu(screen, mode_opts, title="Select Mode")
    mode = mode_menu.run()

    size_opts = [("3 x 3 boxes", (3, 3)), ("4 x 4 boxes", (4, 4)), ("5 x 5 boxes", (5, 5))]
    size_menu = Menu(screen, [(label, val) for label, val in size_opts], title="Select Board Size")
    board_choice = size_menu.run()
    box_rows, box_cols = board_choice

    diff_opts = [("Easy (depth 2)", 2), ("Medium (depth 4)", 4), ("Hard (depth 6)", 6), ("Expert (depth 8)", 8)]
    diff_menu = Menu(screen, diff_opts, title="Select Difficulty (AI Depth)")
    ai_depth = diff_menu.run()

    ui = GameUI(box_rows, box_cols, mode=mode, ai_depth=ai_depth)
    ui.run()
    pygame.quit()

if __name__ == "__main__":
    main()