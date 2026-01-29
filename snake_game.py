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
        opposite_of_last_move = (self.last_moved_direction[0] * -1, self.last_moved_direction[1] * -1)
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
            rect = pygame.Rect(
                OFFSET_X + segment[0] * GRID_SIZE + 1,
                OFFSET_Y + segment[1] * GRID_SIZE + 1,
                GRID_SIZE - 1,
                GRID_SIZE - 1,
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
            random.randint(0, BOARD_ROWS - 1),
        )

    def draw(self, screen):
        """Draw the food on the screen"""
        rect = pygame.Rect(
            OFFSET_X + self.position[0] * GRID_SIZE + 1,
            OFFSET_Y + self.position[1] * GRID_SIZE + 1,
            GRID_SIZE - 1,
            GRID_SIZE - 1,
        )
        pygame.draw.rect(screen, RED, rect)


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

    # Center x position
    center_x = WINDOW_WIDTH // 2

    # Title
    draw_text(screen, "SNAKE GAME", 72, center_x, 120)
    draw_text(screen, "Arrow keys, ENTER on mode to start", 24, center_x, 180, GRAY)

    # Mode selection section
    draw_text(screen, "GAME MODE", 48, center_x, 260, WHITE)

    # Classic mode (highlight only when cursor is on it)
    cursor_classic = "> " if cursor_position == 0 else "  "
    classic_color = WHITE if cursor_position == 0 else GRAY
    draw_text(screen, cursor_classic + "CLASSIC MODE", 38, center_x, 320, classic_color)

    # Relaxed mode (highlight only when cursor is on it)
    cursor_relaxed = "> " if cursor_position == 1 else "  "
    relaxed_color = WHITE if cursor_position == 1 else GRAY
    draw_text(screen, cursor_relaxed + "RELAXED MODE", 38, center_x, 370, relaxed_color)

    # Board size section
    draw_text(screen, "BOARD SIZE", 48, center_x, 470, WHITE)

    # Draw box around board size options
    box_rect = pygame.Rect(center_x - 150, 510, 300, 90)
    pygame.draw.rect(screen, GRAY, box_rect, 2)

    # Board columns (horizontal cells)
    cursor_cols = "> " if cursor_position == 2 else "  "
    cols_color = WHITE if cursor_position == 2 else GRAY
    draw_text(
        screen,
        cursor_cols + f"Columns: {board_cols} cells",
        32,
        center_x,
        530,
        cols_color,
    )

    # Board rows (vertical cells)
    cursor_rows = "> " if cursor_position == 3 else "  "
    rows_color = WHITE if cursor_position == 3 else GRAY
    draw_text(
        screen,
        cursor_rows + f"Rows:    {board_rows} cells",
        32,
        center_x,
        580,
        rows_color,
    )

    pygame.display.flip()


