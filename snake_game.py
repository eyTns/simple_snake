"""
Simple Snake Game using Pygame
"""

import pygame
import sys
import random

# Game Constants
WINDOW_WIDTH = 800  # Fixed window width
WINDOW_HEIGHT = 800  # Fixed window height
GRID_SIZE = 20  # Size of each grid cell in pixels
DEFAULT_BOARD_COLS = 20  # Default number of columns (horizontal cells)
DEFAULT_BOARD_ROWS = 20  # Default number of rows (vertical cells)
MIN_BOARD_SIZE = 6  # Minimum board size
MAX_BOARD_SIZE = 32  # Maximum board size

# These will be set dynamically based on user selection
BOARD_COLS = DEFAULT_BOARD_COLS
BOARD_ROWS = DEFAULT_BOARD_ROWS

# Offset to center the board in the window (will be calculated dynamically)
OFFSET_X = 0
OFFSET_Y = 0

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
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


class TextLabel:
    """Reusable text label for UI elements"""

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


# Mode Selection Screen Labels
LABEL_TITLE = TextLabel("SNAKE GAME", 72, WINDOW_WIDTH // 2, 120)
LABEL_MODE_HINT = TextLabel(
    "Arrow keys, ENTER on mode to start", 24, WINDOW_WIDTH // 2, 180, GRAY
)
LABEL_MODE_HEADER = TextLabel("GAME MODE", 48, WINDOW_WIDTH // 2, 260)
LABEL_SIZE_HEADER = TextLabel("BOARD SIZE", 48, WINDOW_WIDTH // 2, 470)
LABEL_CLASSIC = TextLabel("  CLASSIC MODE", 38, WINDOW_WIDTH // 2, 320, GRAY)
LABEL_RELAXED = TextLabel("  RELAXED MODE", 38, WINDOW_WIDTH // 2, 370, GRAY)
LABEL_COLS = TextLabel("  Columns: 20 cells", 32, WINDOW_WIDTH // 2, 530, GRAY)
LABEL_ROWS = TextLabel("  Rows:    20 cells", 32, WINDOW_WIDTH // 2, 580, GRAY)

# Game Screen Labels
LABEL_SCORE = TextLabel("Score: 1", 36, WINDOW_WIDTH // 2, 30)
LABEL_MODE = TextLabel("Mode: CLASSIC", 28, 80, WINDOW_HEIGHT - 20, GRAY)

# Overlay Menu Labels
LABEL_OVERLAY_TITLE = TextLabel("", 72, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80)
LABEL_OVERLAY_SUBTITLE = TextLabel("", 48, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20)
LABEL_OVERLAY_RESTART = TextLabel("  Restart", 36, WINDOW_WIDTH // 2, 0, GRAY)
LABEL_OVERLAY_MENU = TextLabel("  Main Menu", 36, WINDOW_WIDTH // 2, 0, GRAY)
LABEL_OVERLAY_HINT = TextLabel(
    "Press R to restart, ENTER to confirm", 24, WINDOW_WIDTH // 2, 0, GRAY
)


class Snake:
    """Snake class for the game"""

    def __init__(self):
        """Initialize the snake at the center of the grid"""
        self.body = [(BOARD_COLS // 2, BOARD_ROWS // 2)]
        self.direction = RIGHT
        self.last_moved_direction = RIGHT  # Track actual last move for input validation
        self.grow_pending = False

    def move(self):
        """Move the snake in the current direction"""
        head_x, head_y = self.body[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

        # Add new head
        self.body.insert(0, new_head)

        # Remove tail if not growing
        if not self.grow_pending:
            self.body.pop()
        else:
            self.grow_pending = False

        # Update last moved direction for input validation
        self.last_moved_direction = self.direction

    def grow(self):
        """Mark the snake to grow on next move"""
        self.grow_pending = True

    def change_direction(self, new_direction):
        """Change the snake's direction (prevent 180-degree turn)"""
        # Can't turn back on itself - check against last actual move, not queued direction
        opposite_of_last_move = (
            self.last_moved_direction[0] * -1,
            self.last_moved_direction[1] * -1,
        )
        if new_direction != opposite_of_last_move:
            self.direction = new_direction
            return True
        return False

    def check_collision(self):
        """Check if snake collided with wall or itself"""
        head_x, head_y = self.body[0]

        # Wall collision
        if head_x < 0 or head_x >= BOARD_COLS or head_y < 0 or head_y >= BOARD_ROWS:
            return True

        # Self collision
        if self.body[0] in self.body[1:]:
            return True

        return False

    def can_move(self, direction):
        """Check if the snake can move in the given direction (for relaxed mode)"""
        head_x, head_y = self.body[0]
        new_head = (head_x + direction[0], head_y + direction[1])

        # Check wall collision
        if (
            new_head[0] < 0
            or new_head[0] >= BOARD_COLS
            or new_head[1] < 0
            or new_head[1] >= BOARD_ROWS
        ):
            return False

        # Check self collision
        if new_head in self.body:
            return False

        return True

    def draw(self, screen):
        """Draw the snake on the screen"""
        for segment in self.body:
            pygame.draw.rect(screen, GREEN, grid_rect(segment[0], segment[1]))


class Food:
    """Food class for the game"""

    def __init__(self):
        """Initialize food at a random position"""
        self.position = (0, 0)
        self.randomize_position()

    def randomize_position(self):
        """Place food at a random grid position"""
        self.position = (
            random.randint(0, BOARD_COLS - 1),
            random.randint(0, BOARD_ROWS - 1),
        )

    def draw(self, screen):
        """Draw the food on the screen"""
        pygame.draw.rect(screen, RED, grid_rect(self.position[0], self.position[1]))


def grid_rect(x, y):
    """Create a rect for drawing at grid position (x, y)"""
    return pygame.Rect(
        OFFSET_X + x * GRID_SIZE + 1,
        OFFSET_Y + y * GRID_SIZE + 1,
        GRID_SIZE - 1,
        GRID_SIZE - 1,
    )


def reset_game():
    """Create new snake and food, return initial game state"""
    snake = Snake()
    food = Food()
    while food.position in snake.body:
        food.randomize_position()
    return snake, food


def draw_overlay_menu(screen, title, menu_position, subtitle=None):
    """Draw game over or game complete overlay menu"""
    center_y = WINDOW_HEIGHT // 2

    LABEL_OVERLAY_TITLE.update(title)
    LABEL_OVERLAY_TITLE.draw(screen)

    if subtitle:
        LABEL_OVERLAY_SUBTITLE.update(subtitle)
        LABEL_OVERLAY_SUBTITLE.draw(screen)
        y_base = center_y + 40
    else:
        y_base = center_y + 20

    cursor_restart = "> " if menu_position == 0 else "  "
    cursor_menu = "> " if menu_position == 1 else "  "
    restart_color = WHITE if menu_position == 0 else GRAY
    menu_color = WHITE if menu_position == 1 else GRAY

    LABEL_OVERLAY_RESTART.update(cursor_restart + "Restart", restart_color)
    LABEL_OVERLAY_RESTART.y = y_base
    LABEL_OVERLAY_MENU.update(cursor_menu + "Main Menu", menu_color)
    LABEL_OVERLAY_MENU.y = y_base + 40
    LABEL_OVERLAY_HINT.y = y_base + 90

    LABEL_OVERLAY_RESTART.draw(screen)
    LABEL_OVERLAY_MENU.draw(screen)
    LABEL_OVERLAY_HINT.draw(screen)


def handle_menu_input(event, menu_position):
    """Handle menu input. Returns (new_menu_position, action)
    action: None, 'restart', or 'main_menu'
    """
    if event.key in (pygame.K_UP, pygame.K_DOWN):
        return 1 - menu_position, None
    elif event.key == pygame.K_RETURN:
        return menu_position, "restart" if menu_position == 0 else "main_menu"
    elif event.key == pygame.K_r:
        return menu_position, "restart"
    return menu_position, None


def draw_grid(screen):
    """Draw grid lines for better visibility"""
    board_pixel_width = BOARD_COLS * GRID_SIZE
    board_pixel_height = BOARD_ROWS * GRID_SIZE

    for x in range(0, board_pixel_width + 1, GRID_SIZE):
        pygame.draw.line(
            screen,
            GRAY,
            (OFFSET_X + x, OFFSET_Y),
            (OFFSET_X + x, OFFSET_Y + board_pixel_height),
        )
    for y in range(0, board_pixel_height + 1, GRID_SIZE):
        pygame.draw.line(
            screen,
            GRAY,
            (OFFSET_X, OFFSET_Y + y),
            (OFFSET_X + board_pixel_width, OFFSET_Y + y),
        )


def draw_mode_selection(screen, selected_mode, cursor_position, board_cols, board_rows):
    """Draw mode selection screen with cursor"""
    screen.fill(BLACK)

    # Update dynamic labels
    cursor_classic = "> " if cursor_position == 0 else "  "
    classic_color = WHITE if cursor_position == 0 else GRAY
    LABEL_CLASSIC.update(cursor_classic + "CLASSIC MODE", classic_color)

    cursor_relaxed = "> " if cursor_position == 1 else "  "
    relaxed_color = WHITE if cursor_position == 1 else GRAY
    LABEL_RELAXED.update(cursor_relaxed + "RELAXED MODE", relaxed_color)

    cursor_cols = "> " if cursor_position == 2 else "  "
    cols_color = WHITE if cursor_position == 2 else GRAY
    LABEL_COLS.update(cursor_cols + f"Columns: {board_cols} cells", cols_color)

    cursor_rows = "> " if cursor_position == 3 else "  "
    rows_color = WHITE if cursor_position == 3 else GRAY
    LABEL_ROWS.update(cursor_rows + f"Rows:    {board_rows} cells", rows_color)

    # Draw all labels
    LABEL_TITLE.draw(screen)
    LABEL_MODE_HINT.draw(screen)
    LABEL_MODE_HEADER.draw(screen)
    LABEL_CLASSIC.draw(screen)
    LABEL_RELAXED.draw(screen)
    LABEL_SIZE_HEADER.draw(screen)

    # Draw box around board size options
    box_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, 510, 300, 90)
    pygame.draw.rect(screen, GRAY, box_rect, 2)

    LABEL_COLS.draw(screen)
    LABEL_ROWS.draw(screen)

    pygame.display.flip()


def main():
    """Main game function"""
    global BOARD_COLS, BOARD_ROWS, OFFSET_X, OFFSET_Y

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    while True:
        # Mode selection
        pygame.display.set_caption("Simple Snake Game - Settings")
        selected_mode = CLASSIC
        cursor_position = 0  # 0=classic, 1=relaxed, 2=cols, 3=rows
        board_cols = DEFAULT_BOARD_COLS
        board_rows = DEFAULT_BOARD_ROWS
        selecting_mode = True

        while selecting_mode:
            draw_mode_selection(
                screen, selected_mode, cursor_position, board_cols, board_rows
            )

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        cursor_position = (cursor_position - 1) % 4
                        # Update selected mode based on cursor
                        if cursor_position == 0:
                            selected_mode = CLASSIC
                        elif cursor_position == 1:
                            selected_mode = RELAXED

                    elif event.key == pygame.K_DOWN:
                        cursor_position = (cursor_position + 1) % 4
                        # Update selected mode based on cursor
                        if cursor_position == 0:
                            selected_mode = CLASSIC
                        elif cursor_position == 1:
                            selected_mode = RELAXED

                    elif event.key == pygame.K_LEFT:
                        shift_pressed = pygame.key.get_mods() & pygame.KMOD_SHIFT
                        step = 10 if shift_pressed else 1
                        if cursor_position == 2:  # Board columns
                            board_cols = max(MIN_BOARD_SIZE, board_cols - step)
                        elif cursor_position == 3:  # Board rows
                            board_rows = max(MIN_BOARD_SIZE, board_rows - step)

                    elif event.key == pygame.K_RIGHT:
                        shift_pressed = pygame.key.get_mods() & pygame.KMOD_SHIFT
                        step = 10 if shift_pressed else 1
                        if cursor_position == 2:  # Board columns
                            board_cols = min(MAX_BOARD_SIZE, board_cols + step)
                        elif cursor_position == 3:  # Board rows
                            board_rows = min(MAX_BOARD_SIZE, board_rows + step)

                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        # Only start game if on mode selection (position 0 or 1)
                        if cursor_position == 0 or cursor_position == 1:
                            selecting_mode = False

            clock.tick(60)

        # Update global grid settings
        BOARD_COLS = board_cols
        BOARD_ROWS = board_rows

        # Calculate offset to center the board
        board_pixel_width = BOARD_COLS * GRID_SIZE
        board_pixel_height = BOARD_ROWS * GRID_SIZE
        OFFSET_X = (WINDOW_WIDTH - board_pixel_width) // 2
        OFFSET_Y = (WINDOW_HEIGHT - board_pixel_height) // 2

        # Window is already correct size (800x800)
        pygame.display.set_caption("Simple Snake Game")

        mode = selected_mode

        # Create game objects
        snake, food = reset_game()
        score = 1

        # Game state
        game_over = False
        game_complete = False
        menu_position = 0  # 0=restart, 1=main menu
        running = True
        last_move_time = pygame.time.get_ticks()

        # Unified game loop
        while running:
            should_move = False
            direction_input = None

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    # Handle menu input when game over or complete
                    if game_over or game_complete:
                        menu_position, action = handle_menu_input(event, menu_position)
                        if action == "restart":
                            snake, food = reset_game()
                            score = 1
                            game_over = False
                            game_complete = False
                            menu_position = 0
                            last_move_time = pygame.time.get_ticks()
                        elif action == "main_menu":
                            running = False
                    else:
                        # Handle game input
                        if event.key == pygame.K_UP:
                            direction_input = UP
                        elif event.key == pygame.K_DOWN:
                            direction_input = DOWN
                        elif event.key == pygame.K_LEFT:
                            direction_input = LEFT
                        elif event.key == pygame.K_RIGHT:
                            direction_input = RIGHT
                        elif event.key == pygame.K_q:
                            game_over = True
                            menu_position = 0

                        # Mode-specific direction handling
                        if direction_input and not game_over:
                            if mode == CLASSIC:
                                snake.change_direction(direction_input)
                            elif mode == RELAXED:
                                if snake.change_direction(direction_input):
                                    if snake.can_move(direction_input):
                                        should_move = True

            # Movement logic
            if not game_over and not game_complete:
                if mode == CLASSIC:
                    current_time = pygame.time.get_ticks()
                    if current_time - last_move_time >= SNAKE_MOVE_INTERVAL:
                        should_move = True
                        last_move_time = current_time

                if should_move:
                    # Check if next position has food
                    next_head = (
                        snake.body[0][0] + snake.direction[0],
                        snake.body[0][1] + snake.direction[1],
                    )
                    if next_head == food.position:
                        snake.grow()

                    snake.move()

                    # Check if food was eaten
                    if snake.body[0] == food.position:
                        score += 1
                        if len(snake.body) >= BOARD_COLS * BOARD_ROWS:
                            game_complete = True
                            menu_position = 0
                        else:
                            food.randomize_position()
                            while food.position in snake.body:
                                food.randomize_position()

                    # Check collisions (Classic mode only)
                    if mode == CLASSIC and snake.check_collision():
                        game_over = True
                        menu_position = 0

            # Draw
            screen.fill(BLACK)
            draw_grid(screen)
            snake.draw(screen)
            if not game_complete:
                food.draw(screen)

            LABEL_SCORE.update(f"Score: {score}")
            LABEL_MODE.update(f"Mode: {mode.upper()}")
            LABEL_SCORE.draw(screen)
            LABEL_MODE.draw(screen)

            if game_over:
                draw_overlay_menu(screen, "GAME OVER!", menu_position)
            elif game_complete:
                draw_overlay_menu(
                    screen, "CONGRATULATIONS!", menu_position, "Board Complete!"
                )

            pygame.display.flip()
            clock.tick(FPS)


if __name__ == "__main__":
    main()
