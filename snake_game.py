"""
Simple Snake Game using Pygame
"""

import pygame
import sys
import random
from pydantic import BaseModel, computed_field

# Game Constants
WINDOW_WIDTH = 800  # Fixed window width
WINDOW_HEIGHT = 800  # Fixed window height
GRID_SIZE = 20  # Size of each grid cell in pixels
DEFAULT_BOARD_COLS = 20  # Default number of columns (horizontal cells)
DEFAULT_BOARD_ROWS = 20  # Default number of rows (vertical cells)
MIN_BOARD_SIZE = 6  # Minimum board size
MAX_BOARD_SIZE = 32  # Maximum board size

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GREEN_HEAD = (0, 180, 0)
RED = (255, 0, 0)
GRAY = (40, 40, 40)

# Game Settings
FPS = 60  # Frame rate for rendering
SNAKE_MOVE_INTERVAL = 1000 // 6  # Snake moves 6 times per second (166.67ms)

# Game Modes
CLASSIC = "classic"
RELAXED = "relaxed"

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class GameConfig(BaseModel):
    mode: str = CLASSIC
    board_cols: int = DEFAULT_BOARD_COLS
    board_rows: int = DEFAULT_BOARD_ROWS

    @computed_field
    @property
    def offset_x(self) -> int:
        return (WINDOW_WIDTH - self.board_cols * GRID_SIZE) // 2

    @computed_field
    @property
    def offset_y(self) -> int:
        return (WINDOW_HEIGHT - self.board_rows * GRID_SIZE) // 2


class TextLabel:
    def __init__(self, text, size, x, y, color=WHITE):
        self.text = text
        self.size = size
        self.x = x
        self.y = y
        self.color = color

    def update(self, text=None, color=None):
        if text is not None:
            self.text = text
        if color is not None:
            self.color = color

    def draw(self, screen):
        font = pygame.font.Font(None, self.size)
        surface = font.render(self.text, True, self.color)
        rect = surface.get_rect(center=(self.x, self.y))
        screen.blit(surface, rect)


