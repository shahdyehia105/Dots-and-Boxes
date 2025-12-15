import pygame
from ui import WHITE, GRAY, BG, FPS

class Menu:
    def __init__(self, screen, options, title="Menu"):
        self.screen = screen
        self.font_title = pygame.font.SysFont(None, 56)
        self.font_opt = pygame.font.SysFont(None, 36)
        self.options = options  # list of (label, value)
        self.selected = 0
        self.title = title

    def draw(self):
        self.screen.fill(BG)
        title_surf = self.font_title.render(self.title, True, WHITE)
        self.screen.blit(title_surf, (self.screen.get_width()//2 - title_surf.get_width()//2, 80))
        for i, (label, _) in enumerate(self.options):
            color = WHITE if i == self.selected else GRAY
            surf = self.font_opt.render(label, True, color)
            self.screen.blit(surf, (self.screen.get_width()//2 - surf.get_width()//2, 200 + i*60))
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        while True:
            clock.tick(FPS)
            self.draw()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.options)
                    elif ev.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.options)
                    elif ev.key == pygame.K_RETURN:

                        return self.options[self.selected][1]
