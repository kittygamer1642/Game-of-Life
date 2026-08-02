import pygame
import os
import math
import time
import tkinter as tk
from tkinter import filedialog
import sys

os.environ['SDL_AUDIODRIVER'] = 'dsp'

version = 'V2.1'

# setup pygame window
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Conway's Game of Life")

# simulation rules
grid_file = open('grid.txt', 'r')
grid_settings = grid_file.readlines()
lonely = int(grid_settings[2]) # minimum number of neighbors needed for a cell to survive (2 in the original Game of Life)
overcrowd = int(grid_settings[3]) # maximum number of neighbors needed for a cell to survive (4 in the original Game of Life)
born = int(grid_settings[4]) # number of neighbors needed for a cell to come to life (3 in the Original game of Life)

# world size
WORLD_WIDTH = int(grid_settings[0])
WORLD_HEIGHT = int(grid_settings[1])

DEFAULT_SIZE = int(grid_settings[5])
CELL_SIZE = DEFAULT_SIZE

simulation_rate = 30 # speed of the simulation in generations per second

tool = 'pen' # currently selected tool when editing

SCROLL_X = round(((WORLD_WIDTH * 10) / 2) - 400)
SCROLL_Y = round(((WORLD_HEIGHT * 10) / 2) - 250)
SCROLL_SPEED = 0.8

grid = bool(grid_settings[6])

# fonts
font1 = pygame.font.Font(None, 32)

# buttons
toggle_tool = pygame.Rect(0, 500, 50, 50)
pen_tool = pygame.Rect(50, 500, 50, 50)
erase_tool = pygame.Rect(100, 500, 50, 50)

save_button = pygame.Rect(150, 500, 50, 50)
open_button = pygame.Rect(200, 500, 50, 50)

grid_toggle = pygame.Rect(750, 500, 50, 50)

zoom_in = pygame.Rect(0, 550, 25, 25)
zoom_out = pygame.Rect(25, 550, 25, 25)

def choose_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    root.update()
    file_path = filedialog.askopenfilename(
        title="Select a save file",
        filetypes=[
            ("Life grids", "*.life"),
        ]
    )
    root.destroy()
    return file_path

def save_as():
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    root.update()
    file_path = filedialog.asksaveasfilename(
        title="Save the grid",
        filetypes=[
            ("Life grids", "*.life"),
        ]
    )
    root.destroy()
    return file_path

# images
def load_scaled(name, size):
    image = pygame.image.load(name)
    return pygame.transform.scale(image, size)

toggle_img = load_scaled('toggle.png', (50, 50))
pen_img = load_scaled('pencil.png', (50, 50))
erase_img = load_scaled('eraser.png', (50, 50))
save_img = load_scaled('save.png', (50, 50))
open_img = load_scaled('open.png', (50, 50))

zoom_in_img = load_scaled('zoom+.png', (25, 25))
zoom_out_img = load_scaled('zoom-.png', (25, 25))

menu_bg = pygame.Rect(0, 500, 800, 100)

class cell:
    def __init__(self, row, col, alive = False):
        self.row = row
        self.col = col
        self.alive = alive
        self.next = alive
        self.rect = pygame.Rect(self.col * CELL_SIZE, self.row * CELL_SIZE, CELL_SIZE - 0.5, CELL_SIZE - 0.5)
    
    def is_alive(self, row_offset, col_offset):
        try:
            return cells[self.row + row_offset][self.col + col_offset].alive
        except IndexError:
            return False
    
    # count the living cells around the cell
    def find_neighbors(self):
        neighbors = []
        
        # check the surrounding area for living cells
        neighbors.append(self.is_alive(0, -1))
        neighbors.append(self.is_alive(0, 1))
        neighbors.append(self.is_alive(-1, 0))
        neighbors.append(self.is_alive(1, 0))
        neighbors.append(self.is_alive(-1, -1))
        neighbors.append(self.is_alive(-1, 1))
        neighbors.append(self.is_alive(1, -1))
        neighbors.append(self.is_alive(1, 1))
        
        # count and return the number of living cells
        return neighbors.count(True);
    
    # determine the next state of the cell
    def step(self):
        neighbors = self.find_neighbors()
        # we use self.next instead of self.alive here because self.alive can't be changed until every cell is updated
        if neighbors < lonely or neighbors >= overcrowd:
            self.next = False # cell dies
        elif neighbors == born:
            self.next = True # cell comes to life
        else:
            self.next = self.alive # cell doesn't change
    
    # set the state of the cell to the next state
    def update(self):
        self.alive = self.next
    
    # toggle the cell between alive and dead
    def toggle(self):
        self.alive = not(self.alive)
    
    # draw the cell on the screen (black for alive, light gray for dead)
    def draw(self, x, y):
        self.rect.x = (self.col * CELL_SIZE) - x
        self.rect.y = (self.row * CELL_SIZE) - y
        if (self.rect.x >= (0 - (SCROLL_SPEED * 10)) and self.rect.x < 800) and (self.rect.y >= (0 - (SCROLL_SPEED * 10)) and self.rect.y < 600):
            color = (0, 0, 0) if self.alive else (240, 240, 240)
            color = (200, 200, 200) if self.rect.collidepoint(pygame.mouse.get_pos()) and not self.alive else color
            self.rect.width = CELL_SIZE - (1 if grid else 0)
            self.rect.height = CELL_SIZE -  (1 if grid else 0)
            pygame.draw.rect(screen, color, self.rect)

