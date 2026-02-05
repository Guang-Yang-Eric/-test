import sys
import random

import pygame
from PySide6 import QtCore, QtGui, QtWidgets


CELL_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE
TICK_MS = 500
SCORE_PER_LINE = 100

SHAPES = [
    [[[1, 1, 1, 1]], [[1], [1], [1], [1]]],
    [[[1, 1], [1, 1]]],
    [[[0, 1, 0], [1, 1, 1]], [[1, 0], [1, 1], [1, 0]], [[1, 1, 1], [0, 1, 0]], [[0, 1], [1, 1], [0, 1]]],
    [[[1, 0, 0], [1, 1, 1]], [[1, 1], [1, 0], [1, 0]], [[1, 1, 1], [0, 0, 1]], [[0, 1], [0, 1], [1, 1]]],
    [[[0, 0, 1], [1, 1, 1]], [[1, 0], [1, 0], [1, 1]], [[1, 1, 1], [1, 0, 0]], [[1, 1], [0, 1], [0, 1]]],
    [[[1, 1, 0], [0, 1, 1]], [[0, 1], [1, 1], [1, 0]]],
    [[[0, 1, 1], [1, 1, 0]], [[1, 0], [1, 1], [0, 1]]],
]

COLORS = [
    (0, 0, 0),
    (0, 255, 255),
    (255, 255, 0),
    (128, 0, 128),
    (255, 165, 0),
    (0, 0, 255),
    (0, 255, 0),
    (255, 0, 0),
]


class TetrisGame:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_shape = None
        self.current_color = 0
        self.rotation_index = 0
        self.position = [0, 0]
        self.game_over = False
        self.score = 0
        self.spawn_piece()

    def spawn_piece(self):
        shape_index = random.randint(0, len(SHAPES) - 1)
        self.current_shape = SHAPES[shape_index]
        self.current_color = shape_index + 1
        self.rotation_index = 0
        self.position = [GRID_WIDTH // 2 - 2, 0]
        if self.check_collision(self.position, self.rotation_index):
            self.game_over = True

    def shape_matrix(self, rotation_index=None):
        if rotation_index is None:
            rotation_index = self.rotation_index
        return self.current_shape[rotation_index]

    def check_collision(self, position, rotation_index):
        matrix = self.shape_matrix(rotation_index)
        for y, row in enumerate(matrix):
            for x, cell in enumerate(row):
                if not cell:
                    continue
                grid_x = position[0] + x
                grid_y = position[1] + y
                if grid_x < 0 or grid_x >= GRID_WIDTH or grid_y >= GRID_HEIGHT:
                    return True
                if grid_y >= 0 and self.grid[grid_y][grid_x]:
                    return True
        return False

    def lock_piece(self):
        matrix = self.shape_matrix()
        for y, row in enumerate(matrix):
            for x, cell in enumerate(row):
                if cell:
                    grid_x = self.position[0] + x
                    grid_y = self.position[1] + y
                    if 0 <= grid_y < GRID_HEIGHT:
                        self.grid[grid_y][grid_x] = self.current_color
        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        new_grid = [row for row in self.grid if any(cell == 0 for cell in row)]
        cleared = GRID_HEIGHT - len(new_grid)
        while len(new_grid) < GRID_HEIGHT:
            new_grid.insert(0, [0 for _ in range(GRID_WIDTH)])
        self.grid = new_grid
        if cleared:
            self.score += cleared * SCORE_PER_LINE
        return cleared

    def move(self, dx, dy):
        if self.game_over:
            return
        new_pos = [self.position[0] + dx, self.position[1] + dy]
        if not self.check_collision(new_pos, self.rotation_index):
            self.position = new_pos
        elif dy > 0:
            self.lock_piece()

    def rotate(self):
        if self.game_over:
            return
        new_rotation = (self.rotation_index + 1) % len(self.current_shape)
        if not self.check_collision(self.position, new_rotation):
            self.rotation_index = new_rotation

    def step(self):
        if self.game_over:
            return
        self.move(0, 1)


class TetrisWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        pygame.init()
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.game = TetrisGame()
        self.font = pygame.font.SysFont(
            ["Digital-7", "Digital-7 Mono", "DS-Digital", "Courier New"],
            22,
        )
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(TICK_MS)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def update_game(self):
        self.game.step()
        self.update()

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_A:
            self.game.move(-1, 0)
        elif key == QtCore.Qt.Key_D:
            self.game.move(1, 0)
        elif key == QtCore.Qt.Key_S:
            self.game.move(0, 1)
        elif key == QtCore.Qt.Key_W:
            self.game.rotate()
        elif key == QtCore.Qt.Key_R and self.game.game_over:
            self.game = TetrisGame()
        self.update()

    def paintEvent(self, event):
        self.surface.fill((20, 20, 20))
        self.draw_grid()
        self.draw_piece()
        self.draw_score()
        if self.game.game_over:
            self.draw_game_over()
        image = self.surface_to_image()
        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, image)
        painter.end()

    def draw_grid(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color_index = self.game.grid[y][x]
                if color_index:
                    self.draw_cell(x, y, COLORS[color_index])
                pygame.draw.rect(
                    self.surface,
                    (40, 40, 40),
                    (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                    1,
                )

    def draw_piece(self):
        matrix = self.game.shape_matrix()
        for y, row in enumerate(matrix):
            for x, cell in enumerate(row):
                if cell:
                    draw_x = self.game.position[0] + x
                    draw_y = self.game.position[1] + y
                    if draw_y >= 0:
                        self.draw_cell(draw_x, draw_y, COLORS[self.game.current_color])

    def draw_cell(self, x, y, color):
        pygame.draw.rect(
            self.surface,
            color,
            (x * CELL_SIZE + 1, y * CELL_SIZE + 1, CELL_SIZE - 2, CELL_SIZE - 2),
        )

    def draw_game_over(self):
        font = pygame.font.SysFont("Arial", 24)
        text = font.render("Game Over - Press R to Restart", True, (255, 255, 255))
        rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.surface.blit(text, rect)

    def draw_score(self):
        score_text = self.font.render(f"SCORE {self.game.score:05d}", True, (0, 255, 150))
        self.surface.blit(score_text, (8, 6))

    def surface_to_image(self):
        raw = pygame.image.tostring(self.surface, "RGB")
        image = QtGui.QImage(raw, WINDOW_WIDTH, WINDOW_HEIGHT, QtGui.QImage.Format_RGB888)
        return image


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    widget = TetrisWidget()
    window.setCentralWidget(widget)
    window.setWindowTitle("PySide6 + pygame Tetris")
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
