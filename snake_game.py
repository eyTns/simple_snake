"""
Simple Snake Game using Pygame
"""

from collections import deque

import pygame
import sys
import random
from pydantic import BaseModel, computed_field

# Game Constants
WINDOW_WIDTH = 800  # Fixed window width
WINDOW_HEIGHT = 800  # Fixed window height
GRID_SIZE = 20  # Size of each grid cell in pixels
DEFAULT_BOARD_WIDTH = 20  # Default board width (horizontal cells)
DEFAULT_BOARD_HEIGHT = 20  # Default board height (vertical cells)
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
CLASSIC = "classic"  # 클래식 모드
RELAXED = "relaxed"  # 릴랙스 모드
MUSEUM = "museum"  # 관람 모드

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class GameConfig(BaseModel):
    mode: str = CLASSIC
    board_width: int = DEFAULT_BOARD_WIDTH
    board_height: int = DEFAULT_BOARD_HEIGHT

    @computed_field
    @property
    def offset_x(self) -> int:
        return (WINDOW_WIDTH - self.board_width * GRID_SIZE) // 2

    @computed_field
    @property
    def offset_y(self) -> int:
        return (WINDOW_HEIGHT - self.board_height * GRID_SIZE) // 2


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
    def __init__(self, config, start_pos=None, start_direction=None):
        self.config = config
        if start_pos is not None:
            self.body = [start_pos]
        else:
            self.body = [(config.board_width // 2, config.board_height // 2)]
        self.direction = start_direction or RIGHT
        self.last_moved_direction = self.direction
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
        if len(self.body) > 1:
            opposite_of_last_move = (
                self.last_moved_direction[0] * -1,
                self.last_moved_direction[1] * -1,
            )
            if new_direction == opposite_of_last_move:
                return False
        self.direction = new_direction
        return True

    def check_collision(self):
        head_x, head_y = self.body[0]
        if (
            head_x < 0
            or head_x >= self.config.board_width
            or head_y < 0
            or head_y >= self.config.board_height
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
            or new_head[0] >= self.config.board_width
            or new_head[1] < 0
            or new_head[1] >= self.config.board_height
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
            random.randint(0, self.config.board_width - 1),
            random.randint(0, self.config.board_height - 1),
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


class MuseumAlgorithm:
    """관람 모드 알고리즘 기반 클래스"""

    name: str = ""
    dynamic: bool = False

    def can_run(self, width: int, height: int) -> bool:
        raise NotImplementedError

    def generate_path(self, width: int, height: int) -> list[tuple[int, int]]:
        raise NotImplementedError

    def constraint_message(self) -> str:
        return ""

    def initialize(
        self, width: int, height: int
    ) -> tuple[tuple[int, int], tuple[int, int]]:
        """동적 알고리즘 초기화. (start_pos, start_dir)을 반환합니다."""
        raise NotImplementedError

    def next_position(
        self, snake_body: list, food_pos: tuple
    ) -> tuple[int, int] | None:
        """다음 이동 위치를 반환합니다. 없으면 None."""
        raise NotImplementedError


class CombAlgorithm(MuseumAlgorithm):
    name = "COMB"

    def can_run(self, width: int, height: int) -> bool:
        return height % 2 == 0

    def constraint_message(self) -> str:
        return "Height must be even"

    def generate_path(self, width: int, height: int) -> list[tuple[int, int]]:
        path = []
        # Phase 1: 왼쪽 열 상승
        for y in range(height - 1, -1, -1):
            path.append((0, y))
        # Phase 2: 나머지 열 지그재그
        for row in range(height):
            if row % 2 == 0:
                for x in range(1, width):
                    path.append((x, row))
            else:
                for x in range(width - 1, 0, -1):
                    path.append((x, row))
        return path


class FishboneAlgorithm(MuseumAlgorithm):
    name = "FISHBONE"
    dynamic = True
    debug = False

    def can_run(self, width: int, height: int) -> bool:
        return height % 2 == 0

    def constraint_message(self) -> str:
        return "Height must be even"

    def initialize(
        self, width: int, height: int
    ) -> tuple[tuple[int, int], tuple[int, int]]:
        self._width = width
        self._height = height
        self._mid = width // 2
        self._num_ribs = height // 2
        self._queue: deque[tuple[int, int]] = deque()
        self._phase = "left"
        self._rib_index = 0
        # 첫 rib을 enqueue하고 시작 위치를 꺼낸다
        self._enqueue_rib_cells("left", 0, self._mid - 1)
        self._rib_index = 1
        start_pos = self._queue.popleft()
        next_pos = self._queue[0]
        start_dir = (next_pos[0] - start_pos[0], next_pos[1] - start_pos[1])
        return start_pos, start_dir

    def next_position(
        self, snake_body: list, food_pos: tuple
    ) -> tuple[int, int] | None:
        if not self._queue:
            self._enqueue_next(snake_body, food_pos)
        if self._queue:
            return self._queue.popleft()
        return None

    def _rib_bounds(self, side: str, rib_index: int) -> tuple[int, int, int, int]:
        """rib 경계를 (x_min, x_max, y_min, y_max)로 반환합니다."""
        if side == "left":
            top_row = self._height - 1 - rib_index * 2
            return (0, self._mid - 1, top_row - 1, top_row)
        top_row = rib_index * 2
        return (self._mid, self._width - 1, top_row, top_row + 1)

    def _next_rib(self, side: str, rib_index: int) -> tuple[str, int]:
        """다음 rib의 (side, index)를 반환합니다."""
        if side == "left":
            if rib_index + 1 < self._num_ribs:
                return ("left", rib_index + 1)
            return ("right", 0)
        if rib_index + 1 < self._num_ribs:
            return ("right", rib_index + 1)
        return ("left", 0)

    def _pos_depth(self, pos: tuple, side: str, rib_index: int) -> int:
        """pos의 spine으로부터의 깊이를 반환합니다. rib 범위 밖이면 0."""
        x0, x1, y0, y1 = self._rib_bounds(side, rib_index)
        if not (y0 <= pos[1] <= y1 and x0 <= pos[0] <= x1):
            return 0
        if side == "left":
            return (self._mid - 1) - pos[0]
        return pos[0] - self._mid

    def rib_depth(
        self, side: str, rib_index: int, snake_body: list, food_pos: tuple
    ) -> int:
        """이 rib에서 spine으로부터 몇 칸 깊이까지 갈지 결정합니다."""
        max_depth = (self._mid - 1) if side == "left" else (self._width - 1 - self._mid)
        body_d = max(
            (self._pos_depth(seg, side, rib_index) for seg in snake_body), default=-2
        )
        food_d = self._pos_depth(food_pos, side, rib_index)
        depth = max(0, body_d, food_d)
        if depth >= max_depth - 2:
            depth = max_depth
        if depth > 0:  # 현재 가장 빠름
            depth = max_depth
        if self.debug:
            print(
                f"rib_depth({side}, {rib_index}): body_d={body_d}, food_d={food_d}, depth={depth}, max={max_depth}"
            )
        return depth

    def _enqueue_rib_cells(self, side: str, rib_index: int, depth: int):
        """rib 셀들을 depth만큼 queue에 추가합니다."""
        if side == "left":
            top_row = self._height - 1 - rib_index * 2
            bottom_row = top_row - 1
            spine = self._mid - 1
            far = spine - depth
            for x in range(spine, far - 1, -1):
                self._queue.append((x, top_row))
            for x in range(far, spine + 1):
                self._queue.append((x, bottom_row))
        else:
            top_row = rib_index * 2
            bottom_row = top_row + 1
            spine = self._mid
            far = spine + depth
            for x in range(spine, far + 1):
                self._queue.append((x, top_row))
            for x in range(far, spine - 1, -1):
                self._queue.append((x, bottom_row))

    def _enqueue_next(self, snake_body: list, food_pos: tuple):
        """다음 rib을 판단하여 queue에 추가합니다."""
        depth = self.rib_depth(self._phase, self._rib_index, snake_body, food_pos)
        self._enqueue_rib_cells(self._phase, self._rib_index, depth)
        self._phase, self._rib_index = self._next_rib(self._phase, self._rib_index)


ALGORITHMS = [CombAlgorithm(), FishboneAlgorithm()]


def draw_grid(surface, config):
    board_pixel_width = config.board_width * GRID_SIZE
    board_pixel_height = config.board_height * GRID_SIZE
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
    _board_width = DEFAULT_BOARD_WIDTH
    _board_height = DEFAULT_BOARD_HEIGHT

    def __init__(self, manager):
        super().__init__(manager)
        self.selected_mode = CLASSIC
        self.cursor_position = 0  # 0=classic, 1=relaxed, 2=museum, 3=width, 4=height
        self.board_width = ModeSelectionScreen._board_width
        self.board_height = ModeSelectionScreen._board_height

        self.label_title = TextLabel("SNAKE GAME", 72, WINDOW_WIDTH // 2, 120)
        self.label_hint = TextLabel(
            "Arrow keys, ENTER on mode to start", 24, WINDOW_WIDTH // 2, 180, GRAY
        )
        self.label_mode_header = TextLabel("GAME MODE", 48, WINDOW_WIDTH // 2, 260)
        self.label_size_header = TextLabel("BOARD SIZE", 48, WINDOW_WIDTH // 2, 520)
        self.label_classic = TextLabel(
            "  CLASSIC MODE", 38, WINDOW_WIDTH // 2, 320, GRAY
        )
        self.label_relaxed = TextLabel(
            "  RELAXED MODE", 38, WINDOW_WIDTH // 2, 370, GRAY
        )
        self.label_museum = TextLabel("  MUSEUM MODE", 38, WINDOW_WIDTH // 2, 420, GRAY)
        self.label_width = TextLabel(
            "  Width:  20 cells", 32, WINDOW_WIDTH // 2, 580, GRAY
        )
        self.label_height = TextLabel(
            "  Height: 20 cells", 32, WINDOW_WIDTH // 2, 630, GRAY
        )

    def on_enter(self):
        pygame.display.set_caption("Simple Snake Game - Settings")

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_UP:
            self.cursor_position = (self.cursor_position - 1) % 5
            if self.cursor_position == 0:
                self.selected_mode = CLASSIC
            elif self.cursor_position == 1:
                self.selected_mode = RELAXED

        elif event.key == pygame.K_DOWN:
            self.cursor_position = (self.cursor_position + 1) % 5
            if self.cursor_position == 0:
                self.selected_mode = CLASSIC
            elif self.cursor_position == 1:
                self.selected_mode = RELAXED

        elif event.key == pygame.K_LEFT:
            shift_pressed = pygame.key.get_mods() & pygame.KMOD_SHIFT
            step = 10 if shift_pressed else 1
            if self.cursor_position == 3:
                self.board_width = max(MIN_BOARD_SIZE, self.board_width - step)
                ModeSelectionScreen._board_width = self.board_width
            elif self.cursor_position == 4:
                self.board_height = max(MIN_BOARD_SIZE, self.board_height - step)
                ModeSelectionScreen._board_height = self.board_height

        elif event.key == pygame.K_RIGHT:
            shift_pressed = pygame.key.get_mods() & pygame.KMOD_SHIFT
            step = 10 if shift_pressed else 1
            if self.cursor_position == 3:
                self.board_width = min(MAX_BOARD_SIZE, self.board_width + step)
                ModeSelectionScreen._board_width = self.board_width
            elif self.cursor_position == 4:
                self.board_height = min(MAX_BOARD_SIZE, self.board_height + step)
                ModeSelectionScreen._board_height = self.board_height

        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.cursor_position in (0, 1):
                config = GameConfig(
                    mode=self.selected_mode,
                    board_width=self.board_width,
                    board_height=self.board_height,
                )
                self.manager.replace(GameplayScreen(self.manager, config))
            elif self.cursor_position == 2:
                self.manager.push(
                    AlgorithmSelectionScreen(
                        self.manager, self.board_width, self.board_height
                    )
                )

    def draw(self, surface):
        surface.fill(BLACK)

        cursor_classic = "> " if self.cursor_position == 0 else "  "
        classic_color = WHITE if self.cursor_position == 0 else GRAY
        self.label_classic.update(cursor_classic + "CLASSIC MODE", classic_color)

        cursor_relaxed = "> " if self.cursor_position == 1 else "  "
        relaxed_color = WHITE if self.cursor_position == 1 else GRAY
        self.label_relaxed.update(cursor_relaxed + "RELAXED MODE", relaxed_color)

        cursor_museum = "> " if self.cursor_position == 2 else "  "
        museum_color = WHITE if self.cursor_position == 2 else GRAY
        self.label_museum.update(cursor_museum + "MUSEUM MODE", museum_color)

        cursor_width = "> " if self.cursor_position == 3 else "  "
        width_color = WHITE if self.cursor_position == 3 else GRAY
        self.label_width.update(
            cursor_width + f"Width:  {self.board_width} cells", width_color
        )

        cursor_height = "> " if self.cursor_position == 4 else "  "
        height_color = WHITE if self.cursor_position == 4 else GRAY
        self.label_height.update(
            cursor_height + f"Height: {self.board_height} cells", height_color
        )

        self.label_title.draw(surface)
        self.label_hint.draw(surface)
        self.label_mode_header.draw(surface)
        self.label_classic.draw(surface)
        self.label_relaxed.draw(surface)
        self.label_museum.draw(surface)
        self.label_size_header.draw(surface)

        box_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, 560, 300, 90)
        pygame.draw.rect(surface, GRAY, box_rect, 2)

        self.label_width.draw(surface)
        self.label_height.draw(surface)


class AlgorithmSelectionScreen(Screen):
    def __init__(self, manager, board_width, board_height):
        super().__init__(manager)
        self.board_width = board_width
        self.board_height = board_height
        self.cursor_position = 0

        self.label_title = TextLabel("MUSEUM MODE", 72, WINDOW_WIDTH // 2, 120)
        self.label_hint = TextLabel(
            "ENTER to select, ESC to go back", 24, WINDOW_WIDTH // 2, 180, GRAY
        )
        self.label_algo_header = TextLabel("ALGORITHM", 48, WINDOW_WIDTH // 2, 280)
        self.label_constraint = TextLabel("", 24, WINDOW_WIDTH // 2, 420, RED)
        self._algo_labels = []
        for i, algo in enumerate(ALGORITHMS):
            label = TextLabel(
                f"  {algo.name}", 38, WINDOW_WIDTH // 2, 340 + i * 50, GRAY
            )
            self._algo_labels.append(label)

    def on_enter(self):
        pygame.display.set_caption("Simple Snake Game - Museum Mode")

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            self.manager.pop()

        elif event.key == pygame.K_UP:
            self.cursor_position = (self.cursor_position - 1) % len(ALGORITHMS)

        elif event.key == pygame.K_DOWN:
            self.cursor_position = (self.cursor_position + 1) % len(ALGORITHMS)

        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            algo = ALGORITHMS[self.cursor_position]
            if algo.can_run(self.board_width, self.board_height):
                config = GameConfig(
                    mode=MUSEUM,
                    board_width=self.board_width,
                    board_height=self.board_height,
                )
                if algo.dynamic:
                    self.manager.replace_all(
                        GameplayScreen(self.manager, config, algorithm=algo)
                    )
                else:
                    path = algo.generate_path(self.board_width, self.board_height)
                    self.manager.replace_all(
                        GameplayScreen(self.manager, config, algorithm_path=path)
                    )

    def draw(self, surface):
        surface.fill(BLACK)

        self.label_title.draw(surface)
        self.label_hint.draw(surface)
        self.label_algo_header.draw(surface)

        for i, label in enumerate(self._algo_labels):
            algo = ALGORITHMS[i]
            selected = i == self.cursor_position
            can_run = algo.can_run(self.board_width, self.board_height)
            cursor = "> " if selected else "  "
            if can_run:
                color = WHITE if selected else GRAY
            else:
                color = (80, 80, 80)
            label.update(cursor + algo.name, color)
            label.draw(surface)

        algo = ALGORITHMS[self.cursor_position]
        if not algo.can_run(self.board_width, self.board_height):
            self.label_constraint.update(algo.constraint_message())
        else:
            self.label_constraint.update("")
        self.label_constraint.draw(surface)


class GameplayScreen(Screen):
    def __init__(self, manager, config, algorithm_path=None, algorithm=None):
        super().__init__(manager)
        self.config = config
        self.algorithm_path = algorithm_path
        self.algorithm = algorithm
        self.path_index = 0
        self.snake = None
        self.food = None
        self.score = 1
        self.move_count = 0
        self.start_time = 0
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
        if self.config.mode == MUSEUM and self.algorithm:
            start_pos, start_dir = self.algorithm.initialize(
                self.config.board_width, self.config.board_height
            )
            self.snake = Snake(self.config, start_pos, start_dir)
        elif self.config.mode == MUSEUM and self.algorithm_path:
            path = self.algorithm_path
            start_pos = path[0]
            nx, ny = path[1]
            sx, sy = start_pos
            start_dir = (nx - sx, ny - sy)
            self.snake = Snake(self.config, start_pos, start_dir)
            self.path_index = 0
        else:
            self.snake = Snake(self.config)
        self.food = Food(self.config)
        while self.food.position in self.snake.body:
            self.food.randomize_position()
        self.score = 1
        self.move_count = 0
        now = pygame.time.get_ticks()
        self.start_time = now
        self.game_over = False
        self.game_complete = False
        self._should_move = False
        self.last_move_time = now

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
            # MUSEUM: 방향 입력 무시

    def update(self):
        if self.game_over or self.game_complete:
            return

        if self.config.mode == MUSEUM and (self.algorithm or self.algorithm_path):
            area = self.config.board_width * self.config.board_height
            speed_mult = max(self.config.board_width, self.config.board_height) / 6
            interval = 3000 / area / speed_mult
            current_time = pygame.time.get_ticks()
            while current_time - self.last_move_time >= interval:
                self.last_move_time += interval
                if self.algorithm:
                    next_pos = self.algorithm.next_position(
                        self.snake.body, self.food.position
                    )
                    if next_pos is None:
                        break
                    head = self.snake.body[0]
                    self.snake.direction = (
                        next_pos[0] - head[0],
                        next_pos[1] - head[1],
                    )
                else:
                    path = self.algorithm_path
                    n = len(path)
                    next_idx = (self.path_index + 1) % n
                    cx, cy = path[self.path_index]
                    nx, ny = path[next_idx]
                    self.snake.direction = (nx - cx, ny - cy)
                    self.path_index = next_idx
                self._do_move()
                if self.game_over or self.game_complete:
                    break
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
        if self.config.mode in (CLASSIC, MUSEUM):
            w, h = self.config.board_width, self.config.board_height
            wall_hit = (
                next_head[0] < 0
                or next_head[0] >= w
                or next_head[1] < 0
                or next_head[1] >= h
            )
            if wall_hit:
                self.game_over = True
                self.manager.push(OverlayMenuScreen(self.manager, self, "GAME OVER!"))
                return
            will_eat = next_head == self.food.position
            body_after = self.snake.body if will_eat else self.snake.body[:-1]
            if next_head in body_after:
                self.game_over = True
                self.manager.push(OverlayMenuScreen(self.manager, self, "GAME OVER!"))
                return

        if next_head == self.food.position:
            self.snake.grow()

        self.snake.move()
        self.move_count += 1

        if self.snake.body[0] == self.food.position:
            self.score += 1
            if self.algorithm and getattr(self.algorithm, "debug", False):
                print(
                    f"ate food at {self.food.position}, score={self.score}, tail={self.snake.body[-1]}, len={len(self.snake.body)}"
                )
            if (
                len(self.snake.body)
                >= self.config.board_width * self.config.board_height
            ):
                self.game_complete = True
                elapsed = (pygame.time.get_ticks() - self.start_time) / 1000
                area = self.config.board_width * self.config.board_height
                stats = [
                    f"Moves: {self.move_count}",
                    f"Time: {elapsed:.1f}s",
                    f"Efficiency: {(area - 1) / self.move_count * 100:.3g}%",
                ]
                self.manager.push(
                    OverlayMenuScreen(
                        self.manager, self, "CONGRATULATIONS!", "Board Complete!", stats
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

    def __init__(self, manager, gameplay, title, subtitle=None, stats=None):
        super().__init__(manager)
        self.gameplay = gameplay
        self.title = title
        self.subtitle = subtitle
        self.stats = stats or []
        self.menu_position = 0  # 0=restart, 1=main menu

        center_y = WINDOW_HEIGHT // 2
        self.label_title = TextLabel(title, 72, WINDOW_WIDTH // 2, center_y - 80)
        self.label_subtitle = TextLabel(
            subtitle or "", 48, WINDOW_WIDTH // 2, center_y - 20
        )
        self.stat_labels = [TextLabel(s, 28, 0, 0, WHITE) for s in self.stats]
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
            y_base = center_y + 20
        else:
            y_base = center_y + 20

        for i, label in enumerate(self.stat_labels):
            label.x = WINDOW_WIDTH - 100
            label.y = WINDOW_HEIGHT - 30 - (len(self.stat_labels) - 1 - i) * 28
            label.draw(surface)

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
