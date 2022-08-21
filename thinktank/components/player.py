
from cxr.state.state import StateManager
from cxr.math.base36 import Tridozenal as Td

from thinktank import TICK


class Player(StateManager):

    def __init__(self, key, name):
        super().__init__(key, name)
        self.initialize()

    def _initialize_ser(self):
        self["science"] = Td.zero()
        self["art"] = Td.zero()
        self["literature"] = Td.zero()
        self["philosophy"] = Td.zero()
        self["credits"] = Td.zero()
        self["credit_rate"] = Td(1) / Td(30)

    def _initialize_nonser(self):
        self.nonser("average_timer", 0)
        self.nonser("gains", [Td.zero() for _ in range(5)])
        self.nonser("averages", [Td.zero() for _ in range(5)])

    def initialize(self):
        self._initialize_ser()
        self._initialize_nonser()

        @self.controller
        def player_controller(event):
            if event.type == TICK:
                self["credits"] += self.credit_rate
                self["gains"][0] += self.credit_rate
                self["average_timer"] += 1
                if self.average_timer >= 240:
                    self["average_timer"] = 0
                    self.calculate_averages()

    def add_resources(self, science, art, literature, philosophy, multiplier):
        modifier = 1 + multiplier
        self["science"] += science * modifier
        self["gains"][1] += science * modifier
        self["art"] += art * modifier
        self["gains"][2] += art * modifier
        self["literature"] += literature * modifier
        self["gains"][3] += literature * modifier
        self["philosophy"] += philosophy * modifier
        self["gains"][4] += philosophy * modifier

    def show_stats(self, screen, font):
        text = font.render(f"credits: {self.credits.as_int()} ({self.averages[0]})", True, (255, 255, 255), "black")
        text_rect = text.get_rect(topleft=(10, 10))
        screen.blit(text, text_rect)

        text = font.render(f"science: {self.science.as_int()} ({self.averages[1]})", True, (255, 255, 255), "black")
        text_rect = text.get_rect(topleft=(10, 40))
        screen.blit(text, text_rect)

        text = font.render(f"art: {self.art.as_int()} ({self.averages[2]})", True, (255, 255, 255), "black")
        text_rect = text.get_rect(topleft=(10, 70))
        screen.blit(text, text_rect)

        text = font.render(f"literature: {self.literature.as_int()} ({self.averages[3]})", True, (255, 255, 255), "black")
        text_rect = text.get_rect(topleft=(10, 100))
        screen.blit(text, text_rect)

        text = font.render(f"philosophy: {self.philosophy.as_int()} ({self.averages[4]})", True, (255, 255, 255), "black")
        text_rect = text.get_rect(topleft=(10, 130))
        screen.blit(text, text_rect)

    def convert(self):
        self["science"] = self.science.convert()
        self["art"] = self.art.convert()
        self["literature"] = self.literature.convert()
        self["philosophy"] = self.philosophy.convert()
        self["credits"] = self.credits.convert()
        self["credit_rate"] = self.credit_rate.convert()
        self["gains"] = [a.convert() for a in self.gains]
        self["averages"] = [a.convert().truncated(4).rounded(3) for a in self.averages]

    def calculate_averages(self):
        self["averages"] = [(gain / Td(8)).truncated(4).rounded(3) for gain in self.gains]
        self["gains"] = [Td.zero() for _ in range(5)]
