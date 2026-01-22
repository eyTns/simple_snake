"""
Simple Snake Game using Pygame
"""
import pygame
import sys
import random

# Game Constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (40, 40, 40)

# Game Settings
FPS = 10

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class Snake:
    """Snake class for the game"""

    def __init__(self):
        """Initialize the snake at the center of the grid"""
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
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

    def check_collision(self):
        """Check if snake collided with wall or itself"""
        head_x, head_y = self.body[0]

        # Wall collision
        if head_x < 0 or head_x >= GRID_WIDTH or head_y < 0 or head_y >= GRID_HEIGHT:
            return True

        # Self collision
        if self.body[0] in self.body[1:]:
            return True

        return False

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
            random.randint(0, GRID_WIDTH - 1),
            random.randint(0, GRID_HEIGHT - 1)
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


def main():
    """Main game function"""
    # Initialize Pygame
    pygame.init()

    # Create game window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Simple Snake Game")

    # Create clock for controlling frame rate
    clock = pygame.time.Clock()

    # Create game objects
    snake = Snake()
    food = Food()
    score = 0

    # Game state
    game_over = False
    running = True

    # Game loop
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle keyboard input
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
            # Move snake
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

        # Draw score
        draw_text(screen, f"Score: {score}", 36, WINDOW_WIDTH // 2, 30)

        # Draw game over message
        if game_over:
            draw_text(screen, "GAME OVER!", 72, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40)
            draw_text(screen, "Press SPACE to restart", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20)

        # Update display
        pygame.display.flip()

        # Control frame rate
        clock.tick(FPS)

    # Quit game
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
