import random
import pickle
import curses
from stuff import get_random_message, get_random_quote, get_random_item

# Constants
MAZE_SIZE = 128  # Must be a power of 2, minimum 32
NUM_ITEMS = 100
NUM_STRANGERS = 50
RADIUS = 5
MESSAGE_LIMIT = 4

# Color pairs
COLOR_PAIR_TREASURE = 1
COLOR_PAIR_ITEM = 2
COLOR_PAIR_CHARACTER = 3
COLOR_PAIR_MESSAGE = 4
COLOR_PAIR_HEADER = 7
COLOR_PAIR_PLAYER = 6

class Cell:
    WALL = '#'
    PATH = ' '
    START = '@'
    TREASURE = '[^]'
    ITEM = '?'
    CHARACTER = '&'

class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[Cell.WALL for _ in range(width)] for _ in range(height)]

    def generate(self):
        start_x = self.width // 2
        start_y = self.height // 2
        self.grid[start_y][start_x] = Cell.PATH
        walls = [(start_x, start_y)]

        while walls:
            x, y = random.choice(walls)
            walls.remove((x, y))
            directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
            random.shuffle(directions)

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 1 <= nx < self.width - 1 and 1 <= ny < self.height - 1 and self.grid[ny][nx] == Cell.WALL:
                    wall_x, wall_y = x + dx // 2, y + dy // 2
                    if self.grid[ny][nx] == Cell.WALL:
                        self.grid[ny][nx] = Cell.PATH
                        self.grid[wall_y][wall_x] = Cell.PATH
                        walls.append((nx, ny))

        self.grid[start_y][start_x] = Cell.TREASURE

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

