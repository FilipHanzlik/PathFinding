import pygame
from queue import PriorityQueue
from collections import deque

pygame.init()

WIDTH = 1000
HEIGHT = 800
WIDTH_OF_GRID = 800
HEIGHT_OF_GRID = 800
ROWS = 50
VISUALISATION = True # This variable decides if the visualization of the path finding will be shown
ALGORITM_RUNNING = False # While this variable is set to True the interface doesnt accept any input excepted the close 'x'. Meanwhile the algoritm is finding the shortest path
start, end = None, None # Here are stored the start and the end cubes
TYPES_OF_ALGORITMS = ['A*', 'Bread First Search', 'Djikstra'] # List of avalaible types of algoritms
TYPE_OF_ALGORITM = TYPES_OF_ALGORITMS[0] # this variable decides which algoritm will be used to find the shortest path
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('path_finding algoritms')

# rgb colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Button:

    def __init__(self, id, x, y, height, width, color, func=None, border_width=0, border_color=None, texts={}):
        self.id = id # this id will be used in the is_clicked method to check if it need to add itself as an argument to the function
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.color = color
        self.border_width = border_width
        self.border_color = border_color
        self.func = func  # this function will be use if the button is clicked
        self.texts = texts # The text will be composided of parts
        self.total_texts_width = 0 # This stores the total lenght of the text displayed (will be used for centering the text)
        self.temp_text_width = 0 # Store the width of the parts of the text that have already been displayed, to know where to display the next part
    
    def __str__(self):
        return str(list(self.texts.keys()))
    
    def is_clicked(self, pos):
        """ Check if the button was clicked and if yes run the function that is assigned to the button """
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                if self.id in ['visualization', 'change_algoritm']: # These buttons needs themselves as arguments                    
                    self.func(self)
                else:
                    self.func()

    def draw(self, surface):
        if self.border_width:
            if type(self.border_width) == int:
                if self.border_width >= 0:
                    pygame.draw.rect(surface, self.border_color, (self.x, self.y, self.width, self.height))
                else:
                    raise ValueError(f"Border width must be positive not {self.border_width}")
            else:
                raise ValueError(f"Border width must have the type of integer not {type(self.border_width)}")
        pygame.draw.rect(surface, self.color, (self.x + self.border_width, self.y + self.border_width, self.width - self.border_width * 2, self.height - self.border_width * 2))

        if self.texts:
            self.temp_text_width = 0
            self.total_texts_width = 0
            
            for key in self.texts.keys():
                # the word is the key and the values are its attributes
                if self.texts[key]['active']: # if the valide attribute is set to false the word will be skiped
                    font = pygame.font.SysFont(self.texts[key]['font'], int(self.height / 100 * self.texts[key]['height']))
                    text = font.render(key, 1, BLACK)
                    self.total_texts_width += text.get_width()

            for key in self.texts.keys():
                if self.texts[key]['active']: # if the valide attribute is set to false the word will be skiped, hence not displayed
                    font = pygame.font.SysFont(self.texts[key]['font'], int(self.height / 100 * self.texts[key]['height']))
                    text = font.render(key, 1, self.texts[key]['color'])
                    surface.blit(text, (self.x + (self.width - self.total_texts_width) // 2 + self.temp_text_width, self.y + (self.height - text.get_height()) // 2))
                    self.temp_text_width += text.get_width()


class Queue:

    def __init__(self):
        self.queue = deque()
    
    def append(self, obj):
        self.queue.appendleft(obj)
    
    def pop(self):
        return self.queue.pop()
    
    def is_empty(self):
        return len(self.queue) == 0
    
    def lenght(self):
        return len(self.queue)


class Cube:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.color = WHITE
        self.width = WIDTH_OF_GRID // ROWS
        self.neighbors = []

    def __str__(self):
        return f'({self.row}, {self.col}) - {self.color}'
    
    def __lt__(self, other):
        # used when comparing two cubes by the == operator
        if self.get_pos() == other.get_pos():
            return True
        else:
            return False
    
    def make_start(self):
        self.color = ORANGE
    
    def make_end(self):
        self.color = TURQUOISE
    
    def make_obstacle(self):
        self.color = BLACK

    def make_open(self):
        self.color = GREEN
    
    def make_close(self):
        self.color = RED

    def make_path(self):
        self.color = PURPLE

    def reset(self):
        self.color = WHITE

    def is_obstacle(self):
        return self.color == BLACK
    
    def is_path(self):
        return self.color == PURPLE

    def is_closed(self):
        return self.color == RED
    
    def is_open(self):
        return self.color == GREEN
    
    def is_blank(self):
        return self.color == WHITE

    def get_pos(self):
        return self.row, self.col

    def get_neighbors(self, grid):
        self.neighbors = []
        if self.row > 0 and not grid[self.row - 1][self.col].is_obstacle(): # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < ROWS - 1 and not grid[self.row][self.col + 1].is_obstacle(): # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.row < ROWS - 1 and not grid[self.row + 1][self.col].is_obstacle(): # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.col > 0 and not grid[self.row][self.col - 1].is_obstacle(): # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.col * self.width, self.row * self.width, self.width, self.width))


def main(surface):
    global ALGORITM_RUNNING, start, end
    zakladnicyklus = True
    grid = create_grid()

    ## buttons ## (The y coordinate of a button is thy y coordinate of the previous button plus the previous button height)
    buttons = []

    # visualization button
    visualisation_button_texts = {
        'Visualizations:': {
            'font': 'comicsans',      
            'height': 50,               # height in percents
            'color': BLACK,
            'active': True
        },
        
        '  ON': {
            'font': 'comicsans',
            'height': 70,
            'color': GREEN,
            'active': True
        },

        ' OFF': {
            'font': 'comicsans',
            'height': 70,
            'color': RED,
            'active': False
        }
    }
    visualisation_button = Button('visualization', WIDTH_OF_GRID, 0, 50, WIDTH - WIDTH_OF_GRID, WHITE, visualisation_button_function, border_width=3, border_color=GREEN, texts=visualisation_button_texts)
    
    # clear path button
    clear_path_button_texts = {
        'Clear path': {
            'font': 'comicsans',
            'height': 50,
            'color': BLACK,
            'active': True
        }
    }
    clear_path_button = Button('clear_path', WIDTH_OF_GRID, visualisation_button.height, 50, WIDTH - WIDTH_OF_GRID, WHITE, lambda: clear_path(grid), border_width=3, border_color=BLACK, texts=clear_path_button_texts)
    
    # clear all button
    clear_all_button_texts = {
        'Clear all': {
            'font': 'comicsans',
            'color': BLACK,
            'height': 50,
            'active': True
        }
    }
    clear_all_button = Button('clear_all', WIDTH_OF_GRID, clear_path_button.y + clear_path_button.height, 50, WIDTH - WIDTH_OF_GRID, WHITE, lambda: clear_all(grid), border_width=3, border_color=BLACK, texts=clear_all_button_texts)

    # button for switching algoritms
    change_algoritm_button_texts = {
        'Type:': {
            'font': 'comicsans',
            'height': 50,
            'color': BLACK,
            'active': True 
        },

        ' ' + TYPES_OF_ALGORITMS[0]: {
            'font': 'comicsans',
            'height': 55,
            'color': BLACK,
            'active': True 
        },

        ' ' + TYPES_OF_ALGORITMS[1]: {
            'font': 'comicsans',
            'height': 45,
            'color': BLACK,
            'active': False
        },

        ' ' + TYPES_OF_ALGORITMS[2]: {
            'font': 'comicsans',
            'height': 50,
            'color': BLACK,
            'active': False
        }
    }
    change_algoritm_button = Button('change_algoritm', WIDTH_OF_GRID, clear_all_button.y + clear_all_button.height, 50, WIDTH - WIDTH_OF_GRID, WHITE, change_algoritm_button_function, border_width=3, border_color=BLACK, texts=change_algoritm_button_texts)

    # button for starting the path_finding algoritm
    run_button_texts = {
        'Run': {
            'font': 'comicsans',
            'height': 60,
            'color': BLACK,
            'active': True
        }
    }
    run_button = Button('run', WIDTH_OF_GRID, change_algoritm_button.y + change_algoritm_button.height, 50, WIDTH - WIDTH_OF_GRID, WHITE, lambda: run_button_function(surface, grid, buttons), border_width=3, border_color=BLACK, texts=run_button_texts)

    buttons.extend([visualisation_button, clear_path_button, clear_all_button, change_algoritm_button, run_button])
    ## end of buttons ##

    while zakladnicyklus:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                zakladnicyklus = False
            
            if ALGORITM_RUNNING: # If the algoritm is finding the shortest path any other input except pygame.QUIT won't be accepted 
                continue

            if pygame.mouse.get_pressed()[0]: # Left mouse button
                pos = pygame.mouse.get_pos()
                if pos[0] >= WIDTH_OF_GRID:
                    for button in buttons:
                        button.is_clicked(pos)
                    continue # apply to the 'for event in pygame.event.get()'. If we got here, it means that the click was in the button area and hence there is no need to run the rest of the loop
                
                row, col = get_row_col_from_pos(pos) # converts the x and y coordinate to the row and col in the grid of cubes (row and col starts at 0)
                cube = grid[row][col] # get the clicked cu 
                
                if not start and cube != end and not cube.is_obstacle():
                    start = cube
                    cube.make_start()
                
                elif not end and cube != start and not cube.is_obstacle():
                    end = cube
                    cube.make_end()
                
                elif cube.color == WHITE:
                    cube.make_obstacle()
                
            if pygame.mouse.get_pressed()[2]: # Right mouse button
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_pos(pos)
                cube = grid[row][col]
                cube.reset()
            
                if cube == start:
                    start = None
                
                elif cube == end:
                    end = None

        redraw_window(surface, grid, buttons)

    pygame.quit()


def algoritms(surface, type, grid, buttons, start, end):
    if type == 'A*':
        count = 0
        f_scores = {spot: float('inf') for row in grid for spot in row}
        f_scores[start] = h(start.get_pos(), end.get_pos())
        g_scores = {spot: float('inf') for row in grid for spot in row}
        g_scores[start] = 0
        came_from = {}
        open_set = PriorityQueue()
        open_set.put([0, count, start])
        open_set_hash = {start}

        while not open_set.empty():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            current = open_set.get()[2]
            open_set_hash.remove(current)

            if current == end:
                while current:
                    current = came_from[current]
                    if current == start:
                        break
                    current.make_path()

                return True

            for neighbor in current.neighbors:
                temp_g_score = g_scores[current] + 1
                if temp_g_score < g_scores[neighbor]:
                    came_from[neighbor] = current
                    g_scores[neighbor] = temp_g_score
                    f_scores[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())

                    if neighbor not in open_set_hash:
                        count += 1
                        open_set_hash.add(neighbor)
                        open_set.put([f_scores[neighbor], count, neighbor])
                        if VISUALISATION:
                            if neighbor != end:
                                neighbor.make_open()
            
            if VISUALISATION:
                redraw_window(surface, grid, buttons)

                if current != start:
                    current.make_close()

        print('not found')
        return False

    elif type == 'Bread First Search':
        
        my_queue = Queue()
        my_queue.append(start)
        came_from = {}

        while not my_queue.is_empty():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            current = my_queue.pop()

            if current == end:
                path = came_from[current]
                while path != start:
                    path.make_path()
                    path = came_from[path]
                end.make_end()

                if not VISUALISATION:
                    for row in grid:
                        for cube in row:
                            if cube.is_closed() or cube.is_open():
                                cube.reset()

                return True

            for neighbor in current.neighbors:
                if neighbor.is_blank() or neighbor == end:
                    neighbor.make_open()
                    came_from[neighbor] = current
                    my_queue.append(neighbor)
                else:
                    continue

            if current != start:
                current.make_close()

            if VISUALISATION:
                redraw_window(surface, grid, buttons)

        print('NOT FOUND')
        return False

    elif type == 'Djikstra':
        came_from = {}
        distances = {cube: float('inf') for row in grid for cube in row}
        distances[start] = 0
        count = 0
        my_queue = PriorityQueue()
        my_queue.put([0, count, start])
        my_queue_hash = {start}
        seen = []

        while not my_queue.empty():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            current = my_queue.get()[2]
            my_queue_hash.remove(current)

            if current == end:
                current = end
                while came_from[current] != start:
                    current = came_from[current]
                    current.make_path()
                    if VISUALISATION:
                        redraw_window(surface, grid, buttons)
                return True
            
            for neighbor in current.neighbors:
                if neighbor in seen:
                    continue
            
                if distances[neighbor] > distances[current] + 1:
                    distances[neighbor] = distances[current] + 1
                    came_from[neighbor] = current
                    
                    if current not in my_queue_hash:
                        count += 1
                        my_queue.put([distances[neighbor], count, neighbor])
                        my_queue_hash.add(neighbor) 

                    if VISUALISATION:
                        if neighbor != end:
                            neighbor.make_open()
            
            seen.append(current)

            if VISUALISATION:
                if current != start:
                    current.make_close()
                redraw_window(surface, grid, buttons)

        
        print('Not Found')
        return False


def visualisation_button_function(button):
    global VISUALISATION
    for key in button.texts.keys():
        if button.texts[key]['active'] and key != 'Visualizations:':
            if 'ON' in key:
                button.texts[key]['active'] = False
                button.texts[list(button.texts.keys())[2]]['active'] = True
                VISUALISATION = False
                button.border_color = RED
                break
            else:
                button.texts[key]['active'] = False
                button.texts[list(button.texts.keys())[1]]['active'] = True
                VISUALISATION = True
                button.border_color = GREEN
                break


def change_algoritm_button_function(button):
    global TYPE_OF_ALGORITM
    keys = list(button.texts.keys())
    if button.texts[keys[-1]]['active']:
        button.texts[keys[-1]]['active'] = False
        button.texts[keys[1]]['active'] = True
        TYPE_OF_ALGORITM = TYPES_OF_ALGORITMS[0]
    else:
        for i, key in enumerate(keys):
            if i > 0: # the first item is the word 'Types:'
                if button.texts[key]['active']:
                    button.texts[key]['active'] = False
                    button.texts[keys[i + 1]]['active'] = True
                    TYPE_OF_ALGORITM = TYPES_OF_ALGORITMS[i] # the position in types_of_algoritm is +1 because of the Type: key
                    break


def run_button_function(surface, grid, buttons):
    for row in grid:
        for cube in row:
            cube.get_neighbors(grid)
    ALGORITM_RUNNING = True
    clear_path(grid)
    algoritms(surface, TYPE_OF_ALGORITM, grid, buttons, start, end)
    ALGORITM_RUNNING = False

                
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def create_grid():
    grid = []
    for i in range(ROWS):
        grid.append([])
        for j in range(ROWS):
            grid[i].append(Cube(i, j))
    
    return grid


def draw_grid(surface):
    width_of_cubes = WIDTH_OF_GRID // ROWS
    for i in range(ROWS):
        pygame.draw.line(surface, GREY, (0, i * width_of_cubes), (WIDTH_OF_GRID, i * width_of_cubes))
        pygame.draw.line(surface, GREY, (i * width_of_cubes, 0), (i * width_of_cubes, WIDTH_OF_GRID))


def clear_path(grid):
    for row in grid:
        for cube in row:
            if cube.is_path() or cube.is_open() or cube.is_closed():
                cube.reset()


def clear_all(grid):
    global start, end
    start, end = None, None
    for row in grid:
        for cube in row:
            cube.reset()


def get_row_col_from_pos(pos):
    width_of_cubes = WIDTH_OF_GRID // ROWS
    x, y = pos
    row = y // width_of_cubes
    col = x // width_of_cubes
    return row, col


def redraw_window(surface, grid, buttons):
    surface.fill(GREY)
    for row in grid:
        for cube in row:
            cube.draw(surface)
    for button in buttons:
        button.draw(surface)
    draw_grid(surface)
    pygame.display.update()

main(win)