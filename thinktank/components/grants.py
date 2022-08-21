import pygame
import time

from cxr.state.state import StateManager
from cxr.math.base36 import Tridozenal as Td

targets = [Td(x**2) for x in range(1, 50)]
l_t = len(targets)


class Grants(StateManager):

    def __init__(self, key, name):
        super().__init__(key, name)
        self.initialize()

    def initialize(self):
        self["current_target"] = 0
        self["count"] = Td.zero()
        self["credit_rate_increase"] = Td(2) / Td(78)
        self["completed"] = False
        self["start_time"] = time.time()
        self["progress_time"] = 0
        self.nonser("player")

        @self.controller
        def grants_controller(event):
            self["count"] += event.count
            if not self.completed:
                if self.count >= targets[self.current_target]:
                    self["player"]["credit_rate"] += self.credit_rate_increase
                    self["current_target"] += 1
                    print(f"Grant level up, new credit rate is {str(self.player.credit_rate)}. ", end="")
                    self["credit_rate_increase"] = Td((self.current_target + 1) * (2 + (self.current_target + 1) // 2)) / Td(66)
                    self["progress_time"] = time.time() - self.start_time
                    if self.current_target < l_t:
                        print(f"New target is {targets[self.current_target]}")
                    else:
                        self["completed"] = True
                        print()

    def set_player(self, player):
        self["player"] = player

    def convert(self):
        global targets
        targets = [target.convert() for target in targets]
        self["count"] = self.count.convert()

    def draw(self, screen, font):
        text = font.render(f"{self.count}", True, (255, 255, 255), "black")
        text_rect = text.get_rect(center=(685, 500))
        screen.blit(text, text_rect)
        if self.current_target < l_t:
            pygame.draw.line(screen, (255, 255, 255), (650, 515), (730, 515))
            text = font.render(f"{targets[self.current_target]}", True, (255, 255, 255), "black")
            text_rect = text.get_rect(center=(685, 535))
            screen.blit(text, text_rect)
