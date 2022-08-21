import pygame

from thinktank import TICK
from cxr.state.state import StateManager


class Pod:

    def __init__(self, pos):
        self.pos = pos
        self.surf = pygame.Surface((25, 25))
        self.surf.fill((255, 255, 255))
        self.brain = None

    def collidepoint(self, pos):
        if self.surf.get_rect(topleft=self.pos).collidepoint(pos):
            return True
        return False

    def set_brain(self, brain):
        self.brain = brain
        self.surf.fill((100, 100, 100))

    def draw(self, screen):
        screen.blit(self.surf, self.pos)


class Tank(StateManager):

    def __init__(self, key, name):
        super().__init__(key, name)
        self.initialize()

    def initialize(self):

        self.nonser("pods", [])
        self.nonser("neuron_panel", None)

        self.pods.append(Pod((100, 200)))
        self.pods.append(Pod((150, 200)))
        self.pods.append(Pod((200, 200)))
        self.pods.append(Pod((100, 250)))
        self.pods.append(Pod((150, 250)))
        self.pods.append(Pod((200, 250)))
        # self.pods.append(Pod((100, 300)))
        # self.pods.append(Pod((150, 300)))
        # self.pods.append(Pod((200, 300)))

        @self.controller
        def tank_controller(event):
            for pod in self.pods:
                if pod.brain:
                    if event.type == TICK:
                        pod.brain(event)
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if pod.collidepoint(event.pos):
                            self.neuron_panel.set_neuron(pod.brain.neuron)
            self.neuron_panel(event)

    def add_brain(self, brain):
        for pod in self.pods:
            if not pod.brain:
                pod.set_brain(brain)
                if not self.neuron_panel.neuron:
                    self.neuron_panel.set_neuron(pod.brain.neuron)
                break

    def set_neuron_panel(self, neuron_panel):
        self["neuron_panel"] = neuron_panel

    def draw(self, screen):
        for pod in self.pods:
            pod.draw(screen)
