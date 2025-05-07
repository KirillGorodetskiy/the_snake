import logging
from random import choice, randint

import pygame as pg

# Constants for board and grid:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

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
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Window title:
pg.display.set_caption("Змейка")

# Time settings:
clock = pg.time.Clock()


class GameObject:
    """This is an abstract class for any game objects."""

    def __init__(self,
                 position: tuple = SCREEN_CENTER,
                 body_color: tuple | None = None
                 ) -> None:

        self.position: tuple = position
        self.body_color: tuple | None = body_color

    def draw(self) -> None:
        """
        This is an empty method for realisation
        in children objects.
        """

    def draw_rect(self,
                  position: tuple,
                  body_color: tuple | None = None
                  ) -> None:
        """
        Draws a rectangle on the screen at the specified position.

        If no body color is provided,
        the object's default `self.body_color` is used.

        Args:
            position (tuple): The (x, y) position of
            the rectangle's top-left corner.

            body_color (tuple | None): Optional RGB color tuple.
            If None, defaults to `self.body_color`.

        Returns:
            None
        """
        if body_color is None:
            body_color = self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def _get_random_position(self) -> tuple:
        """Returns a random grid-aligned (x, y) position."""
        rand_x = randint(0, GRID_WIDTH - GRID_SIZE) * GRID_SIZE
        rand_y = randint(0, GRID_HEIGHT - GRID_SIZE) * GRID_SIZE
        return (rand_x, rand_y)

    def remove_segments_from_board(self, segments: tuple) -> None:
        """
        Erases specified segments from the game board by redrawing them
        with the background color.

        Args:
            segments (list of tuple): List of (x, y) positions
            to be cleared from the screen.

        Side Effects:
            Overwrites each segment's rectangle area with
            BOARD_BACKGROUND_COLOR using pg.draw.rect().
        """
        for segment in segments:
            last_rect = pg.Rect(segment, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


class Apple(GameObject):
    """
    Represents an apple object in the game grid.

    This class inherits from GameObject and is used to display an apple
    at a specific position on the game screen. It sets the apple's color
    and provides a method to draw it using pg.
    """

    def __init__(self,
                 blocked_segments: list | None = None,
                 position: tuple | None = None,
                 body_color: tuple | None = APPLE_COLOR
                 ) -> None:
        super().__init__(position, body_color)
        if blocked_segments is None:
            blocked_segments = []
        # randomize_position checks collisions
        self.randomize_position(blocked_segments)

    def draw(self) -> None:
        """
        Draws the apple on the screen at its current position.

        It draws a filled rectangle with the apple color and a border
        around it to visually distinguish it on the grid.
        """
        self.draw_rect(self.position, APPLE_COLOR)

    def randomize_position(self, blocked_cells: list | None = None) -> None:
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
            Logs the new coordinates with logging.info.
        """
        if blocked_cells is None:
            blocked_cells = []
        while True:
            rand_pos = self._get_random_position()
            # Avoiding creation of an apple in another GameObjects like snake
            if rand_pos not in blocked_cells:
                self.position = rand_pos
                break
            logging.info(
                "Apple change coordintaes to X: %d Y: %d",
                rand_pos[0], rand_pos[1]
            )


class Snake(GameObject):
    """
    Represents a snake object in the game grid.

    This class inherits from GameObject and is used to display an apple
    at a specific position on the game screen. It sets the apple's color
    and provides a method to draw it using pg.
    """

    def __init__(self,
                 position: tuple = SCREEN_CENTER,
                 body_color: tuple | None = SNAKE_COLOR
                 ) -> None:
        super().__init__(position, body_color)
        self.positions: list = [self.position]
        self.last: tuple | None = self.positions[-1]
        self.direction: tuple = RIGHT
        self.next_direction: tuple | None = None

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
            - pg.draw.rect() for rendering segments.
            - screen (pg.Surface): the main drawing surface.
            - GRID_SIZE (int): the size of each square segment.
            - BORDER_COLOR: color used for segment borders.
        """
        # Draw snake head
        self.draw_rect(self.positions[0])

        # Blank last segment
        if self.last:
            self.remove_segments_from_board([self.last])

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
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )

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
        self.positions.append(self.last)
        self.last = None

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
        self.positions = [self.position]
        self.last = self.positions[-1]
        self.direction = choice([UP, LEFT, RIGHT, DOWN])
        self.next_direction = None


def handle_keys(game_object):
    """
    Handles keyboard input and updates the game object's next direction.

    - Quits the game if the window is closed or Escaped pressed.
    - On arrow key press, updates `next_direction` if it's not
    opposite to the current direction.

    Args:
        game_object: The object (e.g., snake) whose direction
        is being controlled.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT
            elif event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit


def main():
    """
    Initializes and runs the main game loop.

    - Sets up pg and creates game objects (snake and apple).
    - Runs the game loop with drawing, movement, input handling,
    and collision checks.
    - Updates the display each frame and handles snake growth
    or reset conditions.
    """
    # Inititalization pg:
    pg.init()
    # Creating gameobjects
    snake = Snake(SCREEN_CENTER, SNAKE_COLOR)
    apple = Apple(snake.positions)

    logging.info("The new game has started. Speed %d", SPEED)

    while True:
        clock.tick(SPEED)
        apple.draw()
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        snake.draw()

        # main logic. check if snake ate an apple
        if snake.get_head_position() == apple.position:
            snake.add_segment(0, apple.position)
            logging.info("Snake ate an apple. Snake length %d",
                         len(snake.positions))
            apple.randomize_position(snake.positions)

        # main logic. check if the snake bit itself
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            # removing Rect of an old apple position from board
            apple.remove_segments_from_board([apple.position])
            apple.randomize_position(snake.positions)
            logging.info("The snake has bit itself. Snake has reseted")

        pg.display.update()


if __name__ == "__main__":
    # Logging configure
    logging.basicConfig(
        filename="login.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    main()