class Snake:
    def __init__(self, config):
        self.config = config
        self.body = [(config.board_cols // 2, config.board_rows // 2)]
        self.direction = RIGHT
        self.last_moved_direction = RIGHT
        self.grow_pending = False

    def move(self):
        head_x, head_y = self.body[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

        self.body.insert(0, new_head)

        if not self.grow_pending:
            self.body.pop()
        else:
            self.grow_pending = False

        self.last_moved_direction = self.direction

    def grow(self):
        self.grow_pending = True

    def change_direction(self, new_direction):
        opposite_of_last_move = (
            self.last_moved_direction[0] * -1,
            self.last_moved_direction[1] * -1,
        )
        if new_direction != opposite_of_last_move:
            self.direction = new_direction
            return True
        return False

    def check_collision(self):
        head_x, head_y = self.body[0]
        if (
            head_x < 0
            or head_x >= self.config.board_cols
            or head_y < 0
            or head_y >= self.config.board_rows
        ):
            return True
        if self.body[0] in self.body[1:]:
            return True
        return False

    def can_move(self, direction):
        head_x, head_y = self.body[0]
        new_head = (head_x + direction[0], head_y + direction[1])
        if (
            new_head[0] < 0
            or new_head[0] >= self.config.board_cols
            or new_head[1] < 0
            or new_head[1] >= self.config.board_rows
        ):
            return False
        if new_head in self.body:
            return False
        return True

    def draw(self, surface):
        padding = 3
        body_size = GRID_SIZE - 2 * padding
        ox, oy = self.config.offset_x, self.config.offset_y

        # Draw bridges between consecutive segments
        for i in range(len(self.body) - 1):
            gx1, gy1 = self.body[i]
            gx2, gy2 = self.body[i + 1]
            if gy1 == gy2:  # horizontal
                min_gx = min(gx1, gx2)
                bx = ox + min_gx * GRID_SIZE + padding + body_size
                by = oy + gy1 * GRID_SIZE + padding
                pygame.draw.rect(
                    surface, GREEN, pygame.Rect(bx, by, 2 * padding, body_size)
                )
            else:  # vertical
                min_gy = min(gy1, gy2)
                bx = ox + gx1 * GRID_SIZE + padding
                by = oy + min_gy * GRID_SIZE + padding + body_size
                pygame.draw.rect(
                    surface, GREEN, pygame.Rect(bx, by, body_size, 2 * padding)
                )

        # Draw core body for each segment
        for i, (gx, gy) in enumerate(self.body):
            x = ox + gx * GRID_SIZE + padding
            y = oy + gy * GRID_SIZE + padding
            color = GREEN_HEAD if i == 0 else GREEN
            pygame.draw.rect(surface, color, pygame.Rect(x, y, body_size, body_size))


class Food:
    """Food class for the game"""

    def __init__(self, config):
        self.config = config
        self.position = (0, 0)
        self.randomize_position()

    def randomize_position(self):
        self.position = (
            random.randint(0, self.config.board_cols - 1),
            random.randint(0, self.config.board_rows - 1),
        )

    def draw(self, surface):
        pygame.draw.rect(
            surface, RED, grid_rect(self.position[0], self.position[1], self.config)
        )


def grid_rect(x, y, config):
    return pygame.Rect(
        config.offset_x + x * GRID_SIZE + 1,
        config.offset_y + y * GRID_SIZE + 1,
        GRID_SIZE - 1,
        GRID_SIZE - 1,
    )


def draw_grid(surface, config):
    board_pixel_width = config.board_cols * GRID_SIZE
    board_pixel_height = config.board_rows * GRID_SIZE
    for x in range(0, board_pixel_width + 1, GRID_SIZE):
        pygame.draw.line(
            surface,
            GRAY,
            (config.offset_x + x, config.offset_y),
            (config.offset_x + x, config.offset_y + board_pixel_height),
        )
    for y in range(0, board_pixel_height + 1, GRID_SIZE):
        pygame.draw.line(
            surface,
            GRAY,
            (config.offset_x, config.offset_y + y),
            (config.offset_x + board_pixel_width, config.offset_y + y),
        )


class Screen:
    """Base class for all screens."""

    def __init__(self, manager):
        self.manager = manager

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def draw(self, surface):
        pass

    def on_enter(self):
        pass

    def on_exit(self):
        pass


class ScreenManager:
    """Stack-based screen manager. The top screen receives input.
    All screens in the stack are drawn bottom-to-top (for overlay support).
    """

    def __init__(self, surface, clock):
        self.surface = surface
        self.clock = clock
        self._stack = []
        self.running = True

    @property
    def top(self):
        return self._stack[-1] if self._stack else None

    def push(self, screen):
        self._stack.append(screen)
        screen.on_enter()

    def pop(self):
        if self._stack:
            self._stack[-1].on_exit()
            self._stack.pop()
            if self._stack:
                self._stack[-1].on_enter()

    def replace(self, screen):
        if self._stack:
            self._stack[-1].on_exit()
            self._stack[-1] = screen
        else:
            self._stack.append(screen)
        screen.on_enter()

    def replace_all(self, screen):
        for s in reversed(self._stack):
            s.on_exit()
        self._stack.clear()
        self._stack.append(screen)
        screen.on_enter()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                if self.top:
                    self.top.handle_event(event)
            if not self.running:
                break
            if self.top:
                self.top.update()
            for screen in self._stack:
                screen.draw(self.surface)
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


class ModeSelectionScreen(Screen):
    def __init__(self, manager):
        super().__init__(manager)
        self.selected_mode = CLASSIC
        self.cursor_position = 0  # 0=classic, 1=relaxed, 2=cols, 3=rows
        self.board_cols = DEFAULT_BOARD_COLS
        self.board_rows = DEFAULT_BOARD_ROWS

        self.label_title = TextLabel("SNAKE GAME", 72, WINDOW_WIDTH // 2, 120)
        self.label_hint = TextLabel(
            "Arrow keys, ENTER on mode to start", 24, WINDOW_WIDTH // 2, 180, GRAY
        )
        self.label_mode_header = TextLabel("GAME MODE", 48, WINDOW_WIDTH // 2, 260)
        self.label_size_header = TextLabel("BOARD SIZE", 48, WINDOW_WIDTH // 2, 470)
        self.label_classic = TextLabel(
            "  CLASSIC MODE", 38, WINDOW_WIDTH // 2, 320, GRAY
        )
        self.label_relaxed = TextLabel(
            "  RELAXED MODE", 38, WINDOW_WIDTH // 2, 370, GRAY
        )
        self.label_cols = TextLabel(
            "  Columns: 20 cells", 32, WINDOW_WIDTH // 2, 530, GRAY
        )
        self.label_rows = TextLabel(
            "  Rows:    20 cells", 32, WINDOW_WIDTH // 2, 580, GRAY
        )

    def on_enter(self):
        pygame.display.set_caption("Simple Snake Game - Settings")

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_UP:
            self.cursor_position = (self.cursor_position - 1) % 4
            if self.cursor_position == 0:
                self.selected_mode = CLASSIC
            elif self.cursor_position == 1:
                self.selected_mode = RELAXED

        elif event.key == pygame.K_DOWN:
            self.cursor_position = (self.cursor_position + 1) % 4
            if self.cursor_position == 0:
                self.selected_mode = CLASSIC
            elif self.cursor_position == 1:
                self.selected_mode = RELAXED

        elif event.key == pygame.K_LEFT:
            shift_pressed = pygame.key.get_mods() & pygame.KMOD_SHIFT
            step = 10 if shift_pressed else 1
            if self.cursor_position == 2:
                self.board_cols = max(MIN_BOARD_SIZE, self.board_cols - step)
            elif self.cursor_position == 3:
                self.board_rows = max(MIN_BOARD_SIZE, self.board_rows - step)

        elif event.key == pygame.K_RIGHT:
            shift_pressed = pygame.key.get_mods() & pygame.KMOD_SHIFT
            step = 10 if shift_pressed else 1
            if self.cursor_position == 2:
                self.board_cols = min(MAX_BOARD_SIZE, self.board_cols + step)
            elif self.cursor_position == 3:
                self.board_rows = min(MAX_BOARD_SIZE, self.board_rows + step)

        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.cursor_position in (0, 1):
                config = GameConfig(
                    mode=self.selected_mode,
                    board_cols=self.board_cols,
                    board_rows=self.board_rows,
                )
                self.manager.replace(GameplayScreen(self.manager, config))

    def draw(self, surface):
        surface.fill(BLACK)

        cursor_classic = "> " if self.cursor_position == 0 else "  "
        classic_color = WHITE if self.cursor_position == 0 else GRAY
        self.label_classic.update(cursor_classic + "CLASSIC MODE", classic_color)

        cursor_relaxed = "> " if self.cursor_position == 1 else "  "
        relaxed_color = WHITE if self.cursor_position == 1 else GRAY
        self.label_relaxed.update(cursor_relaxed + "RELAXED MODE", relaxed_color)

        cursor_cols = "> " if self.cursor_position == 2 else "  "
        cols_color = WHITE if self.cursor_position == 2 else GRAY
        self.label_cols.update(
            cursor_cols + f"Columns: {self.board_cols} cells", cols_color
        )

        cursor_rows = "> " if self.cursor_position == 3 else "  "
        rows_color = WHITE if self.cursor_position == 3 else GRAY
        self.label_rows.update(
            cursor_rows + f"Rows:    {self.board_rows} cells", rows_color
        )

        self.label_title.draw(surface)
        self.label_hint.draw(surface)
        self.label_mode_header.draw(surface)
        self.label_classic.draw(surface)
        self.label_relaxed.draw(surface)
        self.label_size_header.draw(surface)

        box_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, 510, 300, 90)
        pygame.draw.rect(surface, GRAY, box_rect, 2)

        self.label_cols.draw(surface)
        self.label_rows.draw(surface)


class GameplayScreen(Screen):
    def __init__(self, manager, config):
        super().__init__(manager)
        self.config = config
        self.snake = None
        self.food = None
        self.score = 1
        self.game_over = False
        self.game_complete = False
        self._should_move = False
        self.last_move_time = 0

        self.label_score = TextLabel("Score: 1", 36, WINDOW_WIDTH // 2, 30)
        self.label_mode = TextLabel(
            f"Mode: {config.mode.upper()}", 28, 80, WINDOW_HEIGHT - 20, GRAY
        )

        self.reset_game()

    def on_enter(self):
        pygame.display.set_caption("Simple Snake Game")

    def reset_game(self):
        self.snake = Snake(self.config)
        self.food = Food(self.config)
        while self.food.position in self.snake.body:
            self.food.randomize_position()
        self.score = 1
        self.game_over = False
        self.game_complete = False
        self._should_move = False
        self.last_move_time = pygame.time.get_ticks()

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        direction_input = None

        if event.key == pygame.K_UP:
            direction_input = UP
        elif event.key == pygame.K_DOWN:
            direction_input = DOWN
        elif event.key == pygame.K_LEFT:
            direction_input = LEFT
        elif event.key == pygame.K_RIGHT:
            direction_input = RIGHT
        elif event.key == pygame.K_q:
            self.game_over = True
            self.manager.push(OverlayMenuScreen(self.manager, self, "GAME OVER!"))
            return

        if direction_input and not self.game_over:
            if self.config.mode == CLASSIC:
                self.snake.change_direction(direction_input)
            elif self.config.mode == RELAXED:
                if self.snake.change_direction(direction_input):
                    if self.snake.can_move(direction_input):
                        self._should_move = True

    def update(self):
        if self.game_over or self.game_complete:
            return

        if self.config.mode == CLASSIC:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_move_time >= SNAKE_MOVE_INTERVAL:
                self.last_move_time = current_time
                self._should_move = True

        if self._should_move:
            self._should_move = False
            self._do_move()

    def _do_move(self):
        next_head = (
            self.snake.body[0][0] + self.snake.direction[0],
            self.snake.body[0][1] + self.snake.direction[1],
        )

        # Check collision BEFORE moving so the snake stays within the board
        if self.config.mode == CLASSIC:
            cols, rows = self.config.board_cols, self.config.board_rows
            wall_hit = (
                next_head[0] < 0
                or next_head[0] >= cols
                or next_head[1] < 0
                or next_head[1] >= rows
            )
            if wall_hit:
                self.game_over = True
                self.manager.push(
                    OverlayMenuScreen(self.manager, self, "GAME OVER!")
                )
                return
            will_eat = next_head == self.food.position
            body_after = self.snake.body if will_eat else self.snake.body[:-1]
            if next_head in body_after:
                self.game_over = True
                self.manager.push(
                    OverlayMenuScreen(self.manager, self, "GAME OVER!")
                )
                return

        if next_head == self.food.position:
            self.snake.grow()

        self.snake.move()

        if self.snake.body[0] == self.food.position:
            self.score += 1
            if len(self.snake.body) >= self.config.board_cols * self.config.board_rows:
                self.game_complete = True
                self.manager.push(
                    OverlayMenuScreen(
                        self.manager, self, "CONGRATULATIONS!", "Board Complete!"
                    )
                )
            else:
                self.food.randomize_position()
                while self.food.position in self.snake.body:
                    self.food.randomize_position()

    def draw(self, surface):
        surface.fill(BLACK)
        draw_grid(surface, self.config)
        self.snake.draw(surface)
        if not self.game_complete:
            self.food.draw(surface)

        self.label_score.update(f"Score: {self.score}")
        self.label_score.draw(surface)
        self.label_mode.draw(surface)


class OverlayMenuScreen(Screen):
    """Rendered on top of GameplayScreen. Does NOT fill the background."""

    def __init__(self, manager, gameplay, title, subtitle=None):
        super().__init__(manager)
        self.gameplay = gameplay
        self.title = title
        self.subtitle = subtitle
        self.menu_position = 0  # 0=restart, 1=main menu

        center_y = WINDOW_HEIGHT // 2
        self.label_title = TextLabel(title, 72, WINDOW_WIDTH // 2, center_y - 80)
        self.label_subtitle = TextLabel(
            subtitle or "", 48, WINDOW_WIDTH // 2, center_y - 20
        )
        self.label_restart = TextLabel("> Restart", 36, WINDOW_WIDTH // 2, 0, WHITE)
        self.label_menu = TextLabel("  Main Menu", 36, WINDOW_WIDTH // 2, 0, GRAY)
        self.label_hint = TextLabel(
            "Press R to restart, ENTER to confirm", 24, WINDOW_WIDTH // 2, 0, GRAY
        )

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_UP, pygame.K_DOWN):
            self.menu_position = 1 - self.menu_position
        elif event.key == pygame.K_RETURN:
            if self.menu_position == 0:
                self._restart()
            else:
                self._main_menu()
        elif event.key == pygame.K_r:
            self._restart()

    def _restart(self):
        self.manager.pop()
        self.gameplay.reset_game()

    def _main_menu(self):
        self.manager.replace_all(ModeSelectionScreen(self.manager))

    def draw(self, surface):
        center_y = WINDOW_HEIGHT // 2

        self.label_title.draw(surface)

        if self.subtitle:
            self.label_subtitle.draw(surface)
            y_base = center_y + 40
        else:
            y_base = center_y + 20

        cursor_restart = "> " if self.menu_position == 0 else "  "
        cursor_menu = "> " if self.menu_position == 1 else "  "
        restart_color = WHITE if self.menu_position == 0 else GRAY
        menu_color = WHITE if self.menu_position == 1 else GRAY

        self.label_restart.update(cursor_restart + "Restart", restart_color)
        self.label_restart.y = y_base
        self.label_menu.update(cursor_menu + "Main Menu", menu_color)
        self.label_menu.y = y_base + 40
        self.label_hint.y = y_base + 90

        self.label_restart.draw(surface)
        self.label_menu.draw(surface)
        self.label_hint.draw(surface)


def main():
    pygame.init()
    surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    manager = ScreenManager(surface, clock)
    manager.push(ModeSelectionScreen(manager))
    manager.run()


if __name__ == "__main__":
    main()
