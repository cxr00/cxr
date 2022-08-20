
from spectrum8.components import Rule, DotFrame
import pygame
import random
import os


def main():
    pygame.init()
    os.environ['SDL_VIDEO_WINDOW_POS'] = '100,100'

    color = [random.randint(0, 255) for _ in range(3)]
    print(color)
    length, width = 100, 100
    rule = Rule.cxr10  # See dotframe.Rule
    dot = [1, 2, 2, 1]  # Will be dotted with stored Boards via DotFrame
    code = "f7"  # Starting pattern

    frame = DotFrame(length, width, dot, rule=rule, code=code)
    screen = pygame.display.set_mode((length * DotFrame.dot_size, width * DotFrame.dot_size))

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
                if event.key == pygame.K_SPACE:
                    update = not update
            if event.type == pygame.QUIT:
                run = False
            elif event.type == TICK:
                frame.draw(screen, color)

        pygame.display.update()


if __name__ == "__main__":
    main()
