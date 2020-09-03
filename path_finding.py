import pygame
from queue import PriorityQueue
from collections import deque

pygame.init()

WIDTH = 1000
HEIGHT = 800
WIDTH_OF_GRID = 800
HEIGHT_OF_GRID = 800
ROWS = 50
VISUALISATION = True
ALGORITM_RUNNING = False
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('path_finding algoritms')

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

    def __init__(self, x, y, height, width, color, func=None, border_width=0, border_color=None, texts={}):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.color = color
        self.border_width = border_width
        self.border_color = border_color
        self.total_texts_width = 0 
        self.temp_text_width = 0
        self.func = func  # this function will be use if the button is clicked
        self.texts = texts
    
    def is_clicked(self, pos):
        """ Check if the button was clicked and if yes run the function that is assigned to the button """

        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                self.func(self)

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
            self.total_texts_width = sum([pygame.font.SysFont(self.texts[key]['font'], int(self.height / 100 * self.texts[key]['height'])).render(key, 1, BLACK).get_width() for key in self.texts.keys()])
            
            for key in self.texts.keys():

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
        if self.row < ROWS - 1 and not grid[self.row + 1][self.col].is_obstacle(): # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_obstacle(): # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < ROWS - 1 and not grid[self.row][self.col + 1].is_obstacle(): # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_obstacle(): # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.col * self.width, self.row * self.width, self.width, self.width))


def main(surface):
    global ALGORITM_RUNNING

    zakladnicyklus = True
    start, end = None, None
    grid = create_grid()

    ## buttons ##
    buttons = []

    visualisation_button_texts = {
        'Visualizations:  ': {
            'font': 'comicsans',      
            'height': 50,               # height in percents
            'color': BLACK
        },
        
        'ON': {
            'font': 'comicsans',
            'height': 70,
            'color': GREEN
        }
    }
    visualisation_button = Button(WIDTH_OF_GRID, 0, 50, WIDTH - WIDTH_OF_GRID, WHITE, visualisation_button_function, border_width=3, border_color=GREEN, texts=visualisation_button_texts)
    buttons.append(visualisation_button)
    ## end of buttons ##

    while zakladnicyklus:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                zakladnicyklus = False
            
            if ALGORITM_RUNNING:
                continue

            if pygame.mouse.get_pressed()[0]: # Left mouse button
                pos = pygame.mouse.get_pos()
                if pos[0] > WIDTH_OF_GRID:
                    for button in buttons:
                        button.is_clicked(pos)
                        break
                    continue
                
                row, col = get_row_col_from_pos(pos)
                cube = grid[row][col]
                
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

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for cube in row:
                            cube.get_neighbors(grid)
                    ALGORITM_RUNNING = True
                    algoritms(surface, 'A*', grid, buttons, start, end)
                    ALGORITM_RUNNING = False
            
                if event.key == pygame.K_c:
                    start, end = None, None
                    grid = create_grid()

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

    elif type == 'BreadFirstSearch':
        
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

def visualisation_button_function(button):
    global VISUALISATION
    if 'ON' in button.texts.keys():
        button.texts = {
            'Visualizations:  ': {
                'font': 'comicsans',      
                'height': 50,
                'color': BLACK
            },
            
            'OFF': {
                'font': 'comicsans',
                'height': 70,
                'color': RED
            }
        }
        button.border_color = RED
        VISUALISATION = False
    else:
        button.texts = {
            'Visualizations: ': {
                'font': 'comicsans',      
                'height': 50,
                'color': BLACK
            },
            
            'ON': {
                'font': 'comicsans',
                'height': 70,
                'color': GREEN
            }
        }
        button.border_color = GREEN
        VISUALISATION = True

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