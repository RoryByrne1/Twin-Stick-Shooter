from math import ceil

import pygame

from constants import *
from utility_functions import get_key, check_index, split
from utility_classes import Pixel, ImageButton, Stack
from images import undo_image, redo_image, clear_image, eraser_image, eraser_image_pressed
from sounds import button_click, hover_effect

#======================Colour Grid Class======================# 
# a grid of selectable coloured pixels
# used to change the colours of the CharacterDisplay grid and to change colour in the DrawingGrid
class ColourGrid():
    def __init__(self, pos, colours, max_width, hex_colour=None, locked_list=None):
        self.__colours = colours
        self.__max_width = max_width

        # creates the grid as a 2D array of pixels
        self.__grid = []
        for row in range(ceil(len(self.__colours)/self.__max_width)): # number of rows
            current_row = []
            for column in range(self.__max_width):
                if check_index(self.__colours, column + row*max_width): # only creates a pixel if there is a colour to go with it
                    current_row.append(Pixel((pos[X] + column*EIGHT_PIXELS, pos[Y] + row*EIGHT_PIXELS), colour=self.__colours[column + row*self.__max_width]))
            self.__grid.append(current_row)
        self.__selected = self.__grid[0][0] # the selected pixel, defualted to the first pixel
        
        self.__hover = None

        self.__rect = pygame.Rect(pos, ((self.__max_width if len(self.__colours) / self.__max_width >= 1 else len(self.__colours) % self.__max_width)*EIGHT_PIXELS, ceil(len(self.__colours)/self.__max_width)*EIGHT_PIXELS))
        self.__border_rect = pygame.Rect((self.__rect.x - 5*PIXEL_RATIO, self.__rect.y - 2*PIXEL_RATIO), (self.__rect.width + 10*PIXEL_RATIO, self.__rect.height + EIGHT_PIXELS + 4*PIXEL_RATIO))

        # if a hex colour is passed as a paramter, set it as the selected colour
        if hex_colour: 
            self.__hex_to_selected(hex_colour)   
        self.__update_select_rect() 

        # if there are any locked colours
        if locked_list:
            for locked in locked_list:
                number = locked[1].execute(f"SELECT {locked[3]} FROM Players WHERE username = ?", (locked[2], )).fetchone()[0]
                if number <= locked[4]:
                    self.__grid[locked[0][0]][locked[0][1]].set_locked(True)
                    
    def __hex_to_selected(self, hex_colour): # changes the current selected pixel to the pixel with the colour specified by the hex
        index = self.__colours.index(get_key(hex_colour, BITMAP_DICTIONARY))
        self.__selected = self.__grid[index//self.__max_width][index%self.__max_width]

    def selected_to_hex(self): # returns the hex of the colour of the current selected pixel
        return BITMAP_DICTIONARY[self.__selected.get_colour()]
    
    def get_changed(self): # returns the changed status of the grid
        return self.__changed
    
    def get_rect(self): # returns the rect of the grid
        return self.__rect
    
    def get_selected(self): # returns the selected pixel
        return self.__selected
    
    def deselect(self): # deselect any selected pixel
        self.__selected = None

    def update(self, mpos, click): # changes the selected pixel if a pixel is clicked on
        self.__changed = False
        # if the user has clicked, loops through all the pixels to check if the mouse collides with any and updates the selected pixel if necessary
        if not self.__rect.collidepoint(mpos):
            self.__hover = None
        for row in self.__grid:
            for pixel in row:
                if pixel.get_rect().collidepoint(mpos) and not pixel.get_locked():
                    if click:
                        if self.__selected != pixel:
                            button_click.play()
                        self.__selected = pixel
                        self.__update_select_rect()
                        self.__changed = True  # changed is used to check if an update is needed elsewhere
                    else:
                        if not self.__hover or self.__hover != pixel:
                            if self.__selected != pixel:
                                hover_effect.play()
                            self.__hover = pixel
                            self.__update_hover_rect()
                        
    def __update_select_rect(self): # updates a rect that is used as the border for the selected pixel
        self.__select_rect = pygame.Rect((self.__selected.get_pos()[X] - 1*PIXEL_RATIO, self.__selected.get_pos()[Y] - 1*PIXEL_RATIO), (EIGHT_PIXELS + 2*PIXEL_RATIO, EIGHT_PIXELS + 2*PIXEL_RATIO))
    
    def __update_hover_rect(self): # update a rect that is used as the border for the hovered over pixel
        self.__hover_rect = pygame.Rect((self.__hover.get_pos()[X] - 1*PIXEL_RATIO, self.__hover.get_pos()[Y] - 1*PIXEL_RATIO), (EIGHT_PIXELS + 2*PIXEL_RATIO, EIGHT_PIXELS + 2*PIXEL_RATIO))

    def draw_border_rect(self, screen): # draws a border for the grid
        pygame.draw.rect(screen, BUTTON_HOVER_COLOUR, self.__border_rect) 

    def draw(self, screen): # draws the grid to the screen
        # draws each pixel
        for row in self.__grid:
            for pixel in row:
                pixel.draw(screen)
        # if there is a selected pixel, draw the select_rect with the same colour and the pixel again over it
        if self.__hover:
            pygame.draw.rect(screen, self.__hover.get_colour(), self.__hover_rect)
        if self.__selected:
            pygame.draw.rect(screen, self.__selected.get_colour(), self.__select_rect)
        
#======================Drawing Grid Class======================# 
# creates a grid that can be drawn onto by the user
# the colour can be picked by a colour grid
# there are also buttons to undo, redo, clear, and use an eraser
class DrawingGrid():
    def __init__(self, pos, columns, rows, colours, initial_hex=None):
        self.__rows = rows
        self.__columns = columns

        self.__grid = [[Pixel((pos[X]+(column*EIGHT_PIXELS), pos[Y]+(row*EIGHT_PIXELS)), background_colour=WHITE) for column in range(self.__columns)] for row in range(self.__rows)] 
        self.__rect = pygame.Rect(pos, (self.__columns*EIGHT_PIXELS, self.__rows*EIGHT_PIXELS))
        self.__border_rect = pygame.Rect((self.__rect.x - 2*PIXEL_RATIO, self.__rect.y - 2*PIXEL_RATIO), (self.__rect.width + 4*PIXEL_RATIO, self.__rect.height + 4*PIXEL_RATIO))
        
        # the drawing grid has an undo button, redo button, clear button, eraser button, and a colour grid to select the drawing colour from
        self.__undo_stack = Stack()
        self.__redo_stack = Stack()

        self.__undo_button = ImageButton((pos[X] + self.__columns*EIGHT_PIXELS + EIGHT_PIXELS, pos[Y] + EIGHT_PIXELS), (EIGHT_PIXELS, EIGHT_PIXELS), undo_image)
        self.__redo_button = ImageButton((pos[X] + self.__columns*EIGHT_PIXELS + EIGHT_PIXELS, pos[Y] + 2*EIGHT_PIXELS), (EIGHT_PIXELS, EIGHT_PIXELS), redo_image)
        self.__clear_button = ImageButton((pos[X] + self.__columns*EIGHT_PIXELS + EIGHT_PIXELS, pos[Y]), (EIGHT_PIXELS, EIGHT_PIXELS), clear_image)
        self.__erase_button = ImageButton((pos[X] + self.__columns*EIGHT_PIXELS + EIGHT_PIXELS, pos[Y] - 2*EIGHT_PIXELS), (EIGHT_PIXELS, EIGHT_PIXELS), eraser_image, hold=False, pressed_image=eraser_image_pressed)

        self.__colour_grid = ColourGrid((pos[X], pos[Y] - 2*EIGHT_PIXELS), colours, self.__columns)
        
        self.__previous_state = None
        self.__changed = False
        self.__drawn = False

        for i in range(self.__rows): # alternating grey and white background to represent a blank background
            row = self.__grid[i]
            for j in range(i%2,self.__columns,2):
                row[j].set_background_colour(CUSTOMISATION_GREY)

        if initial_hex: # if a hex value is passed in, set the current state of the drawing grid to the state the hex describes
            self.hex_to_grid(initial_hex)

    def grid_to_hex(self): # creates a single line hex string of the current state of the grid
        hex_string = ""
        for row in self.__grid:
            for pixel in row:
                hex_string += BITMAP_DICTIONARY[pixel.get_colour()]
        return hex_string

    def hex_to_grid(self, hex_string): # takes hex input and converts the drawing grid into the state specified by it
        hex_array = split(split(hex_string, COLOUR_DEPTH), self.__columns) # split hex string into individual colours in rows in the same format as the grid
        for row in range(self.__rows):
            for column in range(self.__columns):
                self.__grid[row][column].set_colour(get_key(hex_array[row][column], BITMAP_DICTIONARY)) # converts each pixel into each colour

    def update(self, mpos, clicking, click, unclick): # updates all the different aspects of the drawing grid
        self.__changed = False # changed is used to check if an update is needed elsewhere
        self.__colour_grid.update(mpos, click)   # update each button and importantly their pressed attributes
        self.__undo_button.update(mpos, click)
        self.__redo_button.update(mpos, click)
        self.__erase_button.update(mpos, click)
        self.__clear_button.update(mpos, click)
        if click:  # when you click, save the current state of the grid to a temporary variable in case you draw on the grid
            self.__previous_state = self.grid_to_hex()
        if self.__undo_button.get_clicked(): 
            self.__undo()
            self.__changed = True
        if self.__redo_button.get_clicked():
            self.__redo()
            self.__changed = True
        if self.__erase_button.get_clicked(): # deselect the colour from the select grid if the erase button is pressed
            self.__colour_grid.deselect()
        if self.__erase_button.get_pressed() and self.__colour_grid.get_selected(): # unpress the eraser button if the colour grid is selected
            self.__erase_button.unpress()
        if self.__clear_button.get_clicked():
            self.__clear()
            self.__undo_stack.push(self.__previous_state) # push the state of the grid before anything was changed onto the stack
            self.__changed = True
        if self.__drawn: # if you've drawn
            self.__redo_stack.reset()
            if unclick:  # if you've drawn and just released the mouse button
                self.__undo_stack.push(self.__previous_state) # push the state of the grid anything was changed onto the stack
                self.__drawn = False
                self.__changed = False
        if clicking:
            for row in self.__grid:
                for pixel in row:
                    if pixel.get_rect().collidepoint(mpos):
                        self.__drawn = True    # changed refers to any aspect of the drawing grid, drawn is only true if you have drawn onto the grid
                        self.__changed = True
                        if not self.__erase_button.get_pressed():
                            pixel.set_colour(self.__colour_grid.get_selected().get_colour())
                        else:
                            pixel.set_colour(None) # erase
    
    def __undo(self): # pushes the current state onto the redo stack and pops the previous state off of the undo stack
        if not self.__undo_stack.empty():
            self.__redo_stack.push(self.grid_to_hex())
            self.hex_to_grid(self.__undo_stack.pop())

    def __redo(self): # pushes the current state onto the undo stack and pops the previous state off of the redo stack
        if not self.__redo_stack.empty():
            self.__undo_stack.push(self.grid_to_hex())
            self.hex_to_grid(self.__redo_stack.pop())

    def __clear(self): # clears the grid 
        for row in self.__grid:
            for pixel in row:
                pixel.set_colour(None)

    def get_changed(self): # return the changed status of the drawing grid
        return self.__changed

    def draw(self, screen): # draws the drawing grid and all its aspects to the screen
        pygame.draw.rect(screen, PALER_BACKGROUND, self.__border_rect)
        for row in self.__grid:
            for pixel in row:
                pixel.draw(screen)
        self.__undo_button.draw(screen)
        self.__redo_button.draw(screen)
        self.__clear_button.draw(screen)
        self.__erase_button.draw(screen)
        self.__colour_grid.draw(screen)
