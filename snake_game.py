"""
Simple Snake Game using Pygame
"""
import pygame
import sys
import random

# Game Constants
GRID_SIZE = 20  # Size of each grid cell in pixels
DEFAULT_BOARD_COLS = 20  # Default number of columns (horizontal cells)
DEFAULT_BOARD_ROWS = 20  # Default number of rows (vertical cells)

# These will be set dynamically based on user selection
BOARD_COLS = DEFAULT_BOARD_COLS
BOARD_ROWS = DEFAULT_BOARD_ROWS
WINDOW_WIDTH = BOARD_COLS * GRID_SIZE
WINDOW_HEIGHT = BOARD_ROWS * GRID_SIZE

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (40, 40, 40)

# Game Settings
FPS = 10

# Game Modes
CLASSIC = "classic"
RELAXED = "relaxed"

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class Snake:
    """Snake class for the game"""

    def __init__(self):
        """Initialize the snake at the center of the grid"""
        self.body = [(BOARD_COLS // 2, BOARD_ROWS // 2)]
        self.direction = RIGHT
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

    def grow(self):
        """Mark the snake to grow on next move"""
        self.grow_pending = True

    def change_direction(self, new_direction):
        """Change the snake's direction (prevent 180-degree turn)"""
        # Can't turn back on itself
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
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
        if new_head[0] < 0 or new_head[0] >= BOARD_COLS or new_head[1] < 0 or new_head[1] >= BOARD_ROWS:
            return False

        # Check self collision
        if new_head in self.body:
            return False

        return True

    def draw(self, screen):
        """Draw the snake on the screen"""
        for segment in self.body:
            rect = pygame.Rect(
                segment[0] * GRID_SIZE,
                segment[1] * GRID_SIZE,
                GRID_SIZE - 2,
                GRID_SIZE - 2
            )
            pygame.draw.rect(screen, GREEN, rect)


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
            random.randint(0, BOARD_ROWS - 1)
        )

    def draw(self, screen):
        """Draw the food on the screen"""
        rect = pygame.Rect(
            self.position[0] * GRID_SIZE,
            self.position[1] * GRID_SIZE,
            GRID_SIZE - 2,
            GRID_SIZE - 2
        )
        pygame.draw.rect(screen, RED, rect)


def draw_grid(screen):
    """Draw grid lines for better visibility"""
    for x in range(0, WINDOW_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WINDOW_WIDTH, y))


def draw_text(screen, text, size, x, y, color=WHITE):
    """Draw text on the screen"""
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)


def draw_mode_selection(screen, selected_mode, cursor_position, board_cols, board_rows):
    """Draw mode selection screen with cursor"""
    screen.fill(BLACK)
    draw_text(screen, "GAME SETTINGS", 72, 300, 80)
    draw_text(screen, "Arrow keys, ENTER on mode to start", 24, 300, 130, GRAY)

    # Classic mode
    classic_color = WHITE if selected_mode == CLASSIC else GRAY
    cursor_classic = "> " if cursor_position == 0 else "  "
    draw_text(screen, cursor_classic + "CLASSIC MODE", 42, 300, 200, classic_color)

    # Relaxed mode
    relaxed_color = WHITE if selected_mode == RELAXED else GRAY
    cursor_relaxed = "> " if cursor_position == 1 else "  "
    draw_text(screen, cursor_relaxed + "RELAXED MODE", 42, 300, 260, relaxed_color)

    # Grid settings box
    pygame.draw.rect(screen, GRAY, (150, 320, 300, 120), 2)
    draw_text(screen, "BOARD SIZE", 36, 300, 350, WHITE)

    # Board columns (horizontal cells)
    cursor_cols = "> " if cursor_position == 2 else "  "
    cols_color = WHITE if cursor_position == 2 else GRAY
    draw_text(screen, cursor_cols + f"Columns: {board_cols} cells", 32, 300, 390, cols_color)

    # Board rows (vertical cells)
    cursor_rows = "> " if cursor_position == 3 else "  "
    rows_color = WHITE if cursor_position == 3 else GRAY
    draw_text(screen, cursor_rows + f"Rows:    {board_rows} cells", 32, 300, 420, rows_color)

    pygame.display.flip()