def main():
    """Main game function"""
    global BOARD_COLS, BOARD_ROWS, OFFSET_X, OFFSET_Y

    # Initialize Pygame
    pygame.init()

    # Create initial window for settings
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
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
    snake = Snake()
    food = Food()
    # Make sure food doesn't spawn on snake's initial position
    while food.position in snake.body:
        food.randomize_position()
    score = 1

    # Game state
    game_over = False
    game_over_menu_position = 0  # 0=restart, 1=main menu
    game_complete = False
    complete_menu_position = 0  # 0=restart, 1=main menu
    running = True

    # Game loop
    if mode == CLASSIC:
        # Classic mode: automatic movement with timed intervals
        last_move_time = pygame.time.get_ticks()
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Handle keyboard input (Classic mode - direction change only)
                if event.type == pygame.KEYDOWN and not game_over and not game_complete:
                    if event.key == pygame.K_UP:
                        snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction(RIGHT)
                    elif event.key == pygame.K_q:
                        # Q key triggers game over
                        game_over = True
                        game_over_menu_position = 0

                # Handle game over menu
                if event.type == pygame.KEYDOWN and game_over:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        game_over_menu_position = 1 - game_over_menu_position
                    elif event.key == pygame.K_RETURN:
                        if game_over_menu_position == 0:  # Restart
                            snake = Snake()
                            food = Food()
                            while food.position in snake.body:
                                food.randomize_position()
                            score = 1
                            game_over = False
                            game_over_menu_position = 0
                            last_move_time = pygame.time.get_ticks()
                        else:  # Main menu
                            return
                    elif event.key == pygame.K_r:
                        # R key restarts regardless of cursor position
                        snake = Snake()
                        food = Food()
                        while food.position in snake.body:
                            food.randomize_position()
                        score = 1
                        game_over = False
                        game_over_menu_position = 0
                        last_move_time = pygame.time.get_ticks()

                # Handle game complete menu
                if event.type == pygame.KEYDOWN and game_complete:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        complete_menu_position = 1 - complete_menu_position
                    elif event.key == pygame.K_RETURN:
                        if complete_menu_position == 0:  # Restart
                            snake = Snake()
                            food = Food()
                            while food.position in snake.body:
                                food.randomize_position()
                            score = 1
                            game_complete = False
                            complete_menu_position = 0
                            last_move_time = pygame.time.get_ticks()
                        else:  # Main menu
                            return  # Return to main menu (restart main function)
                    elif event.key == pygame.K_r:
                        # R key restarts regardless of cursor position
                        snake = Snake()
                        food = Food()
                        while food.position in snake.body:
                            food.randomize_position()
                        score = 1
                        game_complete = False
                        complete_menu_position = 0
                        last_move_time = pygame.time.get_ticks()

            if not game_over:
                # Move snake automatically at timed intervals (Classic mode)
                current_time = pygame.time.get_ticks()
                if current_time - last_move_time >= SNAKE_MOVE_INTERVAL:
                    # Check if next position has food (grow before moving)
                    next_head = (snake.body[0][0] + snake.direction[0],
                                snake.body[0][1] + snake.direction[1])
                    if next_head == food.position:
                        snake.grow()

                    snake.move()
                    last_move_time = current_time

                    # If food was eaten, check if board is full or spawn new food
                    if snake.body[0] == food.position:
                        score += 1
                        # Check if board is completely filled
                        if len(snake.body) >= BOARD_COLS * BOARD_ROWS:
                            game_complete = True
                            complete_menu_position = 0
                        else:
                            food.randomize_position()
                            # Make sure food doesn't spawn on snake
                            while food.position in snake.body:
                                food.randomize_position()

                    # Check collisions
                    if snake.check_collision():
                        game_over = True
                        game_over_menu_position = 0

            # Clear screen
            screen.fill(BLACK)

            # Draw grid
            draw_grid(screen)

            # Draw game objects
            snake.draw(screen)
            if not game_complete:
                food.draw(screen)

            # Draw score and mode
            draw_text(screen, f"Score: {score}", 36, WINDOW_WIDTH // 2, 30)
            draw_text(screen, f"Mode: {mode.upper()}", 28, 80, WINDOW_HEIGHT - 20, GRAY)

            # Draw game over message
            if game_over:
                draw_text(
                    screen, "GAME OVER!", 72, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80
                )

                # Menu options
                restart_color = WHITE if game_over_menu_position == 0 else GRAY
                menu_color = WHITE if game_over_menu_position == 1 else GRAY
                cursor_restart = "> " if game_over_menu_position == 0 else "  "
                cursor_menu = "> " if game_over_menu_position == 1 else "  "

                draw_text(
                    screen, cursor_restart + "Restart", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20, restart_color
                )
                draw_text(
                    screen, cursor_menu + "Main Menu", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60, menu_color
                )
                draw_text(
                    screen, "Press R to restart, ENTER to confirm", 24, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 110, GRAY
                )

            # Draw game complete message
            if game_complete:
                draw_text(
                    screen, "CONGRATULATIONS!", 72, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80
                )
                draw_text(
                    screen, "Board Complete!", 48, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20
                )

                # Menu options
                restart_color = WHITE if complete_menu_position == 0 else GRAY
                menu_color = WHITE if complete_menu_position == 1 else GRAY
                cursor_restart = "> " if complete_menu_position == 0 else "  "
                cursor_menu = "> " if complete_menu_position == 1 else "  "

                draw_text(
                    screen, cursor_restart + "Restart", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40, restart_color
                )
                draw_text(
                    screen, cursor_menu + "Main Menu", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80, menu_color
                )
                draw_text(
                    screen, "Press R to restart, ENTER to confirm", 24, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 130, GRAY
                )

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
                if event.type == pygame.KEYDOWN and not game_over and not game_complete:
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
                        game_over_menu_position = 0

                    # Move snake only if direction is valid and movement is possible
                    if new_direction and not game_over:
                        # Check if direction change is valid (not 180 degrees)
                        if snake.change_direction(new_direction):
                            # Check if snake can move in this direction (not into wall or itself)
                            if snake.can_move(new_direction):
                                # Check if next position has food (grow before moving)
                                next_head = (snake.body[0][0] + new_direction[0],
                                            snake.body[0][1] + new_direction[1])
                                if next_head == food.position:
                                    snake.grow()

                                snake.move()

                                # If food was eaten, check if board is full or spawn new food
                                if snake.body[0] == food.position:
                                    score += 1
                                    # Check if board is completely filled
                                    if len(snake.body) >= BOARD_COLS * BOARD_ROWS:
                                        game_complete = True
                                        complete_menu_position = 0
                                    else:
                                        food.randomize_position()
                                        # Make sure food doesn't spawn on snake
                                        while food.position in snake.body:
                                            food.randomize_position()
                            # If can't move, just ignore the input (don't move, don't game over)

                # Handle game over menu
                if event.type == pygame.KEYDOWN and game_over:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        game_over_menu_position = 1 - game_over_menu_position
                    elif event.key == pygame.K_RETURN:
                        if game_over_menu_position == 0:  # Restart
                            snake = Snake()
                            food = Food()
                            while food.position in snake.body:
                                food.randomize_position()
                            score = 1
                            game_over = False
                            game_over_menu_position = 0
                        else:  # Main menu
                            return
                    elif event.key == pygame.K_r:
                        # R key restarts regardless of cursor position
                        snake = Snake()
                        food = Food()
                        while food.position in snake.body:
                            food.randomize_position()
                        score = 1
                        game_over = False
                        game_over_menu_position = 0

                # Handle game complete menu
                if event.type == pygame.KEYDOWN and game_complete:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        complete_menu_position = 1 - complete_menu_position
                    elif event.key == pygame.K_RETURN:
                        if complete_menu_position == 0:  # Restart
                            snake = Snake()
                            food = Food()
                            while food.position in snake.body:
                                food.randomize_position()
                            score = 1
                            game_complete = False
                            complete_menu_position = 0
                        else:  # Main menu
                            return  # Return to main menu (restart main function)
                    elif event.key == pygame.K_r:
                        # R key restarts regardless of cursor position
                        snake = Snake()
                        food = Food()
                        while food.position in snake.body:
                            food.randomize_position()
                        score = 1
                        game_complete = False
                        complete_menu_position = 0

            # Clear screen
            screen.fill(BLACK)

            # Draw grid
            draw_grid(screen)

            # Draw game objects
            snake.draw(screen)
            if not game_complete:
                food.draw(screen)

            # Draw score and mode
            draw_text(screen, f"Score: {score}", 36, WINDOW_WIDTH // 2, 30)
            draw_text(screen, f"Mode: {mode.upper()}", 28, 80, WINDOW_HEIGHT - 20, GRAY)

            # Draw game over message
            if game_over:
                draw_text(
                    screen, "GAME OVER!", 72, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80
                )

                # Menu options
                restart_color = WHITE if game_over_menu_position == 0 else GRAY
                menu_color = WHITE if game_over_menu_position == 1 else GRAY
                cursor_restart = "> " if game_over_menu_position == 0 else "  "
                cursor_menu = "> " if game_over_menu_position == 1 else "  "

                draw_text(
                    screen, cursor_restart + "Restart", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20, restart_color
                )
                draw_text(
                    screen, cursor_menu + "Main Menu", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60, menu_color
                )
                draw_text(
                    screen, "Press R to restart, ENTER to confirm", 24, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 110, GRAY
                )

            # Draw game complete message
            if game_complete:
                draw_text(
                    screen, "CONGRATULATIONS!", 72, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80
                )
                draw_text(
                    screen, "Board Complete!", 48, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20
                )

                # Menu options
                restart_color = WHITE if complete_menu_position == 0 else GRAY
                menu_color = WHITE if complete_menu_position == 1 else GRAY
                cursor_restart = "> " if complete_menu_position == 0 else "  "
                cursor_menu = "> " if complete_menu_position == 1 else "  "

                draw_text(
                    screen, cursor_restart + "Restart", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40, restart_color
                )
                draw_text(
                    screen, cursor_menu + "Main Menu", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80, menu_color
                )
                draw_text(
                    screen, "Press R to restart, ENTER to confirm", 24, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 130, GRAY
                )

            # Update display
            pygame.display.flip()

            # Control frame rate (higher for responsiveness)
            clock.tick(60)

    # Quit game
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    while True:
        main()
