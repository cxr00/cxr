
from cxr.spectrum8.components import Rule, LFrame
import pygame
import random


def main():
    pygame.init()
    # color = 178, 72, 72
    # color = 46, 148, 244
    # color = 255, 255, 255
    color = [random.randint(0, 255) for _ in range(3)]
    print(color)

    l, w = 120, 120
    d = 1  # How many frames back the LFrame will track
    lerp = [1]  # Will be dotted with stored Boards via LFrame
    code = "x1"  # Starting conditions
    frame = LFrame(l, w, d, rule=Rule.default, lerp=lerp, code=code)
    screen = pygame.display.set_mode((l * LFrame.dot_size + 10, w * LFrame.dot_size + 10))

    FPS = 10
    clock = pygame.time.Clock()
    TICK = pygame.event.custom_type()

    run = True
    update = False
    while run:
        if update:
            frame.update()

        clock.tick(FPS)
        pygame.event.post(pygame.event.Event(TICK))
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                update = not update
            if event.type == pygame.QUIT:
                run = False
            elif event.type == TICK:
                frame.draw(screen, color)

        pygame.display.update()


if __name__ == "__main__":
    main()
