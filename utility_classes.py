from math import ceil

import pygame

from constants import *
from utility_functions import colour_swap, clip, round_to_nearest, split, get_key
from images import padlock_image
from sounds import button_click, hover_effect

#======================Stack Class======================# 
# used for the undo and redo buttons in the DrawingGrid class
class Stack():
    def __init__(self):
        self.__max_size = 100 # the maximum size of the stack
        self.__stack = []     # the stack itself implemented as a list

    def empty(self): # returns true if the stack is empty and false otherwise
        if self.__stack:
            return False
        else:
            return True

    def peek(self): # returns the last item in the stack
        return self.__stack[self.size()-1]

    def size(self): # returns the size of the stack
        return len(self.__stack)
    
    def push(self, item): # pushes an item onto the end of the stack, removing the first item if necessary
        if self.size() == self.__max_size:
            self.__stack = self.__stack[1:]
        self.__stack.append(item)

    def pop(self): # removes the last item from the stack and returns it
        return self.__stack.pop()
    
    def reset(self): # empties the stack
        self.__stack = []

#======================Queue Class======================# 
class Queue():
    def __init__(self):
        self.__queue = []     # the queue itself implemented as a list

    def empty(self): # returns true if the queue is empty and false otherwise
        if self.__queue:
            return False
        else:
            return True

    def peek(self): # returns the last item in the queue
        return self.__queue[0]

    def size(self): # returns the size of the queue
        return len(self.__queue)
    
    def enqueue(self, item): # pushes an item the end of the queue
        self.__queue.append(item)

    def dequeue(self): # removes the first item from the queue and returns it
        return self.__queue.pop(0)
    
    def reset(self): # empties the queue
        self.__queue = []

#======================Button Class======================#
# creates a pressable button that can be interacted with
# the parent class of TextButton and ImageButton, that are used all over the project
class Button():
    def __init__(self, pos, size, hold=True, pressed=False, disabled=False, pressed_delay=BUTTON_PRESSED_DELAY, border_colour=None):
        self._rect = pygame.Rect(pos, size)
        self.__hold = hold # whether or not the button has to be held down to stay pressed
        self.__pressed = pressed
        self.__clicked = False
        self.__hover = False
        self.__pressed_time = 0
        self.__pressed_delay = pressed_delay
        self.__border_colour = border_colour
        self.__disabled = disabled

    def set_disabled(self, disabled): # change the disabled status of the button
        self.__disabled = disabled

    def unpress(self): # unpress the button
        self.__pressed = False
        self._image = self._default_image

    def get_disabled(self):
        return self.__disabled

    def get_pressed(self): # return if the button is currently pressed
        return self.__pressed

    def get_clicked(self): # return if the button is currently clicked
        return self.__clicked

    def update(self, mpos, click): # update the image and state of the button based on the mouse position and click
        if self.__disabled:
            self._image = self._disabled_image
        else:
            if self.__hold and pygame.time.get_ticks() - self.__pressed_time > self.__pressed_delay:
                self.unpress() # pressed set to false if enough time has elapsed
            if self._hover_image and self._image == self._hover_image:
                self._image = self._default_image # temporarily set to default if you were hovering over the button
            self.__clicked = False # clicked is true only in the frame the button is clicked on

            if self._rect.collidepoint(mpos): # if the mouse is in the button rect
                if self.__hover == False:
                    hover_effect.play() # if you were previously not hovering, play the hover sound
                if self._hover_image:
                    self._image = self._hover_image # if there is a hover image, display it
                self.__hover = True
                if click:
                    if not self.__pressed: # if the button was previously not pressed, play the click sound
                        button_click.play()
                    self.__clicked = True
                    self.__pressed = True
                    self.__pressed_time = pygame.time.get_ticks()
            else:
                self.__hover = False
            
            if self.__pressed and self._pressed_image:
                self._image = self._pressed_image # if the button is pressed and there is a pressed image, display it
    
    def draw(self, screen): # draws the button
        if self._image: # if the button has an image, display it
            screen.blit(self._image, self._rect)
        else: # otherwise draw a coloured rect of the button
            pygame.draw.rect(screen, PALER_BACKGROUND, self._rect)
        if self.__border_colour:
            pygame.draw.rect(screen, self.__border_colour, self._rect, width=int(PIXEL_RATIO))