cells = [] # list of all the cell objects
world = [] # list of boolean values corresponding to the state of each cell

# functions

# create a grid of cells
def create_cell_grid(width, height):
    for row in range(height):
        cell_row = []
        for col in range(width):
            cell_row.append(cell(row, col))
        cells.append(cell_row)

# update the world list with the state of each cell
def update_world():
    global world
    world = []
    for row in cells:
        world_row = []
        for cell in row:
            world_row.append(cell.alive)
        world.append(world_row)

# update the state of each cell based on the number of living cells next to it
def step_cells():
    global generation
    for row in cells:
        for cell in row:
            cell.step() # determine the next state of each cell
    for row in cells:
        for cell in row:
            cell.update() # update the state of each cell
    
    generation += 1

# draw the current state of the world
def draw_world():
    if grid:
        screen.fill((100, 100, 100)) # fill screen with gray
    else:
        screen.fill((240, 240, 240)) # fill screen with cell color
    # draw each cell
    for row in cells:
        for cell in row:
                cell.draw(SCROLL_X, SCROLL_Y)

def save_grid(name):
    with open(f'{name}.life', 'w') as save:
        for row in cells:
            for col in row:
                if col.alive:
                    cell_list = [col.row, col.col]
                    save.write(str(cell_list))
                    save.write('\n')

def load_from_save(name, width, height):
    global cells
    with open(name, 'r') as save:
        save_lines = save.readlines() # store each line of the save file as a list
        
        # stop if file is empty
        if len(save_lines) == 0:
            return()
        
        cells = [] # clear the current cell grid
        i = 0
        for row in range(height):
            cell_row = []
            for col in range(width):
                try:
                    cell_pos = eval(save_lines[i]) # get the cell's position as a list
                except IndexError:
                    cell_pos = [0, 0] # set the position to 0 if i is not in the list
                if row == cell_pos[0] and col == cell_pos[1]:
                    cell_row.append(cell(row, col, True)) # create a live cell
                    i += 1
                else:
                    cell_row.append(cell(row, col, False)) # create a dead cell
            cells.append(cell_row) # add the row to the cells list
            
            
    update_world()

def load_grid_data():
    global grid_data, WORLD_WIDTH, WORLD_HEIGHT, lonley, overcrowd, born, simulation_rate, grid
    with open('grid.txt', 'r') as grid:
        grid_data = grid.readlines()
        WORLD_WIDTH = int(grid_data[0])
        WORLD_HEIGHT = int(grid_data[1])
        
        lonley = int(grid_data[2])
        overcrowd = int(grid_data[3])
        born = int(grid_data[4])
        
        simulation_rate = int(grid_data[5])
        
        grid = eval(grid_data[6])

print(f'Welcome to The Game of Life {version}! Use the tools to draw an arrangement of cells and press space to run the simulation!')
load_grid_data() # load grid data from save file

# setup
create_cell_grid(WORLD_WIDTH, WORLD_HEIGHT) # create a 85x50 cell grid
update_world() # initalize the world list

