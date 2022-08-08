import pygame

from cxr.state.state import StateManager, StateManagerReference

from thinktank import screen, font, clock, FPS, TICK, ACCUMULATE
from thinktank.components import NeuronPanel, Brain, Player, Tank, Grants

import cxr.math.base36


def main():
    StateManagerReference.initialize("local\\thinktank")

    # UI
    tank = StateManager.generate("tank", Tank, "tank")
    neuron_panel = StateManager.generate("neuron_panel", NeuronPanel, "neuron_panel")

    # Game objects
    player = StateManager.generate("player", Player, "player")
    brains = []
    # brain = StateManager.generate("brain", Brain, "brain")
    # brain2 = StateManager.generate("brain", Brain, "brain2")
    # brain3 = StateManager.generate("brain", Brain, "brain3")
    grants = StateManager.generate("grants", Grants, "grants")

    # UI connections
    tank.set_neuron_panel(neuron_panel)
    neuron_panel.set_player(player)

    # Test brains
    # tank.add_brain(brain)
    # tank.add_brain(brain2)
    # tank.add_brain(brain3)

    # Player connections
    # brain.set_player(player)
    # brain2.set_player(player)
    # brain3.set_player(player)
    grants.set_player(player)

    run = True
    while run:
        clock.tick(FPS)
        pygame.event.post(pygame.event.Event(TICK))
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                change = False
                if event.key == pygame.K_UP:
                    if cxr.math.base36.default_base < 36:
                        cxr.math.base36.default_base += 1
                        change = True
                elif event.key == pygame.K_DOWN:
                    if cxr.math.base36.default_base > 2:
                        cxr.math.base36.default_base -= 1
                        change = True
                elif event.key == pygame.K_b:
                    if len(brains) < len(tank.pods):
                        new_brain = StateManager.generate("brain", Brain, f"brain{len(brains)}")
                        new_brain.set_player(player)
                        brains.append(new_brain)
                        tank.add_brain(new_brain)
                if change:
                    player.convert()
                    for brain in brains:
                        brain.convert()
                    NeuronPanel.convert()
                    grants.convert()
            elif event.type == ACCUMULATE:
                grants(event)

            tank(event)
            player(event)

        screen.fill("black")

        player.show_stats(screen, font)
        if neuron_panel.neuron:
            neuron_panel.draw(screen, font)
        tank.draw(screen)
        grants.draw(screen, font)

        text = font.render(f"base: {cxr.math.base36.default_base}", True, (255, 255, 255), "black")
        text_rect = text.get_rect(topleft=(500, 300))
        screen.blit(text, text_rect)

        text = font.render(str(clock.get_fps()), True, (255, 255, 255), "black")
        text_rect = text.get_rect(topleft=(600, 300))
        screen.blit(text, text_rect)

        text = font.render(str(grants.progress_time), True, (255, 255, 255), "black")
        text_rect = text.get_rect(topleft=(600, 350))
        screen.blit(text, text_rect)

        pygame.display.update()


if __name__ == "__main__":
    main()