#======================Text Button Class======================#
# creates a button with text on it
# used all over the project, for example the login button
class TextButton(Button):
    def __init__(self, pos, size,  text, font, hold=True, pressed=False, disabled=False, text_colour=BUTTON_TEXT_COLOUR, pressed_text_colour=BUTTON_TEXT_PRESSED_COLOUR, disabled_text_colour=BUTTON_TEXT_DISABLED_COLOUR, background_colour=TEXT_BUTTON_BACKGROUND_COLOUR, hover_background_colour=TEXT_BUTTON_HOVER_COLOUR, pressed_delay=BUTTON_PRESSED_DELAY, border_colour=None):
        super().__init__(pos, size, hold, pressed, disabled, pressed_delay, border_colour)
        self.__set_images(text, font, text_colour, pressed_text_colour, disabled_text_colour, background_colour, hover_background_colour)
        self._image = self._default_image

    # creates the images for the text button
    def __set_images(self, text, font, text_colour, pressed_text_colour, disabled_text_colour, background_colour, hover_background_colour):
        text_x = self._rect.width//2
        if NEW_LINE in text:
            text_y = font.get_character_spacing() + PIXEL_RATIO # if there are multiple lines, start the text a little bit down to not touch the tops
        else:
            text_y = self._rect.height//2 - font.get_height()//2 # if there are not, start the text in the middle of the button

        default_font = font.new_colour_copy(text_colour)

        self._default_image = pygame.Surface(self._rect.size, pygame.SRCALPHA) # pygame.SCRALPHA allows for transparency
        if background_colour:
            self._default_image.fill(background_colour) # fill with the colour
        default_font.render(self._default_image, text, (text_x, text_y), alignment=CENTER) # render the text on top

        self._hover_image = pygame.Surface(self._rect.size, pygame.SRCALPHA)
        if hover_background_colour:
            self._hover_image.fill(hover_background_colour) # fill with the colour
        default_font.render(self._hover_image, text, (text_x, text_y), alignment=CENTER) # render the text on top

        self._pressed_image = pygame.Surface(self._rect.size, pygame.SRCALPHA)
        if hover_background_colour:
            self._pressed_image.fill(hover_background_colour)
        pressed_font = font.new_colour_copy(pressed_text_colour) # different colour font for when the button is pressed
        pressed_font.render(self._pressed_image, text, (text_x, text_y), alignment=CENTER) 

        self._disabled_image = pygame.Surface(self._rect.size, pygame.SRCALPHA)
        if background_colour:
            self._disabled_image.fill(background_colour)
        disabled_font = font.new_colour_copy(disabled_text_colour)
        disabled_font.render(self._disabled_image, text, (text_x, text_y), alignment=CENTER)

#======================Image Button Class======================#
# creates a button with an image on it
# used all over the program, for example the return buttons
class ImageButton(Button):
    def __init__(self, pos, size, image, hold=True, pressed=False, disabled=False, pressed_image=None, image_colour=BUTTON_ICON_COLOUR, pressed_image_colour=BUTTON_ICON_PRESSED_COLOUR, disabled_image_colour=BUTTON_DISABLED_COLOUR, background_colour=BUTTON_BACKGROUND_COLOUR, hover_background_colour=BUTTON_HOVER_COLOUR, pressed_delay=BUTTON_PRESSED_DELAY, text="", font=None, border_colour=None):
        super().__init__(pos, size, hold, pressed, disabled, pressed_delay, border_colour)
        self.__set_images(image, pressed_image, image_colour, pressed_image_colour, disabled_image_colour, background_colour, hover_background_colour)
        self._image = self._default_image

    # creates the images for the image button
    def __set_images(self, image, pressed_image, image_colour, pressed_image_colour, disabled_image_colour, background_colour, hover_background_colour):
        self._default_image = pygame.Surface(self._rect.size) # create an empty surface
        self._default_image.fill(background_colour) # fill it with the background colour
        self._default_image.blit(colour_swap(image, WHITE, image_colour),(0,0)) # blit the image to it

        self._hover_image = pygame.Surface(self._rect.size)
        self._hover_image.fill(hover_background_colour)
        self._hover_image.blit(colour_swap(image, WHITE, image_colour),(0,0)) # images are created in white

        if pressed_image:
            self._pressed_image = pressed_image # passing in a pressed image overwrites the custom pressed image
        else:
            self._pressed_image = pygame.Surface(self._rect.size)
            self._pressed_image.fill(hover_background_colour)
            self._pressed_image.blit(colour_swap(image, WHITE, pressed_image_colour),(0,0))

        self._disabled_image = pygame.Surface(self._rect.size)
        self._disabled_image.fill(background_colour)
        self._disabled_image.blit(colour_swap(image, WHITE, disabled_image_colour),(0,0))

