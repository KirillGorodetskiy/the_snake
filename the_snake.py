import logging
from random import randint

import pygame

# Logging configure
logging.basicConfig(
    filename='login.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# get logger for this module
logger = logging.getLogger(__name__)

# Constants for board and grid:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Directions:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Background color - black:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Cell border color:
BORDER_COLOR = (93, 216, 228)

# Apple color:
APPLE_COLOR = (255, 0, 0)

# Snake color:
SNAKE_COLOR = (0, 255, 0)

# Snake speed:
SPEED = 10

# Window settings:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Window title:
pygame.display.set_caption('Змейка')

# Time settings:
clock = pygame.time.Clock()


class GameObject:
    """This is an abstract class for any game objects."""

    def __init__(self) -> None:
        self.position: tuple = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color: tuple | None = None

    def draw(self) -> None:
        """
        This is an empty method for realisation
        in children objects.
        """
        pass


class Apple(GameObject):
    """
    Represents an apple object in the game grid.

    This class inherits from GameObject and is used to display an apple
    at a specific position on the game screen. It sets the apple's color
    and provides a method to draw it using Pygame.
    """

    def __init__(self) -> None:
        super().__init__()
        self.body_color = APPLE_COLOR

    def draw(self) -> None:
        """
        Draws the apple on the screen at its current position.

        It draws a filled rectangle with the apple color and a border
        around it to visually distinguish it on the grid.
        """
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self, blocked_cells: tuple | None = None) -> None:
        """
        Randomly assigns a new position to the object on the game grid.

        The new position is aligned to the grid size and ensures it does not
        overlap with any of the blocked cells (e.g., snake body).

        Args:
            blocked_cells (set or list of tuple, optional):
                Coordinates that should be avoided when assigning
                a new position. Each coordinate is expected as
                a (x, y) tuple.

        Side Effects:
            Sets self.position to a new (x, y) coordinate.

        Logs:
            Logs the new coordinates with logger.info.
        """
        rand_x = randint(0, GRID_WIDTH - GRID_SIZE) * GRID_SIZE
        rand_y = randint(0, GRID_HEIGHT - GRID_SIZE) * GRID_SIZE
        # Avoiding creation of an apple in another GameObjects like snake
        if blocked_cells is not None and blocked_cells:
            while (rand_x, rand_y) in blocked_cells:
                rand_x = randint(0, GRID_WIDTH - GRID_SIZE) * GRID_SIZE
                rand_y = randint(0, GRID_HEIGHT - GRID_SIZE) * GRID_SIZE
        self.position = (rand_x, rand_y)
        logger.info('Apple change coordintaes to X: %d Y: %d', rand_x, rand_y)


class Snake(GameObject):
    """
    Represents a snake object in the game grid.

    This class inherits from GameObject and is used to display an apple
    at a specific position on the game screen. It sets the apple's color
    and provides a method to draw it using Pygame.
    """

    def __init__(self) -> None:
        super().__init__()
        self.body_color = SNAKE_COLOR
        self.positions = [self.position]
        self.last = self.positions[-1]
        self.direction = RIGHT
        self.next_direction = None

    def draw(self) -> None:
        """
        Draws the snake on the screen, including body, head, and tail cleanup.

        - Draws each segment of the snake's body except the
        head using self.body_color, with a border around each segment.
        - Separately draws the head (first position) for potential
        styling distinction.
        - If `self.last` is set, calls `remove_segments_from_board`
        to erase the last segment, typically used to simulate movement.

        Uses:
            - pygame.draw.rect() for rendering segments.
            - screen (pygame.Surface): the main drawing surface.
            - GRID_SIZE (int): the size of each square segment.
            - BORDER_COLOR: color used for segment borders.
        """
        for position in self.positions[:-1]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            self.remove_segments_from_board([self.last])

    @property
    def length(self) -> int:
        """
        Returns the current length of the object based on its positions.

        Returns:
            int: The number of segments (e.g. body parts of the snake).
        """
        return len(self.positions)

    def remove_segments_from_board(self, segments: tuple) -> None:
        """
        Erases specified segments from the game board by redrawing them
        with the background color.

        Args:
            segments (list of tuple): List of (x, y) positions
            to be cleared from the screen.

        Side Effects:
            Overwrites each segment's rectangle area with
            BOARD_BACKGROUND_COLOR using pygame.draw.rect().
        """
        for segment in segments:
            last_rect = pygame.Rect(segment, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def move(self) -> None:
        """
        Moves the object (e.g. snake) one step in its current direction.

        - Calculates the new head position based on current direction and
         grid size.
        - Applies screen wrapping using modulo with screen width/height.
        - Inserts the new head at the beginning of the positions list.
        - Removes the last segment and stores it in `self.last` for potential
         erasing.

        Side Effects:
            Modifies self.positions (adds new head, removes tail).
            Updates self.last with the removed segment.
        """
        head_x, head_y = self.positions[0]
        dx, dy = self.direction

        new_head = ((head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
                    (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT)

        self.positions.insert(0, new_head)
        self.last = self.positions.pop()

    def update_direction(self) -> None:
        """Applies the next_direction if set, then clears it."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self) -> tuple:
        """Returns the current position of the object's head."""
        return self.positions[0]

    def add_segment(self, index: int, position: tuple) -> None:
        """Inserts a new segment at the given index in the positions list."""
        self.positions.insert(index, position)

    def reset(self) -> None:
        """
        Resets the object to its initial state.

        - Clears the current snake from the board.
        - Re-centers the snake and resets its direction.
        - Initializes positions, last segment, and direction values.
        """
        # clean board from previous snake
        self.remove_segments_from_board(self.positions)

        # renew Snake state
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [self.position]
        self.last = self.positions[-1]
        self.direction = RIGHT
        self.next_direction = None


def handle_keys(game_object):
    """
    Handles keyboard input and updates the game object's next direction.

    - Quits the game if the window is closed.
    - On arrow key press, updates `next_direction` if it's not
    opposite to the current direction.

    Args:
        game_object: The object (e.g., snake) whose direction
        is being controlled.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """
    Initializes and runs the main game loop.

    - Sets up PyGame and creates game objects (snake and apple).
    - Runs the game loop with drawing, movement, input handling,
    and collision checks.
    - Updates the display each frame and handles snake growth
    or reset conditions.
    """
    # Inititalization PyGame:
    pygame.init()
    # Creating gameobjects
    apple = Apple()
    snake = Snake()

    logger.info('The new game has started. Speed %d', SPEED)

    while True:
        clock.tick(SPEED)
        apple.draw()
        snake.update_direction()
        snake.move()
        snake.draw()
        handle_keys(snake)

        # main logic. check if snake ate an apple
        if snake.get_head_position() == apple.position:
            snake.add_segment(0, apple.position)
            logger.info('Snake ate an apple. Snake length %d', snake.length)
            apple.randomize_position(snake.positions)

        # main logic. check if the snake bit itself
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            logger.info('The snake has bit itself. Snake has reseted')

        pygame.display.update()


if __name__ == '__main__':
    main()