load_from_save('backup.life', WORLD_WIDTH, WORLD_HEIGHT) # load the grid saved in the backup file

running = False # ensure simulation is paused

generation = 0

version_txt = font1.render(version, (0, 0, 0), True)

UP = False
LEFT = False
DOWN = False
RIGHT = False

ROW = 0
COL = 0

zoom = 100

# main loop
while True:
    for event in pygame.event.get():
        # exit the program if the user closes the window
        if event.type == pygame.QUIT:
            save_grid('backup.life') # save the current grid in a file before closing
            pygame.quit()
            sys.exit()
        
        mouse_pos = pygame.mouse.get_pos() # get mouse position
        mouse_down = pygame.mouse.get_pressed() # get the state of each mouse button
        
        if mouse_pos[1] <= 500:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR) # set the cursor to a crosshair when it's over the cell grid
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW) # set the cursor to an arrow when is's over the toolbar
        
        ROW = math.floor(((mouse_pos[1] + SCROLL_Y) / 10) / (CELL_SIZE / DEFAULT_SIZE))
        COL = math.floor(((mouse_pos[0] + SCROLL_X) / 10) / (CELL_SIZE / DEFAULT_SIZE))
        
        # check for mouse events
        if mouse_down[0]:
            if mouse_pos[1] < 500:
                if event.type == pygame.MOUSEBUTTONDOWN and tool == 'toggle':
                    # toggle the state of the cell
                    try:
                        cells[ROW][COL].toggle() # try to toggle the state of the cell
                    except IndexError:
                        pass
                
                elif tool == 'pen':
                    # toggle the state of the cell
                    try:
                        cells[ROW][COL].alive = True # try to set the cell to alive
                    except IndexError:
                        pass
    
                else:
                    # toggle the state of the cell
                    try:
                        cells[ROW][COL].alive = False # try to set the cell to alive
                    except IndexError:
                        pass
            
            if toggle_tool.collidepoint(mouse_pos):
                tool = 'toggle'
            elif pen_tool.collidepoint(mouse_pos):
                tool = 'pen'
            elif erase_tool.collidepoint(mouse_pos):
                tool = 'eraser'
            elif save_button.collidepoint(mouse_pos) and not running:
                name = save_as()
                save_grid(name)
                print('Done.')
            elif open_button.collidepoint(mouse_pos) and not running:
                try:
                    name = choose_file();
                    load_from_save(name, WORLD_WIDTH, WORLD_HEIGHT)
                    print('Done.')
                except FileNotFoundError:
                    print(f'No save named "{name}" found.')
            elif grid_toggle.collidepoint(mouse_pos):
                grid = not grid
            elif zoom_in.collidepoint(mouse_pos):
                CELL_SIZE += 1
                zoom = (CELL_SIZE / DEFAULT_SIZE) * 100
            elif zoom_out.collidepoint(mouse_pos):
                CELL_SIZE -= 1
                zoom = (CELL_SIZE / DEFAULT_SIZE) * 100
        
        # handle key events
        keyboard = pygame.key.get_pressed()
        
        UP = keyboard[pygame.K_UP]
        LEFT = keyboard[pygame.K_LEFT]
        DOWN = keyboard[pygame.K_DOWN]
        RIGHT = keyboard[pygame.K_RIGHT]
        
        if event.type == pygame.KEYDOWN:
            # start/stop the simulation when the user presses space
            if keyboard[pygame.K_SPACE]:
                running = not(running)
                if running:
                    print('Simulation is running.')
                else:
                    print('Simulation is paused.')
            
            # move the simulation forward one generation when the enter key is pressed
            if keyboard[pygame.K_RETURN]:
                step_cells()
            
            # reset the grid when the user presses r
            if keyboard[pygame.K_r]:
                cells = []
                create_cell_grid(WORLD_WIDTH, WORLD_HEIGHT)
                SCROLL_X = round(((WORLD_WIDTH * 10) / 2) - 400)
                SCROLL_Y = round(((WORLD_HEIGHT * 10) / 2) - 250)
                update_world()
                generation = 0
            
                
    # scrolling is done outside event loop for smoother motion
    if UP:
        if SCROLL_Y > 0:
            SCROLL_Y -= CELL_SIZE * SCROLL_SPEED
    
    if LEFT:
        if SCROLL_X > 0:
            SCROLL_X -= CELL_SIZE * SCROLL_SPEED
    
    if DOWN:
        if SCROLL_Y < (WORLD_HEIGHT - 50) * CELL_SIZE:
            SCROLL_Y += CELL_SIZE * SCROLL_SPEED
    
    if RIGHT:
        if SCROLL_X < (WORLD_WIDTH - 80) * CELL_SIZE:
            SCROLL_X += CELL_SIZE * SCROLL_SPEED
    
    if SCROLL_Y < 0:
        SCROLL_Y = 0
    
    if SCROLL_Y > (WORLD_HEIGHT - 50) * CELL_SIZE:
        SCROLL_Y = (WORLD_HEIGHT - 50) * CELL_SIZE
    
    if SCROLL_X < 0:
        SCROLL_X = 0
    
    if SCROLL_X > (WORLD_WIDTH - 80) * CELL_SIZE:
        SCROLL_X = (WORLD_WIDTH - 80) * CELL_SIZE
    
    
    if mouse_pos[1] < 500:
        X = math.floor((mouse_pos[0] + SCROLL_X) / 10)
        Y = math.floor((mouse_pos[1] + SCROLL_Y) / 10)
    
    if running:
        step_cells()
    
    update_world()
    
    # count the total number of alive cells
    total_alive = 0
    for row in world:
        total_alive += row.count(True)
    
    # create text objects for simulation variables
    alive_txt = font1.render(f'Population: {total_alive}', (0, 0, 0), True)
    generation_txt = font1.render(f'Generation: {generation}', (0, 0, 0), True)
    world_size_txt = font1.render(f'World size: {WORLD_WIDTH}x{WORLD_HEIGHT}', (0, 0, 0), True)
    simulation_txt = font1.render(f'Speed: {simulation_rate} gen/sec', (0, 0, 0), True)
    rules_txt = font1.render(f'Born: {born} Min: {lonely} Max: {overcrowd}', (0, 0, 0), True)
    scroll_txt = font1.render(f'Pos: ({X}, {Y})', (0, 0, 0), True)
    zoom_txt = font1.render(f'Zoom: {round(zoom)}%', (0, 0, 0), True)
    
    # draw and update display
    draw_world()
    
    pygame.draw.rect(screen, (255, 255, 255), menu_bg)
    
    if not running:
        #draw each edit button
        screen.blit(toggle_img, (0, 500))
        screen.blit(pen_img, (50, 500))
        screen.blit(erase_img, (100, 500))
        screen.blit(save_img, (150, 500))
        screen.blit(open_img, (200, 500))
        
        #draw a border on each button
        pygame.draw.rect(screen, (150, 150, 150) if tool == 'toggle' else (0, 0, 0), toggle_tool, 2)
        pygame.draw.rect(screen, (150, 150, 150) if tool == 'pen' else (0, 0, 0), pen_tool, 2)
        pygame.draw.rect(screen, (150, 150, 150) if tool == 'eraser' else (0, 0, 0), erase_tool, 2)
        pygame.draw.rect(screen, (0, 0, 0), save_button, 2)
        pygame.draw.rect(screen, (0, 0, 0), open_button, 2)
    
    screen.blit(zoom_in_img, (0, 550))
    pygame.draw.rect(screen, (0, 0, 0), zoom_in, 2)
    screen.blit(zoom_out_img, (25, 550))
    pygame.draw.rect(screen, (0, 0, 0), zoom_out, 2)
    
    # draw grid toggle
    pygame.draw.rect(screen, (175, 175, 175), grid_toggle)
    pygame.draw.rect(screen, (0, 0, 0), grid_toggle, 2)
    screen.blit(font1.render('Grid', (0, 0, 0), True), (752.5, 514))
    
    # draw each text object
    screen.blit(alive_txt, (260, 510))
    screen.blit(generation_txt, (500, 510))
    screen.blit(world_size_txt, (260, 540))
    screen.blit(simulation_txt, (500, 540))
    screen.blit(rules_txt, (260, 570))
    screen.blit(scroll_txt, (500, 570))
    screen.blit(zoom_txt, (55, 555))
    screen.blit(version_txt, (0, 580))
    
    pygame.display.flip()
    
    if running:
        time.sleep(1 / simulation_rate) # short time delay between frames