#======================Font Class======================#
class Font():
    def __init__(self, font_image, character_list, colour, space_width, character_spacing=PIXEL_RATIO, alpha=255):
        self.__font_image = font_image
        self.__character_list = character_list
        self.__characters = {}
        current_width = 0
        character_count = 0
        self.__space_width = space_width
        self.__character_spacing = character_spacing
        self.__height = font_image.get_height()

        border_colour = (255,0,0) # not in settings file as it is a property of the font images
        text_colour = (255,255,255)

        # if the desired colour is not the colour of the border between letters, swap the text colour to the new colour
        # otherwise, set the colour of the borders to a different colour and then swap the text colour to the new colour
        if colour != border_colour:  
            font_image = colour_swap(font_image, text_colour, colour) 
        else:
            different_colour = (127,127,127)
            font_image = colour_swap(font_image, border_colour, different_colour) # can be any random colour, just not border_colour or text_colour
            border_colour = different_colour
            font_image = colour_swap(font_image, text_colour, colour)

        if alpha != 255:
            font_image.set_alpha(alpha) # make transparent

        for x in range(0, font_image.get_width(), int(PIXEL_RATIO)): # loop through the width of the font image, incrementing by a pixel each time
            colour = font_image.get_at((x, 0)) # get the colour of the current pixel
            if colour == border_colour: # if colour is the border colour
                character_image = clip(font_image, x - current_width, 0, current_width, font_image.get_height()) # clip the font image from the last border colour to the new one
                self.__characters[self.__character_list[character_count]] = character_image # create an entry in the character dictionary for the current letter and image
                character_count += 1
                current_width = 0
            else:
                current_width += PIXEL_RATIO # stores the current width of the character, width since last border colour

    def new_colour_copy(self, new_colour, alpha=255): # return a copy of the font with a different colour
        return Font(self.__font_image, self.__character_list, new_colour, self.__space_width, character_spacing=self.__character_spacing, alpha=alpha)
    
    def get_text_width(self, text): # given some text, returns the width of the text in this font
        width = [0] # stores width of each line
        line = 0
        width[0] += self.__characters[text[0]].get_width() # first character first so no extra spacing
        for character in text[1:]:
            if character == NEW_LINE:
                width.append(0) # if there is a new line, create a new entry in the widths list
                line += 1
            elif character != ' ':
                width[line] += self.__character_spacing # add the width of the spacing between characters
                width[line] += self.__characters[character].get_width() # add the width of the character
            else:
                width[line] += self.__space_width # if character is a space, add the width of a space
        return max(width) # return the highest value in the list of line widths
    
    def get_height(self): # return the height of the font
        return self.__height
    
    def get_character_spacing(self): # return the width of the spacing between characters
        return self.__character_spacing

    def render(self, screen, text, pos, alignment=LEFT, hide=False): # render a string of text to the screen in the font
        x_offset = [0]
        line = 0
        y_offset = 0
        for character in text:
            if hide:
                character = 'hidden' # 'hidden' is a character in character list
            if character == NEW_LINE:
                y_offset += self.__height + 2*PIXEL_RATIO # if there is a new line, start drawing the characters further down
                x_offset.append(0) # create a new entry in the offset list
                line += 1
            elif character != ' ':
                if alignment == LEFT: # only draw the characters if the alignment is to the left
                    screen.blit(self.__characters[character], (pos[X] + x_offset[line], pos[Y] + y_offset))
                x_offset[line] += self.__characters[character].get_width()
                x_offset[line] += self.__character_spacing # add the necessary widths to the x_offset
            else:
                x_offset[line] += self.__space_width

        widths = x_offset.copy() # x_offset list now represents the width of each line
        line = 0
        
        if alignment == RIGHT: # if the alignment is to the right
            x_offset = []
            for width in widths:
                x_offset.append(-width) # x_offset list starts as the negative width of each line
            y_offset = 0
            for character in text:
                if hide:
                    character = 'hidden'
                if character == NEW_LINE:
                    y_offset = self.__height + 2*PIXEL_RATIO
                    line += 1
                if character != ' ':
                    screen.blit(self.__characters[character], (pos[X] + x_offset[line], pos[Y]))
                    x_offset[line] += self.__characters[character].get_width()
                    x_offset[line] += self.__character_spacing
                else:
                    x_offset[line] += self.__space_width
        elif alignment == CENTER: # if alignment is to the center
            x_offset = []
            for width in widths:
                x_offset.append(0 - round_to_nearest(width//2, PIXEL_RATIO)) # x_offset list starts as the negative width/2 of each line (rounded to the nearest pixel)
            y_offset = 0
            for character in text:
                if hide:
                    character = 'hidden'
                if character == NEW_LINE:
                    y_offset = self.__height + 2*PIXEL_RATIO
                    line += 1
                elif character != ' ':
                    screen.blit(self.__characters[character], (pos[X] + x_offset[line], pos[Y] + y_offset))
                    x_offset[line] += self.__characters[character].get_width()
                    x_offset[line] += self.__character_spacing
                else:
                    x_offset[line] += self.__space_width

#======================Text Box Class======================#
# creates a text box that a message can be written into
# used for entering usernames and pins for logging in or creating an account
class TextBox():
    def __init__(self, pos, size, type_font, message_font, max_length, name="", allowed_strings = None, not_allowed_strings = None, allowed_characters=CHARACTER_LIST_U, background_colour=TEXT_BOX_BACKGROUND, border_width=int(PIXEL_RATIO), initial_text="", hide=False, typing=False):
        self.__rect = pygame.Rect(pos, size)
        self.__type_font = type_font
        self.__message_font = message_font
        self.__max_length = max_length
        self.__name = name
        self.__allowed_strings = allowed_strings # if allowed_strings are supplied, they are the only strings the text box accepts
        self.__not_allowed_strings = not_allowed_strings # if not allowed strings are supplied, they are not accepted by the text box
        self.__allowed_characters = allowed_characters
        self.__background_colour = background_colour
        self.__border_width = border_width
        self.__text = initial_text
        self.__hide = hide # boolean value that, when True, displays the entered text as dots
        self.__error_message = "" # used to tell the user when they have entered something invalid

        self.__typing = typing # whether or not the text box is selected

    def __check_typing(self, mpos, click):
        if click:
            if self.__rect.collidepoint(mpos): # if they have clicked on the text box, typing becomes true
                if not self.__typing:
                    button_click.play()
                self.__typing = True
                self.__error_message = "" # reset the error message if they begin to type
            else:
                self.__typing = False # if they have clicked anywhere else, typing becomes false
            
    def __check_allowed(self): # returns an error message and a border colour based on the text
        # if there is not enough text, border colour is red and it displays to the user how many more characters needed
        # if the text is in the not-allowed list, border colour is amber and it displays to the user that the text is already taken
        # if the text is not in the allowed list, border colour is amber and it displays to the user that the text is not recognised
        # if none of these have occurred, border colour is green and no error message is displayed
        if len(self.__text) != self.__max_length:
            characters_left = self.__max_length - len(self.__text)
            return RED, f"{characters_left} MORE CHARACTER" + ("S" if characters_left != 1 else "")
        elif self.__not_allowed_strings != None and self.__text in self.__not_allowed_strings:
            return AMBER, f"{self.__name} ALREADY TAKEN"
        elif self.__allowed_strings != None and self.__text not in self.__allowed_strings:
            return AMBER, f"{self.__name} NOT RECOGNISED"
        return GREEN, ""
    
    def get_valid(self): # returns whether or not the entered text is valid using the same rules as __check_allowed
        if len(self.__text) != self.__max_length:
            return False
        elif self.__not_allowed_strings != None and self.__text in self.__not_allowed_strings:
            return False
        elif self.__allowed_strings != None and self.__text not in self.__allowed_strings:
            return False
        return True
    
    def get_text(self): # returns the text
        return self.__text
    
    def display_message(self, error_message): # allows the program to display custom error messages
        self.__error_message = error_message
        
    def update(self, mpos, click, event_list): # takes keyboard input and converts it into text
        self.__check_typing(mpos, click)
        if self.__typing:
            for event in event_list:
                if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_BACKSPACE:
                            self.__text = self.__text[:-1] # if backspace pressed, remove a letter
                        else:
                            if len(self.__text) < self.__max_length: # if there is space and the character is allowed, convert the keyboard input into a character and add it to the text
                                character = event.unicode.upper() 
                                if character in self.__allowed_characters:
                                    self.__text += character

    def draw(self, screen): # draw the text box
        if self.__background_colour:
            pygame.draw.rect(screen, self.__background_colour, self.__rect)
        
        if self.__name:
            self.__message_font.render(screen, f"{self.__name}:", (self.__rect.left - PIXEL_RATIO, self.__rect.centery - self.__message_font.get_height()//2), alignment=RIGHT)

        self.__border_colour, message = self.__check_allowed()
        
        if self.__typing: # display the border and __check_allowed message if typing
            pygame.draw.rect(screen, self.__border_colour, self.__rect, width=self.__border_width)
            self.__message_font.render(screen, message, (self.__rect.centerx, self.__rect.bottom + self.__message_font.get_height()//2), alignment=CENTER)

        self.__message_font.render(screen, self.__error_message, (self.__rect.centerx, self.__rect.bottom + self.__message_font.get_height()//2), alignment=CENTER)        
        
        self.__type_font.render(screen, self.__text, (self.__rect.x + 4*PIXEL_RATIO, self.__rect.centery - self.__type_font.get_height()//2), hide=self.__hide)

#======================Character Display Class======================# 
# creates a display of a custom character specified by hex input
# the size of each pixel of the display can be specified
# the character can be changed and customised with functions
class CharacterDisplay():
    def __init__(self, pos, pixel_width, background_colour, hex_string, extra_border_colour=None):
        self.__height = 8
        self.__width = 8
        self.__hat_height = 3
        self.__background_colour = background_colour
        self.__extra_border_colour = extra_border_colour

        self.__parts = dict(zip([0,1,2,3,4,5], FRONT_PATTERNS)) # creates a dictionary of each part pattern as the value and the respective part as the key

        self.__grid = []
        for row in range(self.__height):
            current_row = []
            for column in range(self.__width):
                current_row.append(Pixel((pos[X]+(column*pixel_width*PIXEL_RATIO), pos[Y]+(row*pixel_width*PIXEL_RATIO)), background_colour=background_colour, width=pixel_width, height=pixel_width))
            self.__grid.append(current_row)
        
        self.__rect = pygame.Rect(pos, (self.__width*pixel_width*PIXEL_RATIO, self.__height*pixel_width*PIXEL_RATIO))
        self.__border_thickness = ceil(pixel_width / 2)
        self.__border_rect = pygame.Rect((pos[X] - self.__border_thickness*PIXEL_RATIO, pos[Y] - self.__border_thickness*PIXEL_RATIO), (self.__rect.width + 2*self.__border_thickness*PIXEL_RATIO, self.__rect.height + 2*self.__border_thickness*PIXEL_RATIO))

        if hex_string:
            self.hex_to_grid(hex_string) # the initial state of the grid is defined by the hex string passed in

    def select_hex_to_grid(self, hex_string): # takes a hex string and converts each respective part of the custom character to each respective colour defined by the hex
        hex_list = split(hex_string, COLOUR_DEPTH) # split the hex into individual colours
        for part_index in self.__parts.keys():
            self.update_pattern(part_index, get_key(hex_list[part_index], BITMAP_DICTIONARY)) # update each part to its respective colour
    
    def update_pattern(self, part, colour): # changes the colour of a part of the character
        # goes through each pair of coordinates in the part and changes the colour of the pixel at each location
        for row,column in self.__parts[part]:
            self.__grid[row][column].set_background_colour(colour)  # uses background colour so that a hat doesn't overwrite the character's forehead

    def hat_hex_to_grid(self, hex_string): # takes a hex string and converts the hat into the state the hex describes
        hex_array = split(split(hex_string, COLOUR_DEPTH), self.__width) # split hex string into individual colours in rows in the same format as the grid
        for row in range(len(hex_array)):
            for column in range(self.__width):
                self.__grid[row][column].set_colour(get_key(hex_array[row][column], BITMAP_DICTIONARY)) # converts each pixel into each colour

    def hex_to_grid(self, hex_string): # takes a hex string and converts the character grid into the state it describes
        self.select_hex_to_grid(hex_string[:-COLOUR_DEPTH*self.__hat_height*self.__width]) # the first part of the hex string is the 6 colours of the select grids and the pattern colours 
        self.hat_hex_to_grid(hex_string[-COLOUR_DEPTH*self.__hat_height*self.__width:])    # the latter part is the 24 colours of each pixel in the hat

    def get_rect(self): # return the rect of the grid
        return self.__rect

    def draw(self, screen): # draws the character to the screen
        if self.__background_colour:
            pygame.draw.rect(screen, self.__background_colour, self.__border_rect)
        if self.__extra_border_colour:
            pygame.draw.rect(screen, self.__extra_border_colour, self.__border_rect, width=int(ceil(self.__border_thickness/2)*PIXEL_RATIO))
        for row in self.__grid:
            for pixel in row:
                pixel.draw(screen)

#======================Pixel Class======================# 
# a coloured pixel that has a rect and can be drawn
# used in the ColourGrid, CharacterDisplay, and DrawingGrid classes
class Pixel():
    def __init__(self, pos, background_colour=PALER_BACKGROUND, colour=None, width=8, height=8):
        self.__background_colour = background_colour # background colour so that it can hold what should be behind it
        self.__colour = colour
        self.__pos = pos
        self.__rect = pygame.Rect(pos, (width*PIXEL_RATIO, height*PIXEL_RATIO)) # the rect, used to check if the a coordinate collides with the pixel
        self.__locked = False # pixels can be locked in colour grids

    def get_rect(self): # return the rect of the pixel
        return self.__rect
    
    def get_pos(self): # return the position of the pixel
        return self.__pos
    
    def get_colour(self): # return the colour of the pixel
        return self.__colour
    
    def get_locked(self): # return the locked status of the pixel
        return self.__locked
    
    def set_locked(self, bool): # change the locked status of the pixel
        self.__locked = bool

    def set_colour(self, colour): # change the colour of the pixel
        self.__colour = colour

    def set_background_colour(self, colour): # change the background colour of the pixel
        self.__background_colour = colour
    
    def draw(self, screen): # draws the pixel to the screen
        # if the pixel is locked, draw a padlock
        # otherwise if the pixel has a colour, draw it
        # otherwise draw the background colour
        if self.__locked:
            pygame.draw.rect(screen, LOCKED_COLOUR, self.__rect)
            screen.blit(padlock_image, self.__rect.topleft)
        elif self.__colour:
            pygame.draw.rect(screen, self.__colour, self.__rect) 
        elif self.__background_colour:
            pygame.draw.rect(screen, self.__background_colour, self.__rect)

#======================Slider Class======================#
# creates a slider that you can drag up and down to represent a value
# used for the volume setting
class Slider():
    def __init__(self, pos, size, min, max, value, bar_colour=PALER_BACKGROUND, slider_colour=WHITE):
        self.__min = min # the minimum value of the slider
        self.__max = max # the maximum value of the slider
        self.__bar_colour = bar_colour # the colour of the bar
        self.__slider_colour = slider_colour # the colour of the slider
        self.__active = False # whether or not the slider is being used

        self.__bar_rect = pygame.Rect(pos, size) # the rect of the bar
        self.__slider_rect = pygame.Rect((pos[X], pos[Y] - 2*PIXEL_RATIO), (4*PIXEL_RATIO, size[Y] + 4*PIXEL_RATIO)) # the rect of the slider
        self.__slider_rect.centerx = self.__x_from_value(value) # moves the slider to where the initial value would be

    def __x_from_value(self, value): # takes a value and returns the x coordinate for the slider
        return ((value - self.__min) / (self.__max - self.__min)) * self.__bar_rect.width + self.__bar_rect.left

    def __value_from_x(self, x): # takes an x coordinate and returns the value it represents
        return ((x - self.__bar_rect.left) / self.__bar_rect.width) * (self.__max - self.__min) + self.__min
    
    def get_value(self): # returns the value of the slider
        return round(self.__value_from_x(self.__slider_rect.centerx), 2)

    def update(self, click, unclick, mpos): # update the slider from inputs of clicking and the mouse position
        if not self.__active and click and self.__slider_rect.collidepoint(mpos): # if the slider is clicked on
            button_click.play()
            self.__active = True # become active
                            
        if self.__active:
            if mpos[X] <= self.__bar_rect.left:
                self.__slider_rect.centerx = self.__bar_rect.left # stop the slider at the left boundary
            elif mpos[X] >= self.__bar_rect.right:
                self.__slider_rect.centerx = self.__bar_rect.right # stop the slider at the right boundary
            else:
                self.__slider_rect.centerx = mpos[X] # if within range, the x of the slider becomes the x of the mouse position

            if unclick: # if active and the mouse button is unclicked, no longer active
                self.__active = False
                return True  # true returned if slider has been used so the program can update the volume
        return False

    def draw(self, screen): # draw the slider
        pygame.draw.rect(screen, self.__bar_colour, self.__bar_rect)
        pygame.draw.rect(screen, self.__slider_colour, self.__slider_rect)
