import pygame

from cxr.state.state import StateManager
from cxr.math.base36 import Tridozenal as Td
from thinktank import ACCUMULATE

# growth_rate_modifier = Td(10000)
degeneration_rate_multiplier = Td(650)
soma_growth_point = Td(10000)

resource_prod_rate_multiplier = Td(7)
prod_rate_multiplier = Td(137)


class Button:

    def __init__(self, command, pos):
        self.command = command
        self.pos = pos
        self.rect = pygame.Rect(pos, (120, 30))
        self.player = None
        self.neuron = None

    def set_player(self, player):
        self.player = player

    def set_neuron(self, neuron):
        self.neuron = neuron

    def collidepoint(self, pos):
        if self.rect.collidepoint(pos):
            return True
        return False

    def draw(self, screen, font):
        button_surf = pygame.Surface((120, 30))
        if self.neuron[self.command].can_level_up():
            if self.player.credits >= self.neuron[self.command].cost:
                button_surf.fill((0, 187, 50))
            else:
                button_surf.fill((187, 50, 0))
        else:
            button_surf.fill((50, 50, 50))
        surf_rect = button_surf.get_rect(topleft=self.pos)
        screen.blit(button_surf, surf_rect)

        text = font.render(self.command, True, (255, 255, 255))
        text_rect = text.get_rect(center=surf_rect.center)
        screen.blit(text, text_rect)


class Tooltip:

    def __init__(self, current, neuron):
        self.current = current
        self.neuron = neuron

    def draw(self, screen, font):
        text = font.render(f"Cost: {str(self.neuron[self.current].cost.as_int())}", True, (255, 255, 255), "black")
        text_rect = text.get_rect(center=(650, 460))
        screen.blit(text, text_rect)


class NeuronPanel(StateManager):

    def __init__(self, key, name):
        super().__init__(key, name)
        self.initialize()

    def initialize(self):
        self.nonser("neuron", None)
        self.nonser("player", None)
        self.nonser("tooltip", None)
        self.nonser("current_tooltip", None)

        self.nonser("buttons", [])

        self.buttons.append(Button("soma", (160, 400)))

        self.buttons.append(Button("membrane", (10, 435)))
        self.buttons.append(Button("dendrites", (160, 435)))
        self.buttons.append(Button("hilcock", (310, 435)))

        self.buttons.append(Button("axon", (310, 470)))

        self.buttons.append(Button("terminal", (160, 505)))
        self.buttons.append(Button("ranvier", (310, 505)))
        self.buttons.append(Button("sheath", (460, 505)))

        self.buttons.append(Button("synapse", (160, 540)))

        @self.controller
        def neuron_panel_controller(event):
            if event.type == pygame.MOUSEBUTTONDOWN:
                command = None
                for button in self.buttons:
                    if button.collidepoint(event.pos):
                        command = button.command
                        break
                if command:
                    mouse = pygame.mouse.get_pressed()
                    run = True
                    event = pygame.event.Event(ACCUMULATE)
                    event.count = Td.zero()
                    while run:
                        if mouse[0]:
                            run = False
                        if self.neuron[command].can_level_up():
                            if self.player.credits >= self.neuron[command].cost.as_int():
                                self["player"]["credits"] -= self.neuron[command].cost.as_int()
                                self["neuron"][command].gain_level()
                                if command == "dendrites":
                                    self["neuron"]["soma_growth_rate"] = self.neuron.dendrites.level // Td(5) + Td(1)
                                elif command in ("sheath", "hilcock"):
                                    self["neuron"]["degeneration_reduction"] = (self.neuron.sheath.level + self.neuron.hilcock.level) / degeneration_rate_multiplier
                                elif command == "membrane":
                                    self["neuron"]["max_energy"] += Td(5)
                                elif command in ("axon", "terminal"):
                                    self["neuron"]["brain_production_rate"] = (self.neuron.axon.level / resource_prod_rate_multiplier) * (self.neuron.terminal.level / prod_rate_multiplier)
                                elif command == "ranvier":
                                    self["neuron"]["regeneration_rate"] = Td(2) * (1 + self.neuron.ranvier.level / Td(10))
                                event.count += Td.one()
                            else:
                                run = False
                        else:
                            run = False
                    pygame.event.post(event)
            mouse_pos = pygame.mouse.get_pos()
            for button in self.buttons:
                if button.collidepoint(mouse_pos):
                    if not self.current_tooltip or self.current_tooltip != self.tooltip.current:
                        self["tooltip"] = Tooltip(button.command, self.neuron)
                    break
            else:
                self["tooltip"] = None

    def set_neuron(self, neuron):
        self["neuron"] = neuron
        for button in self.buttons:
            button.set_neuron(neuron)

    def set_player(self, player):
        self["player"] = player
        for button in self.buttons:
            button.set_player(player)

    def draw(self, screen, font):
        for button in self.buttons:
            button.draw(screen, font)
        if self.tooltip:
            self.tooltip.draw(screen, font)
        self.neuron.show_stats(screen, font)

    @staticmethod
    def convert():
        global degeneration_rate_multiplier, prod_rate_multiplier, resource_prod_rate_multiplier
        degeneration_rate_multiplier = degeneration_rate_multiplier.convert()
        prod_rate_multiplier = prod_rate_multiplier.convert()
        resource_prod_rate_multiplier = resource_prod_rate_multiplier.convert()
