from math import trunc, ceil
from random import randint, choice

import pygame

from constants import *
from utility_classes import Queue, Font
from game_classes import (Cell, Player, Item, Score, DefaultEnemy, FastEnemy, 
                          FlyingEnemy, CrowEnemy, ToughEnemy, SpiritEnemy)
from images import (white_flowers1_image, white_flowers2_image, grass1_image, grass2_image, grass3_image, 
                    crate_image, small_font_image, huge_font_image, item_images, fences_image)
from sounds import player_hit_sound, player_death_sound, crate_thud, item_sounds

#======================Game Class======================#
class Game():
    def __init__(self, pos, character_hex, initial_obstacles, players=1, player2_hex=None):
        self.__width = GAME_WIDTH
        self.__height = GAME_HEIGHT
        self.__rect = pygame.Rect((0,0), (self.__width*EIGHT_PIXELS, self.__height*EIGHT_PIXELS))
        self.__grid = [[Cell((i*EIGHT_PIXELS, j*EIGHT_PIXELS)) for i in range(self.__width)] for j in range(self.__height)]
        self.__players = players
        if players == 1:
            self.__player = Player(character_hex, self.__rect)
        elif players == 2:
            self.__player1 = Player(character_hex, self.__rect, 1)
            self.__player2 = Player(player2_hex, self.__rect, 2)
            self.__player1_respawn = -1 # the frame on which player 1 will respawn
            self.__player2_respawn = -1
        self.__pos = pos
        
        self.__small_font = Font(small_font_image, CHARACTER_LIST, WHITE, 2*PIXEL_RATIO)
        self.__countdown_font = Font(huge_font_image, CHARACTER_LIST_U, WHITE, 4*PIXEL_RATIO, alpha=230)
        
        # for each initial obstacle coordinate, add collision to the cell it represents
        for row, column in initial_obstacles:
            self.__grid[row][column].set_collision(True)

        self.__collidable_rects = self.__collidable_rects_list()

        # place random background tiles
        self.__place_random(grass1_image, randint(1,4), 2)
        self.__place_random(grass2_image, randint(1,4), 1)
        self.__place_random(grass3_image, randint(1,4), 2)
        self.__place_random(white_flowers1_image, randint(1,3), 3)
        self.__place_random(white_flowers2_image, randint(1,2), 3)

        self.__items = []
        self.__enemies = []
        self.__enemies_to_spawn = [] # list of enemies that couldn't yet be spawned due to collisions
        self.__scores = []
        
        self.__enemy_queue = Queue()
        self.__enemy_rects = self.__enemy_rects_list()

        self.__countdown = 3*FPS

        self.__time_score = 0 # score gained over time
        self.__enemy_score = 0 # score gained by killing enemies
        
        self.__enemies_killed = 0 # number of enemies killed
        self.__items_used = 0 # number of items used
        
        self.__item_countdown = 0 # countdown between two items spawning
        self.__crate_countdown = 0 # delay after wave before crate
        self.__enemy_delay = 0 # number of frames before the next enemies spawn
        self.__enemy_timer = 0 # frame counter set to 0 everytime enemies spawn
        self.__timer = 0 # overall frame counter that increments every frame
        self.__wave_index = -1  # index is the wave number, used to set the difficulty of the wave

        self.__shake = False # if the screen should be shaking
        self.__bomb_time = 0 # the last time (frame number) a bomb was used
        self.__time_freeze = False # if time should be frozen
        self.__time_freeze_time = 0 # the last time a time freeze was used
        self.__freeze_surface = pygame.Surface((self.__rect.width, self.__rect.height), pygame.SRCALPHA)

    def __place_random(self, image, number, min_distance, collision=False, center_spawn=True): # place a random image on the grid
        available = [] # list of available coordinates
        for row in range(min_distance, self.__height - min_distance): # min_distance is distance from edges
            for column in range(min_distance, self.__width - min_distance):
                if self.__check_valid_placement(row, column, collision, center_spawn):
                    available.append((row, column)) # append all valid coordinates to the list
        for _ in range(number):
            if len(available) > 0:
                row, column = choice(available) # random coordinate from the list
                self.__grid[row][column].set_image(image)
                if collision:
                    self.__grid[row][column].set_collision(True)
                    self.__grid[row][column].set_shade(True)
                available.remove((row, column))
        if collision:
            self.__collidable_rects = self.__collidable_rects_list() # update the collision list

    def __check_valid_placement(self, row, column, collision, center_spawn):
        if self.__grid[row][column].get_collision():
            return False # false if already a collidable object in the position
        
        if not center_spawn and (row in [trunc((GAME_WIDTH-1)/2), GAME_WIDTH//2] and column in [trunc((GAME_HEIGHT-1)/2), GAME_HEIGHT//2]):
            return False # false if it shouldn't spawn in the center and it is in the center
                
        if self.__players == 1:
            if collision and self.__grid[row][column].get_rect().colliderect(self.__player.get_rect()):
                return False # false if colliding with the player
        elif self.__players == 2:
            if collision and (self.__grid[row][column].get_rect().colliderect(self.__player1.get_rect()) 
                              or self.__grid[row][column].get_rect().colliderect(self.__player2.get_rect())):
                return False # false if colliding with either player
            
        return True # otherwise, placement is valid, return True
    
    def __collidable_rects_list(self): # return a list of rects for collidable cells in the grid
        # loops through every coordinate in the grid and checks for their collision
        # recursively combines adjacent rects into singular wider / taller rects
        collidable_rects = [] # list of rects
        row = 0
        column = 0
        checked = []
        for row in range(self.__height):
            for column in range(self.__width):
                if (row, column) not in checked and self.__grid[row][column].get_collision():
                    rect = self.__grid[row][column].get_rect().copy() # base rect is the rect of the cell

                    # check for adjacent collisions horizontally, possible increasing the width of the rect
                    checked_columns = []
                    rect.width, checked_columns = self.__check_next_hor(row, column, checked_columns, checked, EIGHT_PIXELS)
                    for checked_column in checked_columns:
                        checked.append((row, checked_column))

                    if len(checked_columns) == 1: # if nothing was found in the horizontal
                        # check for adjacent collisions vertically, possibly increasing the height of the rect
                        checked_rows = []
                        rect.height, checked_rows = self.__check_next_vert(row, column, checked_rows, checked, EIGHT_PIXELS)
                        for checked_row in checked_rows:
                            checked.append((checked_row, column))

                    collidable_rects.append(rect)
        return collidable_rects

    def __check_next_hor(self, row, column, checked_columns, checked, width): # recursive function to check for adjacent horizontal collidables
        # checks the next coordinate horizontally in the grid
        # if it exists, isn't checked, and has a collision, the function calls itself to look again
        # once an invalid coordinate is found, the function unwinds and add 8 pixels to the width per call 
        try:
            checked_columns.append(column)
            if (row, column+1) not in checked:
                if self.__grid[row][column + 1].get_collision():
                    width, checked_columns = self.__check_next_hor(row, column + 1, checked_columns, checked, width)
                    return width + EIGHT_PIXELS, checked_columns
        except IndexError:
            pass
        return width, checked_columns # base case
    
    def __check_next_vert(self, row, column, checked_rows, checked, height): # recursive function to check for adjacent vertical collidables
        # checks the next coordinate vertically in the grid
        # if it exists, isn't checked, and has a collision, the function calls itself to look again
        # once an invalid coordinate is found, the function unwinds and adds 8 pixels to the height per call
        try:
            checked_rows.append(row)
            if (row + 1, column) not in checked:
                if self.__grid[row + 1][column].get_collision():
                    height, checked_rows = self.__check_next_vert(row + 1, column, checked_rows, checked, height)
                    return height + EIGHT_PIXELS, checked_rows # when unwinding, each iteration adds 8 pixels
        except IndexError:
            pass
        return height, checked_rows # base case

    def __enemy_rects_list(self): # returns a list of rects of all ground enemies
        rect_list = []
        for enemy in self.__enemies:
            if not enemy.get_flying():
                rect_list.append(enemy.get_rect()) 
        return rect_list

    def __enemy_group(self, enemy_class, amount): # returns a dictionary with an amount of enemies and a difficulty of an enemy class
        enemies = []
        spawn_side = randint(0,3)
        groups = amount // 4   # the number of groups of 4  
        remaining = amount % 4 # the number of remaining enemies after groups of 4 are taken out

        # spawn the groups of 4 in lines
        for _ in range(groups): 
            if spawn_side == UP:
                enemies.extend(enemy_class((self.__rect.centerx - (3/2)*(EIGHT_PIXELS) + side_position*EIGHT_PIXELS, self.__rect.top + EIGHT_PIXELS/2), direction=(spawn_side+2)%4) for side_position in range(0,4)) 
            elif spawn_side == LEFT:
                enemies.extend(enemy_class((self.__rect.left + EIGHT_PIXELS/2, self.__rect.centery - (3/2)*(EIGHT_PIXELS) + side_position*EIGHT_PIXELS), direction=(spawn_side+2)%4) for side_position in range(0,4))
            elif spawn_side == DOWN:
                enemies.extend(enemy_class((self.__rect.centerx - (3/2)*(EIGHT_PIXELS) + side_position*EIGHT_PIXELS, self.__rect.bottom - EIGHT_PIXELS/2), direction=(spawn_side+2)%4) for side_position in range(0,4))
            elif spawn_side == RIGHT:
                enemies.extend(enemy_class(((self.__rect.right - EIGHT_PIXELS/2, self.__rect.centery - (3/2)*(EIGHT_PIXELS) + side_position*EIGHT_PIXELS)), direction=(spawn_side+2)%4) for side_position in range(0,4))
        
        side_positions = [2, 1, 3, 0]
        # spawn the remaining enemies, prioritising spawning them in the middle
        if spawn_side == UP:
            enemies.extend(enemy_class((self.__rect.centerx - (3/2)*(EIGHT_PIXELS) + side_positions[i]*EIGHT_PIXELS, self.__rect.top + EIGHT_PIXELS/2), direction=(spawn_side+2)%4) for i in range(remaining)) 
        elif spawn_side == LEFT:
            enemies.extend(enemy_class((self.__rect.left + EIGHT_PIXELS/2, self.__rect.centery - (3/2)*(EIGHT_PIXELS) + side_positions[i]*EIGHT_PIXELS), direction=(spawn_side+2)%4) for i in range(remaining))
        elif spawn_side == DOWN:
            enemies.extend(enemy_class((self.__rect.centerx - (3/2)*(EIGHT_PIXELS) + side_positions[i]*EIGHT_PIXELS, self.__rect.bottom - EIGHT_PIXELS/2), direction=(spawn_side+2)%4) for i in range(remaining))
        elif spawn_side == RIGHT:
            enemies.extend(enemy_class(((self.__rect.right - EIGHT_PIXELS/2, self.__rect.centery - (3/2)*(EIGHT_PIXELS) + side_positions[i]*EIGHT_PIXELS)), direction=(spawn_side+2)%4) for i in range(remaining))
        
        difficulty = 0
        for enemy in enemies:
            difficulty += enemy.get_score() # 'difficulty' rating is the sum of the scores of all enemies

        return {'enemies':enemies, 'difficulty':difficulty}
    
    def __fast_enemy(self, amount): # returns a dictionary with an amount of fast enemies and a difficulty
        enemies = []
        for _ in range(amount):
            spawn_side = randint(0,3) # random side for spawing
            side_position = randint(0,3) # random position on that side
            if spawn_side == UP:
                enemies.append(FastEnemy((self.__rect.centerx - (3/2)*(EIGHT_PIXELS) + side_position*EIGHT_PIXELS, self.__rect.top + EIGHT_PIXELS/2), direction=(spawn_side+2)%4))
            elif spawn_side == LEFT:
                enemies.append(FastEnemy((self.__rect.left + EIGHT_PIXELS/2, self.__rect.centery - (3/2)*(EIGHT_PIXELS) + side_position*EIGHT_PIXELS), direction=(spawn_side+2)%4))
            elif spawn_side == DOWN:
                enemies.append(FastEnemy((self.__rect.centerx - (3/2)*(EIGHT_PIXELS) + side_position*EIGHT_PIXELS, self.__rect.bottom - EIGHT_PIXELS/2), direction=(spawn_side+2)%4))
            elif spawn_side == RIGHT:
                enemies.append(FastEnemy((self.__rect.right - EIGHT_PIXELS/2, self.__rect.centery - (3/2)*(EIGHT_PIXELS) + side_position*EIGHT_PIXELS), direction=(spawn_side+2)%4))
        
        difficulty = 0
        for enemy in enemies:
            difficulty += enemy.get_score()

        return {'enemies':enemies, 'difficulty':difficulty}

    def __flying_enemy(self, amount): # returns a dictionary with an amount of flying enemies and a difficulty
        enemies = []
        for _ in range(amount):
            side = randint(0,3)
            position = randint(1, GAME_WIDTH-2) # random position along an edge
            if side == RIGHT:
                enemies.append(FlyingEnemy((self.__rect.right + EIGHT_PIXELS//2, position*EIGHT_PIXELS + EIGHT_PIXELS//2), direction=(side+2)%4))
            elif side == LEFT:
                enemies.append(FlyingEnemy((self.__rect.left - EIGHT_PIXELS//2, position*EIGHT_PIXELS + EIGHT_PIXELS//2), direction=(side+2)%4))
            elif side == DOWN:
                enemies.append(FlyingEnemy((position*EIGHT_PIXELS + EIGHT_PIXELS//2, self.__rect.bottom + EIGHT_PIXELS//2), direction=(side+2)%4))
            elif side == UP:
                enemies.append(FlyingEnemy((position*EIGHT_PIXELS + EIGHT_PIXELS//2, self.__rect.top - EIGHT_PIXELS//2), direction=(side+2)%4))

        difficulty = 0
        for enemy in enemies:
            difficulty += enemy.get_score()

        return {'enemies':enemies, 'difficulty':difficulty}

    def __crow_enemy(self): # returns a dictionary with an amount of crow enemies and a difficulty
        enemies = []
        side = randint(0,3)
        position = randint(1, GAME_WIDTH-2) # random position along an edge
        if side == RIGHT:
            enemies.append(CrowEnemy((self.__rect.right + EIGHT_PIXELS//2, position*EIGHT_PIXELS + EIGHT_PIXELS//2), (side+2)%4, self.__rect))
        elif side == LEFT:
            enemies.append(CrowEnemy((self.__rect.left - EIGHT_PIXELS//2, position*EIGHT_PIXELS + EIGHT_PIXELS//2), (side+2)%4, self.__rect))
        elif side == DOWN:
            enemies.append(CrowEnemy((position*EIGHT_PIXELS + EIGHT_PIXELS//2, self.__rect.bottom + EIGHT_PIXELS//2), (side+2)%4, self.__rect))
        elif side == UP:
            enemies.append(CrowEnemy((position*EIGHT_PIXELS + EIGHT_PIXELS//2, self.__rect.top - EIGHT_PIXELS//2), (side+2)%4, self.__rect))

        difficulty = 0
        for enemy in enemies:
            difficulty += enemy.get_score()

        return {'enemies':enemies, 'difficulty':difficulty}
    
    def __spirit_enemy(self, amount): # returns a dictionary with an amount of spirit enemies and a difficulty
        enemies = []
        for _ in range(amount):
            side = randint(0,3)
            position = randint(1, GAME_WIDTH-2) # random position along an edge
            if side == RIGHT:
                enemies.append(SpiritEnemy((self.__rect.right + EIGHT_PIXELS//2, position*EIGHT_PIXELS + EIGHT_PIXELS//2), direction=(side+2)%4))
            elif side == LEFT:
                enemies.append(SpiritEnemy((self.__rect.left - EIGHT_PIXELS//2, position*EIGHT_PIXELS + EIGHT_PIXELS//2), direction=(side+2)%4))
            elif side == DOWN:
                enemies.append(SpiritEnemy((position*EIGHT_PIXELS + EIGHT_PIXELS//2, self.__rect.bottom + EIGHT_PIXELS//2), direction=(side+2)%4))
            elif side == UP:
                enemies.append(SpiritEnemy((position*EIGHT_PIXELS + EIGHT_PIXELS//2, self.__rect.top - EIGHT_PIXELS//2), direction=(side+2)%4))
        
        difficulty = 0
        for enemy in enemies:
            difficulty += enemy.get_score() # sum of scores is used as a measurment of difficulty

        return {'enemies':enemies, 'difficulty':difficulty}

    def __generate_enemy_waves_1p(self): # enqueues dictionaries of enemies to the enemy queue
        # total difficulty specifies the total sum of enemy scores for the enemy waves group
        total_difficulty = 500 + 400*self.__wave_index - (self.__wave_index**3) # gradually increases for each wave group
        if total_difficulty > 3000: # capped at 3000
            total_difficulty = 3000 
        difficulty = 0

        # while the sum of enemy scores is less than the desired sum, randomly select the enemy type to create a wave of
        # create a wave of that enemy, randomly generating the amount of them to spawn
        # enqueue that wave and add the sum of scores to the overall sum
        # the range of enemies that can spawn and the number of enemies that can spawn at once for each type change over time
        while difficulty < total_difficulty:
            match randint(0,(self.__wave_index + 1) if self.__wave_index < 5 else 5): # randomly selects the enemy type to create a wave of
                case 0: # default enemies can spawn from wave 0
                    wave = self.__enemy_group(DefaultEnemy, randint(2, 6) if self.__wave_index < 3 else (randint(4, 10) if self.__wave_index < 6 else randint(2,6)))
                case 1: # fast enemies can spawn from wave 0
                    wave = self.__fast_enemy(1 if self.__wave_index < 3 else (randint(1, 2) if self.__wave_index < 6 else randint(2,3)))
                case 2: # flying enemies can spawn from wave 1
                    wave = self.__flying_enemy(1 if self.__wave_index < 2 else (randint(1, 2) if self.__wave_index < 7 else randint(2,4)))
                case 3: # crow enemies can spawn from wave 2
                    wave = self.__crow_enemy() # always 1 crow enemy
                case 4: # tough enemies can spawn from wave 3
                    wave = self.__enemy_group(ToughEnemy, randint(4,6) if self.__wave_index < 4 else (randint(4, 10) if self.__wave_index < 8 else randint(6,12)))
                case 5: # spirit enemies can spawn from wave 4
                    wave = self.__spirit_enemy(1 if self.__wave_index < 5 else (randint(1, 3) if self.__wave_index < 8 else randint(2,4)))
            self.__enemy_queue.enqueue(wave)
            difficulty += wave['difficulty']

    def __generate_enemy_waves_2p(self): # very similar to its 1 player counterpart but tailored for two player
        total_difficulty = 800 + 600*self.__wave_index - (self.__wave_index**3) # higher score sum for 2p
        if total_difficulty > 5000: # higher limit
            total_difficulty = 5000 
        difficulty = 0

        # the number of enemies that can spawn in each wave is increased for two player
        while difficulty < total_difficulty:
            match randint(0, (self.__wave_index + 1) if self.__wave_index < 5 else 5):
                case 0: # spawns from wave 0
                    wave = self.__enemy_group(DefaultEnemy, randint(2, 6) if self.__wave_index < 3 else (randint(4, 12) if self.__wave_index < 6 else randint(6,14)))
                case 1: # spawns from wave 0
                    wave = self.__fast_enemy(1 if self.__wave_index < 2 else (randint(2, 3) if self.__wave_index < 6 else randint(2,4)))
                case 2: # spawns from wave 1
                    wave = self.__flying_enemy(1 if self.__wave_index < 2 else (randint(2, 3) if self.__wave_index < 7 else randint(3,5)))
                case 3: # spawns from wave 2
                    wave = self.__crow_enemy()
                case 4: # spawns from wave 3
                    wave = self.__enemy_group(ToughEnemy, randint(4,8) if self.__wave_index < 4 else (randint(6, 12) if self.__wave_index < 8 else randint(8,14)))
                case 5: # spawns from wave 4
                    wave = self.__spirit_enemy(1 if self.__wave_index < 5 else (randint(2, 3) if self.__wave_index < 8 else randint(3,5)))
            self.__enemy_queue.enqueue(wave)
            difficulty += wave['difficulty']

    def __first_waves(self): # allows the very first wave to be controlled
        self.__enemy_queue.enqueue(self.__enemy_group(DefaultEnemy, randint(3,6))) # spawn between 3 and 6 default enemies
        self.__enemy_queue.enqueue(self.__enemy_group(DefaultEnemy, randint(4,8))) # spawn between 4 and 8 more

    def __use_item(self, type, player=0): # use an item
        match player: # which player used the item
            case 0:
                player_class = self.__player
            case 1:
                player_class = self.__player1
            case 2:
                player_class = self.__player2

        # check the item type and run the approprite method
        if type == BOMB:
            self.__bomb(player_class)
        elif type == SHOES:
            player_class.add_shoes()
        elif type == SHOTGUN:
            player_class.add_shotgun()
        elif type == RAPID_FIRE:
            player_class.add_rapid_fire()
        elif type == TIME_FREEZE:
            self.__freeze_time()
        elif type == BACKWARDS_SHOT:
            player_class.add_backwards_shot()
        elif type == HEART:
            player_class.increase_health(1)

        if item_sounds[type]: # if there is a sound for the item
            item_sounds[type].play()

        self.__items_used += 1

    def __bomb(self, player_class): # use the bomb item
        to_kill = [] # the enemies to be killed
        # calculate the distance of each enemy and add them to the list if they are within the bomb's range
        for enemy in self.__enemies:
            distance = ((enemy.get_rect().centerx - player_class.get_rect().centerx)**2 + (enemy.get_rect().centery - player_class.get_rect().centery)**2)**0.5
            if distance < BOMB_RANGE:
                to_kill.append(enemy)
        # remove the enemies in the list from the main enemy list
        for enemy in to_kill:
            self.__enemies.remove(enemy)
            self.__enemies_killed += 1
        self.__bomb_time = self.__timer
        self.__shake = True

    def __freeze_time(self): # use the freeze time item
        self.__time_freeze = True
        self.__time_freeze_time = self.__timer

    def get_player_item(self): # return the player's item's type
        if self.__player.get_item():
            return self.__player.get_item().get_type()
        return None
    
    def get_player_lives(self): # return the player's lives
        if self.__players == 1:
            return self.__player.get_lives()
        elif self.__players == 2:
            return self.__player1.get_lives(), self.__player2.get_lives()
    
    def get_score(self): # return the total score
        return trunc(self.__time_score + self.__enemy_score)
    
    def get_time_score(self): # return the score from time
        return self.__time_score
    
    def get_enemy_score(self): # return the score from killing enemies
        return self.__enemy_score
    
    def get_enemies_killed(self): # return the number of enemies killed
        return self.__enemies_killed
    
    def get_bullets_shot(self): # return the number of bullets shot
        if self.__players == 1:
            return self.__player.get_bullets_shot()
        elif self.__players == 2:
            return self.__player1.get_bullets_shot() + self.__player2.get_bullets_shot()
    
    def get_items_used(self): # return the number of items used
        return self.__items_used
    
    def __check_enemy_spawn(self): # add the enemies that won't collide with another enemy to the main enemy list
        for enemy in self.__enemies_to_spawn: 
            if enemy.get_rect().collidelist(self.__enemy_rects) == -1 or enemy.get_flying(): # checking for collision
                self.__enemies.append(enemy)
                self.__enemy_rects.append(enemy.get_rect()) # add the enemy's rect to the enemy rects list
                self.__enemies_to_spawn.remove(enemy)
    
    def __check_player_hit(self): # check if a player has been hit
        # checking for hit is done with distance not rects to be more forgiving to the player
        # a hit is counted if an enemy's centre is within 7 pixels of the player's centre
        # 7 pixels is 1 less than the width of a player to add some leeway and 'close calls'
        if self.__players == 1:
            for enemy in self.__enemies:
                distance = ((enemy.get_rect().centerx - self.__player.get_rect().centerx)**2 + 
                            (enemy.get_rect().centery - self.__player.get_rect().centery)**2)**0.5
                if distance < 7*PIXEL_RATIO: 
                    if not self.__player.get_immunity(): # first checking if the player is immune
                        self.__player.hit(1) # take one life off the player and return them to the centre
                        if self.__player.get_lives() == 0:
                            player_death_sound.play()
                            pygame.time.delay(2000) # pause for 2 seconds if the player is dead
                        else:
                            player_hit_sound.play()
                            pygame.time.delay(1200) # pause for 1.2 seconds if the player is not yet dead
                        self.__enemies = [] # reset the enemy list
                        self.__player.empty_bullets() # reset the player's bullets
                        self.__items = [] # reset the items
                    break # stop looking at enemies to prevent errors
        elif self.__players == 2:
            for enemy in self.__enemies:
                distance1 = ((enemy.get_rect().centerx - self.__player1.get_rect().centerx)**2 + 
                             (enemy.get_rect().centery - self.__player1.get_rect().centery)**2)**0.5 # distance from first player
                distance2 = ((enemy.get_rect().centerx - self.__player2.get_rect().centerx)**2 + 
                             (enemy.get_rect().centery - self.__player2.get_rect().centery)**2)**0.5 # distance from second player
                if distance1 < 7*PIXEL_RATIO:
                    if not self.__player1.get_immunity() and self.__player1.get_lives() > 0:
                        self.__player1.hit(1)
                        self.__player1.add_immunity(7*FPS)  # 7 to account for 3 seconds of respawning
                        self.__player1_respawn = self.__timer + 3*FPS # not spawned for 3 seconds
                        self.__player1.set_spawned(False)
                        self.__enemies.remove(enemy)
                        break
                if distance2 < 7*PIXEL_RATIO:
                    if not self.__player2.get_immunity() and self.__player2.get_lives() > 0:
                        self.__player2.hit(1)
                        self.__player2.add_immunity(7*FPS) # 7 to account for 3 seconds of respawning
                        self.__player2_respawn = self.__timer + 3*FPS # not spawned for 3 seconds
                        self.__player2.set_spawned(False)
                        self.__enemies.remove(enemy)
                        break
    
    def __update_players(self): # update the player(s)
        if self.__players == 1:
            self.__player.update(self.__collidable_rects) # update player 1
        elif self.__players == 2:
            rect1, rect2 = None, None
            if self.__player1.get_lives() > 0 and self.__player1.get_spawned():
                rect1 = self.__player1.get_rect()
            if self.__player2.get_lives() > 0 and self.__player2.get_spawned():
                rect2 = self.__player2.get_rect()  
            self.__player1.update(self.__collidable_rects, other_player_rect = rect2) # update player 1 with player 2's rect if they're spawned
            self.__player2.update(self.__collidable_rects, other_player_rect = rect1) # update player 2 with player 1's rect if they're spawned

    def __update_enemies(self): # update the enemies
        for enemy in self.__enemies:
            # check if the enemy has been hit by a bullet
            if self.__players == 1:
                for bullet in self.__player.get_bullets():
                    if enemy.get_rect().colliderect(bullet.get_rect()):
                        enemy.hit(bullet.get_damage())
                        self.__player.remove_bullet(bullet)
            elif self.__players == 2:
                for bullet in self.__player1.get_bullets():
                    if enemy.get_rect().colliderect(bullet.get_rect()):
                        enemy.hit(bullet.get_damage()) # damage the enemy with the bullet's damage
                        self.__player1.remove_bullet(bullet)
                for bullet in self.__player2.get_bullets():
                    if enemy.get_rect().colliderect(bullet.get_rect()):
                        enemy.hit(bullet.get_damage())
                        self.__player2.remove_bullet(bullet)
                        
            # run the enemy's update function if time isn't frozen
            if not self.__time_freeze: 
                if self.__players == 1:
                    if not enemy.get_flying():
                        enemy.update(self.__player.get_pos(), self.__rect, self.__collidable_rects, self.__enemy_rects.copy())
                    else:
                        enemy.update(self.__player.get_pos())
                elif self.__players == 2:
                    # enemies only travel towards alive and non-immune players
                    player1_pos, player2_pos = None, None 
                    if self.__player1.get_lives() > 0 and not self.__player1.get_immunity():
                        player1_pos = self.__player1.get_pos()
                    if self.__player2.get_lives() > 0 and not self.__player2.get_immunity():
                        player2_pos = self.__player2.get_pos()

                    if not enemy.get_flying():
                        enemy.update(player1_pos, self.__rect, self.__collidable_rects, self.__enemy_rects.copy(), player2_pos=player2_pos)
                    else:
                        enemy.update(player1_pos, player2_pos=player2_pos)

            if enemy.get_health() == -5: # crow enemy is set to -5 if it has flown off of screen
                self.__enemies.remove(enemy) # no score added
            elif enemy.get_health() <= 0:
                if self.__item_countdown == 0 and randint(1,ITEM_CHANCE_1P if self.__players == 1 else ITEM_CHANCE_2P) == 1: # random chance for an item to spawn
                    if (self.__players == 1 and self.__player.get_lives() < 4) or (self.__players == 2 and (self.__player1.get_lives() < 4 or self.__player2.get_lives() < 4)):
                        spawn_lives = True # only spawns lives if a player has less than 4 lives
                    else:
                        spawn_lives = False
                    self.__items.append(Item(enemy.get_rect().center, randint(0, len(item_images)-1 - (0 if spawn_lives else 1))))
                    self.__item_countdown = ITEM_COUNTDOWN # items can't spawn within 0.5 seconds of eachother
                self.__enemies.remove(enemy)
                self.__scores.append(Score(self.__small_font, WHITE, enemy.get_score(), enemy.get_rect(), alpha=SCORE_ALPHA))
                self.__enemy_score += enemy.get_score() # add the enemy's score to the total
                self.__enemies_killed += 1

    def __update_scores(self): # update the score displays
        for score in self.__scores:
            if score.update(): # update returns True if the score should be removed
                self.__scores.remove(score)
        
    def __update_items(self): # update the items
        for item in self.__items:
            if self.__players == 1:
                # if the player collides with the item and already has an item, use the item
                # if the player collides and does not, set the player's item to the item
                if self.__player.get_rect().colliderect(item.get_rect()): 
                    if not self.__player.get_item() and self.__players == 1:
                        self.__player.set_item(item)
                    else:
                        self.__use_item(item.get_type())
                    self.__items.remove(item)
                    break # break to stop the item needlessly updating
            elif self.__players == 2:
                # check both players for a collision
                # if a player collides with an item, use the item
                if self.__player1.get_rect().colliderect(item.get_rect()):
                    self.__use_item(item.get_type(), player=1)
                    self.__items.remove(item)
                    break
                elif self.__player2.get_rect().colliderect(item.get_rect()):
                    self.__use_item(item.get_type(), player=2)
                    self.__items.remove(item)
                    break
            if not self.__time_freeze: # only update if time isn't frozen
                if item.update(): # update returns True if the item should be removed
                    self.__items.remove(item)

        # check and remove time freeze if necessary
        if self.__time_freeze and self.__timer - self.__time_freeze_time >= TIME_FREEZE_LENGTH:
            self.__time_freeze = False

    def update(self, event_list):
        for event in event_list:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.__players == 1: # in 1p, space uses an item
                    if self.__player.get_item():
                        self.__use_item(self.__player.get_item().get_type())
                        self.__player.set_item(None)
                elif self.__players == 2: # in 2p, space steals a life
                    if self.__player1.get_lives() <= 0 and self.__player2.get_lives() > 1:
                        self.__player2.increase_health(-1) # decreases health by 1
                        self.__player1.hit(-1) # increases health by 1, spawns back at start
                        self.__player1.add_immunity(4*FPS) # spawns with with immunity
                        self.__player1.set_spawned(True)
                    elif self.__player2.get_lives() <= 0 and self.__player1.get_lives() > 1:
                        self.__player1.increase_health(-1)
                        self.__player2.hit(-1)
                        self.__player2.add_immunity(4*FPS)
                        self.__player2.set_spawned(True)

        if self.__players == 2: # check if players should respawn, only necessary in 2p
            if not self.__player1.get_spawned() and self.__timer == self.__player1_respawn:
                self.__player1.set_spawned(True)
            if not self.__player2.get_spawned() and self.__timer == self.__player2_respawn:
                self.__player2.set_spawned(True)

        self.__enemy_rects = self.__enemy_rects_list() # update the enemy_rects list
        self.__check_enemy_spawn() # check if any more enemies can spawn
        
        if not self.__countdown: # update if not during the 3 second countdown
            self.__update_enemies()
            self.__update_scores()
            self.__update_items()

        self.__update_players() # player can move during the countdown

        if not self.__countdown and not self.__time_freeze:
            if self.__wave_index == -1: # immediately spawn first wave 
                self.__first_waves()
                self.__wave_index += 1
            if self.__enemy_queue.empty(): # to catch an empty queue, all enemies have spawned
                if not self.__enemies and not self.__enemies_to_spawn:
                    if not self.__crate_countdown:
                        self.__crate_countdown = 1*FPS # first countdown, until a crate is spawned
                    elif self.__crate_countdown == 1:  # 0 would be caught by first if
                        crate_thud.play()
                        self.__place_random(crate_image, 1, 2, collision=True, center_spawn=False)
                        if self.__players == 2: # place a second crate in 2 player
                            self.__place_random(crate_image, 1, 2, collision=True, center_spawn=False)

                        if self.__players == 1:
                            self.__generate_enemy_waves_1p()
                        elif self.__players == 2:
                            self.__generate_enemy_waves_2p()
                            
                        self.__wave_index += 1
                        self.__enemy_delay = 1*FPS # time before the enemies are spawned
                        self.__enemy_timer = 0     # time since last enemies were spawned
            elif self.__enemy_timer > self.__enemy_delay: # spawn enemies
                wave = self.__enemy_queue.dequeue()
                self.__enemies_to_spawn.extend(wave['enemies'])
                self.__enemy_timer = 0
                self.__enemy_delay = (wave['difficulty'] - self.__wave_index * INDEX_MULTIPLIER) * DELAY_MULTIPLIER
                if self.__enemy_delay < MIN_FRAMES:
                    self.__enemy_delay = MIN_FRAMES
        
        if self.__item_countdown > 0:
            self.__item_countdown -= 1
        
        if not self.__countdown:
            if not self.__time_freeze:
                self.__time_score += 1/FPS  # 1 score point for each second alive
                self.__enemy_timer += 1
                if self.__crate_countdown:
                    self.__crate_countdown -= 1
            self.__timer += 1
        else:
            self.__countdown -= 1

    def __display_controls_1p(self, image): # display the single player controls
        self.__small_font.render(image, "MOVE:", (4*EIGHT_PIXELS, 3*EIGHT_PIXELS), alignment=CENTER)
        self.__small_font.render(image, "W"+NEW_LINE+"A S D", (4*EIGHT_PIXELS, 4*EIGHT_PIXELS), alignment=CENTER)
        self.__small_font.render(image, "SHOOT:", (12*EIGHT_PIXELS, 3*EIGHT_PIXELS), alignment=CENTER)
        self.__small_font.render(image, "^"+NEW_LINE+"< _ >", (12*EIGHT_PIXELS, 4*EIGHT_PIXELS), alignment=CENTER)
        self.__small_font.render(image, "USE ITEM:", (8*EIGHT_PIXELS, 10*EIGHT_PIXELS), alignment=CENTER)
        self.__small_font.render(image, "SPACE", (8*EIGHT_PIXELS, 11*EIGHT_PIXELS), alignment=CENTER)
        self.__small_font.render(image, "PAUSE:", (8*EIGHT_PIXELS, 12.5*EIGHT_PIXELS), alignment=CENTER)
        self.__small_font.render(image, "ESC", (8*EIGHT_PIXELS, 13.5*EIGHT_PIXELS), alignment=CENTER)
    
    def __display_controls_2p(self, image): # display the two player controls
        self.__small_font.render(image, "PLAYER 1", (4*EIGHT_PIXELS, 2*EIGHT_PIXELS), alignment=CENTER)
        self.__small_font.render(image, "MOVE:", (4*EIGHT_PIXELS, 3*EIGHT_PIXELS), alignment=CENTER)
        self.__small_font.render(image, "W"+NEW_LINE+"A S D", (4*EIGHT_PIXELS, 4*EIGHT_PIXELS), alignment=CENTER)
        self.__small_font.render(image, "SHOOT:", (4*EIGHT_PIXELS, 6.5*EIGHT_PIXELS), alignment=CENTER)
        self.__small_font.render(image, "G"+NEW_LINE+"V B N", (4*EIGHT_PIXELS, 7.5*EIGHT_PIXELS), alignment=CENTER)
        self.__small_font.render(image, "PLAYER 2", (12*EIGHT_PIXELS, 2*EIGHT_PIXELS), alignment=CENTER)
        self.__small_font.render(image, "MOVE:", (12*EIGHT_PIXELS, 3*EIGHT_PIXELS), alignment=CENTER)
        self.__small_font.render(image, "9"+NEW_LINE+"I O P", (12*EIGHT_PIXELS, 4*EIGHT_PIXELS), alignment=CENTER)
        self.__small_font.render(image, "SHOOT:", (12*EIGHT_PIXELS, 6.5*EIGHT_PIXELS), alignment=CENTER)
        self.__small_font.render(image, "^"+NEW_LINE+"< _ >", (12*EIGHT_PIXELS, 7.5*EIGHT_PIXELS), alignment=CENTER)
        self.__small_font.render(image, "STEAL A LIFE:", (8*EIGHT_PIXELS, 10*EIGHT_PIXELS), alignment=CENTER)
        self.__small_font.render(image, "SPACE", (8*EIGHT_PIXELS, 11*EIGHT_PIXELS), alignment=CENTER)
        self.__small_font.render(image, "PAUSE:", (8*EIGHT_PIXELS, 12.5*EIGHT_PIXELS), alignment=CENTER)
        self.__small_font.render(image, "ESC", (8*EIGHT_PIXELS, 13.5*EIGHT_PIXELS), alignment=CENTER)

    def draw(self, screen):
        image = pygame.surface.Surface(self.__rect.size) # empty image to blit everything to

        above = []
        for row in self.__grid:
            for cell in row:
                if cell.get_collision() and cell.has_image():
                    above.append(cell)
                else:
                    cell.draw(image)                    

        if self.__countdown:
            if self.__players == 1:
                self.__display_controls_1p(image)
            elif self.__players == 2:
                self.__display_controls_2p(image)

        image.blit(fences_image, (0,0))

        for item in self.__items:
            item.draw(image)

        for bullet in self.__player.get_bullets() if self.__players == 1 else self.__player1.get_bullets() + self.__player2.get_bullets():
            bullet.draw(image)

        if self.__players == 1:
            self.__player.draw(image)
        elif self.__players == 2:
            if self.__player2.get_lives() > 0:
                self.__player2.draw(image)
            if self.__player1.get_lives() > 0:
                self.__player1.draw(image) # draw player 1 on top

        for enemy in self.__enemies:
            if not enemy.get_flying():
                enemy.draw(image)

        for cell in above:
            cell.draw(image)

        for score in self.__scores:
            score.draw(image)

        for enemy in self.__enemies:
            if enemy.get_flying():
                enemy.draw(image)
        
        if self.__countdown:
            self.__countdown_font.render(image, f"{ceil(self.__countdown/FPS)}", (8*EIGHT_PIXELS, 8*EIGHT_PIXELS - self.__countdown_font.get_height()//2), alignment=CENTER)

        self.__check_player_hit()

        offset = (0,0)
        if self.__shake:
            if self.__timer - self.__bomb_time == SCREEN_SHAKE_LENGTH and self.__shake:
                self.__shake = False
            else:
                if self.__timer - self.__bomb_time < SCREEN_SHAKE_LENGTH // 2: # if first half of shake, more extreme shakes
                    multiplier = 2
                else:
                    multiplier = 1
                if self.__timer % 8 > 4:
                    offset = (PIXEL_RATIO * multiplier, 0)
                else:
                    offset = (-PIXEL_RATIO * multiplier, 0)
                
        if self.__time_freeze:
            time = self.__timer - self.__time_freeze_time
            self.__freeze_surface.fill((100 + trunc(time / 6), 100 + trunc(time / 6), 160 + trunc(time / 6), 70 - trunc(time / 6)))
            image.blit(self.__freeze_surface, (0,0))

        screen.blit(image, (self.__pos[X] + offset[X], self.__pos[Y] + offset[Y]))