def load_maze(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

# Generate and save the maze
maze = Maze(MAZE_SIZE, MAZE_SIZE)  # Make the maze 256x256
maze.generate()
maze.save('maze.dat')

# Load the maze
maze = load_maze('maze.dat')

# Initial player position
player_x, player_y = 1, 1
maze.grid = [[Cell.WALL for _ in range(MAZE_SIZE)] for _ in range(MAZE_SIZE)]
maze.generate()

# Ensure initial player position has clear paths
maze.grid[player_y][player_x] = Cell.START
maze.grid[1][2] = Cell.PATH
maze.grid[2][1] = Cell.PATH
maze.grid[1][0] = Cell.WALL  # Reinforce boundaries if necessary

def sprinkle_items_characters(maze, num_items, num_characters):
    positions = []
    for _ in range(num_items + num_characters):
        while True:
            x, y = random.randint(0, maze.width - 1), random.randint(0, maze.height - 1)
            if maze.grid[y][x] == Cell.PATH and (x, y) not in positions:
                positions.append((x, y))
                break

    for i in range(num_items):
        x, y = positions[i]
        maze.grid[y][x] = Cell.ITEM

    for i in range(num_characters):
        x, y = positions[num_items + i]
        maze.grid[y][x] = Cell.CHARACTER

# Sprinkle items and characters with fair but random distribution
sprinkle_items_characters(maze, NUM_ITEMS, NUM_STRANGERS)

def colorize_message(stdscr, message):
    if "Congratulations" in message or "treasure" in message:
        stdscr.addstr(f"{message}\n", curses.color_pair(COLOR_PAIR_TREASURE))
    elif "item" in message:
        stdscr.addstr(f"{message}\n", curses.color_pair(COLOR_PAIR_ITEM))
    elif "Stranger" in message:
        stdscr.addstr(f"{message}\n", curses.color_pair(COLOR_PAIR_CHARACTER))
    else:
        stdscr.addstr(f"{message}\n", curses.color_pair(COLOR_PAIR_MESSAGE))

def display_ui(stdscr):
    stdscr.clear()
    stdscr.addstr(0, 0, f"Score: {score} | Move Count: {move_count} | Last Move: {last_move}", curses.color_pair(COLOR_PAIR_HEADER))
    
    # Calculate the top-left corner of the view
    view_top = max(0, player_y - RADIUS)
    view_left = max(0, player_x - RADIUS)
    
    # Ensure the player stays centered in the view
    for y in range(view_top, min(view_top + RADIUS * 2 + 1, maze.height)):
        for x in range(view_left, min(view_left + RADIUS * 2 + 1, maze.width)):
            if (x, y) == (player_x, player_y):
                stdscr.addstr(y - view_top + 1, (x - view_left) * 2, Cell.START, curses.color_pair(COLOR_PAIR_PLAYER))
            elif maze.grid[y][x] == Cell.CHARACTER:
                stdscr.addstr(y - view_top + 1, (x - view_left) * 2, maze.grid[y][x], curses.color_pair(COLOR_PAIR_CHARACTER))
            else:
                stdscr.addstr(y - view_top + 1, (x - view_left) * 2, maze.grid[y][x])
    
    stdscr.addstr(RADIUS * 2 + 2, 0, "-" * 40)
    for i, msg in enumerate(messages[-MESSAGE_LIMIT:]):  # Only display the last MESSAGE_LIMIT messages
        stdscr.addstr(RADIUS * 2 + 3 + i, 0, "  ")
        colorize_message(stdscr, msg)
    stdscr.addstr(RADIUS * 2 + 3 + min(len(messages), MESSAGE_LIMIT), 0, "-" * 40)
    stdscr.refresh()

score = 0
move_count = 0
last_move = ''
messages = ["B R A I D"]

def move_player(direction):
    global player_x, player_y, score, move_count, last_move
    if direction == 'W' and maze.grid[player_y - 1][player_x] != Cell.WALL:
        maze.grid[player_y][player_x] = Cell.PATH
        player_y -= 1
    elif direction == 'S' and maze.grid[player_y + 1][player_x] != Cell.WALL:
        maze.grid[player_y][player_x] = Cell.PATH
        player_y += 1
    elif direction == 'A' and maze.grid[player_y][player_x - 1] != Cell.WALL:
        maze.grid[player_y][player_x] = Cell.PATH
        player_x -= 1
    elif direction == 'D' and maze.grid[player_y][player_x + 1] != Cell.WALL:
        maze.grid[player_y][player_x] = Cell.PATH
        player_x += 1
    else:
        messages.append("Invalid move. Try a different direction.")
        return

    current_cell = maze.grid[player_y][player_x]

    if current_cell == Cell.ITEM:
        item, item_score = get_random_item()
        score += item_score
        messages.append(f"You picked up a {item}! +{item_score} points.")
    elif current_cell == Cell.CHARACTER:
        messages.append(f"Stranger: '{get_random_quote()}'")
    elif current_cell == Cell.TREASURE:
        messages.append("You found the treasure! Congratulations!")

    if random.random() < 0.02:  # 2% chance to display a random message
        messages.append(get_random_message())

    if len(messages) > MESSAGE_LIMIT:
        messages.pop(0)  # Remove the oldest message to keep the list size within MESSAGE_LIMIT

    maze.grid[player_y][player_x] = Cell.START
    last_move = direction
    move_count += 1

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(COLOR_PAIR_TREASURE, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(COLOR_PAIR_ITEM, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(COLOR_PAIR_CHARACTER, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(COLOR_PAIR_MESSAGE, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(COLOR_PAIR_HEADER, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(COLOR_PAIR_PLAYER, curses.COLOR_RED, curses.COLOR_BLACK)
    
    stdscr.nodelay(True)
    display_ui(stdscr)
    while True:
        key = stdscr.getch()
        if key == curses.KEY_UP or key == ord('w'):
            move_player('W')
        elif key == curses.KEY_DOWN or key == ord('s'):
            move_player('S')
        elif key == curses.KEY_LEFT or key == ord('a'):
            move_player('A')
        elif key == curses.KEY_RIGHT or key == ord('d'):
            move_player('D')
        elif key == 27:  # ESC key
            break
        display_ui(stdscr)
        if maze.grid[player_y][player_x] == Cell.TREASURE:
            stdscr.addstr(RADIUS * 2 + 4 + min(len(messages), MESSAGE_LIMIT) + 1, 0, "Game Over! You found the treasure!")
            stdscr.refresh()
            stdscr.getch()
            break

curses.wrapper(main)
