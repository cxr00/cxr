
from cxr.spectrum8.components import Rule, LFrame
import pygame


def main():
    pygame.init()
    color = 178, 72, 72
    # color = 46, 148, 244

    l, w = 120, 120
    d = 1  # How many frames back the LFrame will track
    lerp = [1]  # Will be dotted with stored Boards via LFrame
    code = "s10"  # Starting conditions
    frame = LFrame(l, w, d, rule=Rule.cxr00, lerp=lerp, code=code)
    screen = pygame.display.set_mode((l * LFrame.dot_size, w * LFrame.dot_size))

    FPS = 10
    clock = pygame.time.Clock()
    TICK = pygame.event.custom_type()

    run = True
    while run:
        frame.update()

        clock.tick(FPS)
        pygame.event.post(pygame.event.Event(TICK))
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False
            elif event.type == TICK:
                frame.draw(screen, color)

        pygame.display.update()


if __name__ == "__main__":
    main()
