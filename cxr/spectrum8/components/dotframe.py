import pygame
import random


class Rule:
    default = ((3,), (2, 3))  # Conway's rule
    conway_adj = ((2,), (2, 3))  # Adjusted Conway's rule
    cxr00 = ((2, ), (1, 2, 3))
    cxr01 = ((2, 3), (1, 3, 4, 5))
    cxr02 = ((1, 2), (2, 3, 4))
    cxr03 = ((2, 4, 5, 7), (1, 3, 6, 8))  # Quite chaotic
    cxr04 = ((4,), (3, 4, 5))
    cxr05 = ((3, 4), (2, 4, 5))
    cxr06 = ((2, 4, 5), (1, 2, 3, 4))
    cxr07 = ((2, 3, 4, 5, 6, 7), (2, 3, 4, 5, 6, 7))


class Board:
    """
    Contains the grid of cellular automata at a particular point in time
    """

    def __init__(self, length, width):
        self.length = length
        self.width = width
        self.board = [[0 for _ in range(width)] for __ in range(length)]

    def __iter__(self):
        return iter(self.board)

    def __getitem__(self, item):
        return self.board[item]

    def __setitem__(self, key, value):
        self[key] = value

    def count_neighbors(self, y, x):
        def particular(j, k):
            if 0 <= y + j < self.length:
                if 0 <= x + k < self.width:
                    if self[y+j][x+k] == 1:
                        return 1
            return 0

        neighbors = 0
        for j in range(-1, 2):
            for k in range(-1, 2):
                if not (j == k == 0):
                    neighbors += particular(j, k)
        return neighbors

    def update(self, rule):
        out = Board(self.length, self.width)
        for y in range(self.length):
            for x in range(self.width):
                neighbors = self.count_neighbors(y, x)
                if self[y][x]:
                    if neighbors in rule[1]:
                        out[y][x] = 1
                    else:
                        out[y][x] = 0
                elif neighbors in rule[0]:
                    out[y][x] = 1
                else:
                    out[y][x] = 0
        return [out]

    def initialize(self, code):
        t = code[0]
        if t == "r":  # Random
            for i in range(int(code[1:])):
                x, y = random.randint(0, self.width - 1), random.randint(0, self.length - 1)
                self[y][x] = random.randint(0, 1)
        elif t == "s":  # Square
            size = int(code[1:])
            x_range = -size // 2, size // 2 + 1
            y_range = -size // 2, size // 2 + 1

            for x in range(*x_range):
                for y in range(*y_range):
                    if x == (-size // 2) or x == (size // 2) or y == (-size // 2) or y == (size // 2):
                        self[self.length // 2 + y][self.width // 2 + x] = 1
        elif t == "f":  # Filled square
            size = int(code[1:])
            x_range = -size // 2, size // 2 + 1
            y_range = -size // 2, size // 2 + 1
            for x in range(*x_range):
                for y in range(*y_range):
                    self[self.length // 2 + y][self.width // 2 + x] = 1
        elif t == "b":  # Border
            for x in range(self.width):
                self[0][x] = 1
            for y in range(1, self.length):
                self[y][0] = self[y][-1] = 1
            for x in range(self.width):
                self[-1][x] = 1
        elif t == "x":  # Cross
            size = int(code[1:])
            for y in range(self.length):
                for i in range(size):
                    if self.length > y + i >= 0:
                        self[y][y+i] = 1
                    if self.length > y - i - 1 >= -2:
                        self[self.length - y - i - 1][y] = 1


class DotFrame:
    """
    A DotFrame uses a simple dot product to present
    a unique perspective for a cellular automata
    """

    dot_size = 7  # Size of each cell
    surface = pygame.Surface((dot_size, dot_size))  # Reusable surface
    surface.fill((255, 255, 255))

    def __init__(self, length, width, depth, rule=Rule.default, dot=None, code="r"):
        self.depth = depth
        if dot is None:
            self.dot = [1 for _ in range(self.depth)]
        elif len(dot) > depth:
            self.dot = dot[:self.depth]
        else:
            self.dot = dot
            self.depth = len(dot)
        self.span = sum(self.dot)

        self.length = length
        self.width = width
        self.rule = rule
        self.boards = [Board(self.length, self.width) for _ in range(self.depth)]
        self.boards[-1].initialize(code)

    def __getitem__(self, item):
        return self.boards[-1][item]

    def __setitem__(self, key, value):
        self.boards[key] = value

    def __iter__(self):
        return iter(self.boards)

    def draw(self, screen, color):
        size = DotFrame.dot_size
        surf = DotFrame.surface

        def adj_color(n):
            return color[0] // (self.span - n + 1),\
                color[1] // (self.span - n + 1),\
                color[2] // (self.span - n + 1)

        lerp = self.do_lerp()
        for x in range(self.width):
            for y in range(self.length):
                surf.fill((adj_color(lerp[y][x])))
                screen.blit(surf, pygame.Rect((x*size, y*size, size, size)))

    def update(self):
        self.boards = self.boards[1:] + self.boards[-1].update(self.rule)

    def do_lerp(self):
        out = Board(self.length, self.width)
        for x in range(self.width):
            for y in range(self.length):
                out[y][x] = sum(board[y][x] * self.dot[k] for k, board in enumerate(self))
        return out