def main():
    """Main game function"""
    global BOARD_COLS, BOARD_ROWS, WINDOW_WIDTH, WINDOW_HEIGHT

    # Initialize Pygame
    pygame.init()

    # Create initial window for settings
    screen = pygame.display.set_mode((600, 500))
    pygame.display.set_caption("Simple Snake Game - Settings")

    # Create clock for controlling frame rate
    clock = pygame.time.Clock()

    # Mode selection
    selected_mode = CLASSIC
    cursor_position = 0  # 0=classic, 1=relaxed, 2=cols, 3=rows
    board_cols = DEFAULT_BOARD_COLS
    board_rows = DEFAULT_BOARD_ROWS
    selecting_mode = True

    while selecting_mode:
        draw_mode_selection(screen, selected_mode, cursor_position, board_cols, board_rows)

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
                    if cursor_position == 2:  # Board columns
                        board_cols = max(10, board_cols - 1)
                    elif cursor_position == 3:  # Board rows
                        board_rows = max(10, board_rows - 1)

                elif event.key == pygame.K_RIGHT:
                    if cursor_position == 2:  # Board columns
                        board_cols = min(50, board_cols + 1)
                    elif cursor_position == 3:  # Board rows
                        board_rows = min(50, board_rows + 1)

                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    # Only start game if on mode selection (position 0 or 1)
                    if cursor_position == 0 or cursor_position == 1:
                        selecting_mode = False
                    # If on grid size (position 2 or 3), update window size
                    elif cursor_position == 2 or cursor_position == 3:
                        # Update window size immediately
                        temp_width = board_cols * GRID_SIZE
                        temp_height = board_rows * GRID_SIZE
                        screen = pygame.display.set_mode((max(600, temp_width), max(500, temp_height)))
                        pygame.display.set_caption("Simple Snake Game - Settings")

        clock.tick(60)

    # Update global grid settings
    BOARD_COLS = board_cols
    BOARD_ROWS = board_rows
    WINDOW_WIDTH = BOARD_COLS * GRID_SIZE
    WINDOW_HEIGHT = BOARD_ROWS * GRID_SIZE

    # Recreate window with correct size
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Simple Snake Game")

    mode = selected_mode

    # Create game objects
    snake = Snake()
    food = Food()
    score = 0

    # Game state
    game_over = False
    running = True

    # Game loop
    if mode == CLASSIC:
        # Classic mode: automatic movement
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Handle keyboard input (Classic mode - direction change only)
                if event.type == pygame.KEYDOWN and not game_over:
                    if event.key == pygame.K_UP:
                        snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction(RIGHT)

                # Restart game on SPACE when game over
                if event.type == pygame.KEYDOWN and game_over:
                    if event.key == pygame.K_SPACE:
                        snake = Snake()
                        food = Food()
                        score = 0
                        game_over = False

            if not game_over:
                # Move snake automatically (Classic mode)
                snake.move()

                # Check collision with food
                if snake.body[0] == food.position:
                    snake.grow()
                    food.randomize_position()
                    # Make sure food doesn't spawn on snake
                    while food.position in snake.body:
                        food.randomize_position()
                    score += 10

                # Check collisions
                if snake.check_collision():
                    game_over = True

            # Clear screen
            screen.fill(BLACK)

            # Draw grid
            draw_grid(screen)

            # Draw game objects
            snake.draw(screen)
            food.draw(screen)

            # Draw score and mode
            draw_text(screen, f"Score: {score}", 36, WINDOW_WIDTH // 2, 30)
            draw_text(screen, f"Mode: {mode.upper()}", 28, 80, WINDOW_HEIGHT - 20, GRAY)

            # Draw game over message
            if game_over:
                draw_text(screen, "GAME OVER!", 72, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40)
                draw_text(screen, "Press SPACE to restart", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20)

            # Update display
            pygame.display.flip()

            # Control frame rate
            clock.tick(FPS)

    elif mode == RELAXED:
        # Relaxed mode: move only on key press
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Handle keyboard input (Relaxed mode - move on key press)
                if event.type == pygame.KEYDOWN and not game_over:
                    new_direction = None
                    if event.key == pygame.K_UP:
                        new_direction = UP
                    elif event.key == pygame.K_DOWN:
                        new_direction = DOWN
                    elif event.key == pygame.K_LEFT:
                        new_direction = LEFT
                    elif event.key == pygame.K_RIGHT:
                        new_direction = RIGHT
                    elif event.key == pygame.K_q:
                        # Q key triggers game over
                        game_over = True

                    # Move snake only if direction is valid and movement is possible
                    if new_direction and not game_over:
                        # Check if direction change is valid (not 180 degrees)
                        if snake.change_direction(new_direction):
                            # Check if snake can move in this direction (not into wall or itself)
                            if snake.can_move(new_direction):
                                snake.move()

                                # Check collision with food
                                if snake.body[0] == food.position:
                                    snake.grow()
                                    food.randomize_position()
                                    # Make sure food doesn't spawn on snake
                                    while food.position in snake.body:
                                        food.randomize_position()
                                    score += 10
                            # If can't move, just ignore the input (don't move, don't game over)

                # Restart game on SPACE when game over
                if event.type == pygame.KEYDOWN and game_over:
                    if event.key == pygame.K_SPACE:
                        snake = Snake()
                        food = Food()
                        score = 0
                        game_over = False

            # Clear screen
            screen.fill(BLACK)

            # Draw grid
            draw_grid(screen)

            # Draw game objects
            snake.draw(screen)
            food.draw(screen)

            # Draw score and mode
            draw_text(screen, f"Score: {score}", 36, WINDOW_WIDTH // 2, 30)
            draw_text(screen, f"Mode: {mode.upper()}", 28, 80, WINDOW_HEIGHT - 20, GRAY)

            # Draw game over message
            if game_over:
                draw_text(screen, "GAME OVER!", 72, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40)
                draw_text(screen, "Press SPACE to restart", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20)

            # Update display
            pygame.display.flip()

            # Control frame rate (higher for responsiveness)
            clock.tick(60)

    # Quit game
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
