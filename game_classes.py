from random import randint
from math import trunc, sin, pi

import pygame

from constants import *
from utility_functions import split, get_key
from images import (item_images, bullet_image, default_enemy_images, fast_enemy_images, flying_enemy_images, 
                    crow_enemy_images, tough_enemy_images, spirit_enemy_images, exclamation)
from sounds import crow_sound, enemy_killed, default_shoot

#======================Cell Class======================#
# an 8 pixel by 8 pixel square that can have collision and an image
# makes up the grid of the game as plain grass, flowers, fences, and crates
class Cell():
    def __init__(self, pos):
        self.__image = None # an image for the cell to display
        self.__pos = pos
        self.__collision = False
        self.__shade = False # if the cell should cast a shadow
        self.__rect = pygame.Rect(pos, (EIGHT_PIXELS, EIGHT_PIXELS))
        self.__shade_surface = pygame.Surface((EIGHT_PIXELS, EIGHT_PIXELS), pygame.SRCALPHA)
        pygame.draw.rect(self.__shade_surface, (0,0,0,50), (0, 0, EIGHT_PIXELS, EIGHT_PIXELS)) # a mostly transparent black

    def has_image(self): # returns True if the cell has an image
        if self.__image:
            return True
        return False
    
    def get_collision(self): # returns the collision attribute of the cell
        return self.__collision
    
    def get_rect(self): # returns the rect of the cell
        return self.__rect
    
    def set_image(self, image): # sets the image of the cell
        self.__image = image

    def set_shade(self, shade): # sets the shade attribute of the cell
        self.__shade = shade

    def set_collision(self, collision): # sets the collision attribute of the cell
        self.__collision = collision

    def draw(self, screen): # draws the cell to the screen
        pygame.draw.rect(screen, GRASS_GREEN, self.__rect)
        if self.__shade:
            screen.blit(self.__shade_surface, (self.__pos[X]+PIXEL_RATIO, self.__pos[Y]+PIXEL_RATIO)) # displayed one pixel down and across
        if self.__image:
            screen.blit(self.__image, self.__rect)

#======================Player Class======================#
# a controllable character that can move and shoot
# one or two initialised for the game
class Player():
    def __init__(self, hex_string, game_rect, player=0):
        self.__player = player # 0 for single player, 1 for 1st of two player, 2 for 2nd of two player
        match player:
            case 0: # spawn single player at the center
                self.__initial_pos = pygame.math.Vector2((game_rect.center))
            case 1: # spawn first player a little to the left
                self.__initial_pos = pygame.math.Vector2((game_rect.centerx - EIGHT_PIXELS//2, game_rect.centery))
            case 2: # spawn second player a little to the right
                self.__initial_pos = pygame.math.Vector2((game_rect.centerx + EIGHT_PIXELS//2, game_rect.centery))
        self.__pos = self.__initial_pos.copy()
        self.__custom_character(hex_string) # turn the hex string into images
        self.__image = self.__front_image
        self.__immune_image = self.__front_immune
        self.__rect = self.__image.get_rect(center = self.__pos)
        self.__speed = PLAYER_SPEED
        self.__lives = 3
        self.__bullets = []
        self.__bullet_damage = 1 # lots of variables to make possible future items easy to implement
        self.__last_shot = 0
        self.__fire_rate = FIRE_RATE # frames between each shot
        self.__fire_rate_multiplier = 1
        self.__game_rect = game_rect

        self.__item = None
        self.__shoes = False
        self.__shoes_time = -1
        self.__shotgun = False
        self.__shotgun_time = -1
        self.__rapid_fire = False
        self.__rapid_fire_time = -1
        self.__backwards_shot = False
        self.__backwards_shot_time = -1
        self.__immunity = False
        self.__immunity_time = -1

        self.__spawned = True # used for two player when player has yet to respawn

        self.__new_rect = self.__rect.copy()
        self.__new_rect_x = self.__rect.copy()
        self.__new_rect_y = self.__rect.copy()
        
        self.__bullets_shot = 0

        self.__timer = 0

    def GET_IMAGE(self):
        return self.__image

    def __custom_character(self, hex_string): # converts a custom hex string into front, back, left, and right, images
        self.__front_image, self.__front_immune = self.__hex_to_image(FRONT_PATTERNS, hex_string)
        self.__back_image, self.__back_immune = self.__hex_to_image(BACK_PATTERNS, hex_string)
        self.__left_image, self.__left_immune = self.__hex_to_image(LEFT_PATTERNS, hex_string)
        self.__right_image, self.__right_immune = self.__hex_to_image(RIGHT_PATTERNS, hex_string)
    
    def __hex_to_image(self, patterns, hex_string): # converts a hex string and pixel patterns into an image
        image = pygame.Surface((EIGHT_PIXELS, EIGHT_PIXELS), pygame.SRCALPHA) # blank surface to draw pixels to
        select_hex = split(hex_string[:COLOUR_DEPTH*len(patterns)], COLOUR_DEPTH) # splits the hex codes referring to the selected colours into a list
        hat_hex = split(split(hex_string[COLOUR_DEPTH*len(patterns):], COLOUR_DEPTH), 8) # splits the hex codes referring to the hat colours into a list of rows

        # for each pixel pattern, draw its pixels onto the blank surface in the colours specified by the selected hex codes
        for i in range(len(patterns)):
            for row, column in patterns[i]:
                pygame.draw.rect(image, get_key(select_hex[i], BITMAP_DICTIONARY), pygame.rect.Rect((column*PIXEL_RATIO,row*PIXEL_RATIO), (1*PIXEL_RATIO, 1*PIXEL_RATIO)))

        # for each hex code in each row of the hat list, draw a pixel to the screen with the colour specified
        for i in range(len(hat_hex)):
            for j in range(len(hat_hex[0])):
                if get_key(hat_hex[i][j], BITMAP_DICTIONARY):
                    pygame.draw.rect(image, get_key(hat_hex[i][j], BITMAP_DICTIONARY), pygame.rect.Rect((j*PIXEL_RATIO,i*PIXEL_RATIO), (1*PIXEL_RATIO, 1*PIXEL_RATIO)))

        # creates a transparent white version of the image to draw when the player is immune to damage
        immune = pygame.mask.from_surface(image).to_surface(setcolor=(255,255,255,100), unsetcolor=(0,0,0,0))

        return image, immune

    def __move(self, keys, collidables):
        velocity_x = 0 # the movement of the player's x position
        velocity_y = 0 # the movement of the player's y position

        velocity_x, velocity_y = self.__move_input(velocity_x, velocity_y, keys)  # convert keyboard input into movement

        # rects approximate positions to integer values, not pixel perfect when comparing collisions with the player position
        # dict used for each side and their positions, calculated from adding or subtracting half of the player's width
        player_sides = {'TOP'    : self.__pos[Y] - EIGHT_PIXELS/2, 
                        'BOTTOM' : self.__pos[Y] + EIGHT_PIXELS/2,
                        'LEFT'   : self.__pos[X] - EIGHT_PIXELS/2,
                        'RIGHT'  : self.__pos[X] + EIGHT_PIXELS/2} 

        velocity_x, velocity_y = self.__edge_collisions(player_sides, velocity_x, velocity_y)  # check and correct for collisions with the edges of the game

        velocity_x, velocity_y = self.__collidables_collisions(player_sides, velocity_x, velocity_y, collidables) # check and correct for collisions with each collidable object in the game
        
        return velocity_x, velocity_y

    def __move_input(self, velocity_x, velocity_y, keys): # converts keyboard input into movement
        if (keys[pygame.K_w] and self.__player == 0) or (keys[pygame.K_w] and self.__player == 1) or (keys[pygame.K_9] and self.__player == 2):
            velocity_y -= self.__speed # position is taken from the topleft, so upwards is negative y
            self.__image = self.__back_image # change the player image to be facing upwards
            self.__immune_image = self.__back_immune
        if (keys[pygame.K_s] and self.__player == 0) or (keys[pygame.K_s] and self.__player == 1) or (keys[pygame.K_o] and self.__player == 2):
            velocity_y += self.__speed
            self.__image = self.__front_image
            self.__immune_image = self.__front_immune
        if (keys[pygame.K_a] and self.__player == 0) or (keys[pygame.K_a] and self.__player == 1) or (keys[pygame.K_i] and self.__player == 2):
            velocity_x -= self.__speed
            self.__image = self.__left_image
            self.__immune_image = self.__left_immune
        if (keys[pygame.K_d] and self.__player == 0) or (keys[pygame.K_d] and self.__player == 1) or (keys[pygame.K_p] and self.__player == 2):
            velocity_x += self.__speed
            self.__image = self.__right_image
            self.__immune_image = self.__right_immune

        # if the player is moving diagonally, divide each velocity by root 2 to normalise
        if velocity_x != 0 and velocity_y != 0:
            velocity_x /= 2**0.5
            velocity_y /= 2**0.5

        if self.__shoes:
            velocity_x *= SHOE_MULTIPLIER
            velocity_y *= SHOE_MULTIPLIER
        
        return velocity_x, velocity_y
    
    def __edge_collisions(self, player_sides, velocity_x, velocity_y): # check and correct for collisions with the edges of the game
        if player_sides['LEFT'] - self.__game_rect.left < self.__speed and velocity_x < 0: # if distance to left wall is less than the distance player will move and player is moving left
            velocity_x = self.__game_rect.left - player_sides['LEFT']                      # the amount moving left becomes the distance between the wall and the player
        elif self.__game_rect.right - player_sides['RIGHT'] < self.__speed and velocity_x > 0:
            velocity_x = self.__game_rect.right - player_sides['RIGHT']
        if player_sides['TOP'] - self.__game_rect.top < self.__speed and velocity_y < 0:
            velocity_y = self.__game_rect.top - player_sides['TOP']
        elif self.__game_rect.bottom - player_sides['BOTTOM'] < self.__speed and velocity_y > 0:
            velocity_y = self.__game_rect.bottom - player_sides['BOTTOM']

        return velocity_x, velocity_y

    def __collidables_collisions(self, player_sides, velocity_x, velocity_y, collidables): # check and correct for collisions with each collidable object in the game
        # rects that show where the player is about to move
        self.__new_rect_x.center = self.__pos + pygame.math.Vector2(velocity_x, 0) # only taking into account x motion
        self.__new_rect_y.center = self.__pos + pygame.math.Vector2(0, velocity_y) # only taking into account y motion
        self.__new_rect.center = self.__pos + pygame.math.Vector2(velocity_x, velocity_y) # taking into account both

        x = velocity_x # temporary variables so it doesn't change between loops
        y = velocity_y

        for collidable in collidables:
            collision_x = collidable.colliderect(self.__new_rect_x) # returns true if its rect collides with the players new x rect
            collision_y = collidable.colliderect(self.__new_rect_y)
            # diagonal collision occurs when the player will only move into the collidable when taking into account both x and y motion
            # if you just looked at x and y separately, you would not see any collision
            diagonal = collidable.colliderect(self.__new_rect) and not (collision_x or collision_y)
            
            # if there are collisions, adjust the motion of the player to the distance between them and the collidable
            if collision_x or diagonal:
                if x < 0:  # moving left
                    velocity_x = -(player_sides['LEFT'] - collidable.right)
                elif x > 0:  # moving right
                    velocity_x = collidable.left - player_sides['RIGHT']

            if collision_y or diagonal:
                if y < 0:  # moving up
                    velocity_y = -(player_sides['TOP'] - collidable.bottom)
                elif y > 0:  # moving down
                    velocity_y = collidable.top - player_sides['BOTTOM']

        return velocity_x, velocity_y

    def __shoot(self, keys): # converts keyboard input into shooting
        bullet_x = 0 # direction of the bullet being shot
        bullet_y = 0
        x_offset = 0 # offset to adjust the spawning of the bullet to match the position of the gun
        y_offset = 0

        # single player and 2nd player of two player both use the arrow keys for shooting
        if (keys[pygame.K_UP] and (self.__player == 0 or self.__player == 2)) or (keys[pygame.K_g] and self.__player == 1):
            bullet_y -= 1
        if (keys[pygame.K_DOWN] and (self.__player == 0 or self.__player == 2)) or (keys[pygame.K_b] and self.__player == 1):
            bullet_y += 1
        if (keys[pygame.K_LEFT] and (self.__player == 0 or self.__player == 2)) or (keys[pygame.K_v] and self.__player == 1):
            bullet_x -= 1
        if (keys[pygame.K_RIGHT] and (self.__player == 0 or self.__player == 2)) or (keys[pygame.K_n] and self.__player == 1):
            bullet_x += 1
                
        if bullet_y == -1:                  # if shooting up
            x_offset = PIXEL_RATIO * 2.5    # spawn bullet 3 pixels to the right (from center of player)
            y_offset = PIXEL_RATIO * -1     # and 1 pixel up (-1 pixel down)
            self.__image = self.__back_image
            self.__immune_image = self.__back_immune
        elif bullet_y == 1:
            x_offset = PIXEL_RATIO * -2.5
            y_offset = PIXEL_RATIO * 5
            self.__image = self.__front_image
            self.__immune_image = self.__front_immune
        if bullet_x == -1:
            x_offset = PIXEL_RATIO * -5
            y_offset = PIXEL_RATIO * 1.5
            self.__image = self.__left_image
            self.__immune_image = self.__left_immune
        elif bullet_x == 1:
            x_offset = PIXEL_RATIO * 4   
            y_offset = PIXEL_RATIO * 1.5   
            self.__image = self.__right_image
            self.__immune_image = self.__right_immune

        if bullet_x != 0 and bullet_y != 0: # diagonal
            bullet_x /= 2**0.5
            bullet_y /= 2**0.5
        
        # if the player is trying to shoot and enough time has passed since the last shot, shoot
        if (bullet_x != 0 or bullet_y != 0 )and (self.__timer - self.__last_shot > self.__fire_rate * self.__fire_rate_multiplier):
            offset = (x_offset, y_offset)
            direction = pygame.math.Vector2(bullet_x,bullet_y)
            bullet = Bullet(self.__pos + offset, direction, self.__bullet_damage, self.__timer)
            self.__bullets.append(bullet)
            self.__bullets_shot += 1
            if self.__shotgun:
                self.__shoot_shotgun(offset, direction)
            if self.__backwards_shot:
                self.__shoot_backwards_shot(offset, direction)
            self.__last_shot = self.__timer
                                
    def __shoot_shotgun(self, offset, direction): # shoot 2 extra bullets at a slightly offset angle
        bullet1 = Bullet(self.__pos + offset, direction.rotate(-11.25), self.__bullet_damage, self.__timer)  # 11.25 degrees anticlockwise
        bullet2 = Bullet(self.__pos + offset, direction.rotate(11.25), self.__bullet_damage, self.__timer) # 11.25 degrees clockwise
        self.__bullets.append(bullet1)
        self.__bullets.append(bullet2)
        self.__bullets_shot += 2
    
    def __shoot_backwards_shot(self, offset, direction): # shoots an extra bullet in the opposite direction
        bullet = Bullet(self.__pos + offset, direction.rotate(180), self.__bullet_damage, self.__timer) # 180 degrees clockwise
        self.__bullets.append(bullet)
        self.__bullets_shot += 1
        if self.__shotgun:
            self.__shoot_shotgun(offset, -direction) # shoot shotgun backwards too
    
    def add_shoes(self): # gives the player shoes
        self.__shoes = True
        self.__shoes_time = self.__timer
  
    def add_shotgun(self): # gives the player shotgun
        self.__shotgun = True
        self.__shotgun_time = self.__timer
    
    def add_rapid_fire(self): # gives the player rapid fire
        self.__rapid_fire = True
        self.__rapid_fire_time = self.__timer

    def add_immunity(self, time): # gives the player immunity
        self.__immunity = True
        self.__immunity_time = self.__timer + time

    def add_backwards_shot(self): # gives the player backwards shot
        self.__backwards_shot = True
        self.__backwards_shot_time = self.__timer

    def increase_health(self, amount): # increase the player's health
        self.__lives += amount

    def empty_bullets(self): # reset the player's bullets
        self.__bullets = []

    def remove_bullet(self, bullet): # remove a bullet from the list
        self.__bullets.remove(bullet)

    def get_bullets_shot(self): # return the number of bullets shot
        return self.__bullets_shot

    def get_immunity(self): # return the immunity status
        return self.__immunity
    
    def get_spawned(self): # return the spawned status
        return self.__spawned
    
    def get_item(self): # return the item of the player
        return self.__item
    
    def get_lives(self): # return the health of the player
        return self.__lives
    
    def get_player(self): # return the player number
        return self.__player
    
    def get_rect(self): # return the rect of the player
        return self.__rect
    
    def get_bullets(self): # return the bullets list
        return self.__bullets
    
    def get_pos(self): # return the position of the player
        return self.__pos
    
    def set_item(self, item): # set the item of the player
        self.__item = item

    def set_immunity(self, immunity): # set the immunity status
        self.__immunity = immunity

    def set_spawned(self, spawned): # set the spawned status
        self.__spawned = spawned

    def update(self, collidables, other_player_rect=None): # update the player and take keyboard input
        self.__timer += 1

        # fire rate slightly reduced if the player has shotgun, fire rate increased if the player has rapid fire
        self.__fire_rate_multiplier = (RAPID_FIRE_MULTIPLIER if self.__rapid_fire else 1) * (SHOTGUN_RATE_MULTIPLIER if self.__shotgun else 1)   

        for bullet in self.__bullets:
            for collidable in collidables:
                if collidable.colliderect(bullet.get_rect()):
                    self.__bullets.remove(bullet) # remove every bullet that has collided with a collidable object
                    break # could otherwise try to remove the bullet from the list twice
            bullet.update()
            if self.__timer - bullet.get_spawn_time() > BULLET_LIFETIME: # so that bullets don't last forever if they don't hit anything
                self.__bullets.remove(bullet)

        if self.__lives > 0 and self.__spawned:
            keys = pygame.key.get_pressed()
            velocity_x, velocity_y = self.__move(keys, collidables + ([other_player_rect] if other_player_rect else []))
            self.__pos += pygame.math.Vector2(velocity_x, velocity_y)
            self.__rect.center = self.__pos
            self.__shoot(keys)

        # check the lifetime of power ups
        if self.__shotgun and self.__timer - self.__shotgun_time >= SHOTGUN_LENGTH:
            self.__shotgun = False
        if self.__shoes and self.__timer - self.__shoes_time >= SHOES_LENGTH:
            self.__shoes = False
        if self.__rapid_fire and self.__timer - self.__rapid_fire_time >= RAPID_FIRE_LENGTH:
            self.__rapid_fire = False
        if self.__backwards_shot and self.__timer - self.__backwards_shot_time >= BACKWARDS_SHOT_LENGTH:
            self.__backwards_shot = False
        if self.__immunity and self.__timer == self.__immunity_time:
            self.__immunity = False

    def hit(self, damage): # damage and reset the player
        if not self.__immunity:
            self.__lives -= damage
            self.__item = None
            self.__shoes, self.__shotgun, self.__rapid_fire, self.__backwards_shot = False, False, False, False
            self.__pos = self.__initial_pos.copy()

    def draw(self, screen): # draw the player
        if self.__spawned:
            screen.blit(self.__image, (self.__pos[X] - EIGHT_PIXELS/2, self.__pos[Y] - EIGHT_PIXELS/2))
            if self.__immunity:
                if FPS//2 < (self.__immunity_time - self.__timer) % FPS < FPS: # flash immunity image on and off every 0.5 seconds
                    screen.blit(self.__immune_image, (self.__pos[X] - EIGHT_PIXELS/2, self.__pos[Y] - EIGHT_PIXELS/2))

#======================Bullet Class======================#
# a bullet that travels in a given direction
# shot by the player during the game
class Bullet():
    def __init__(self, pos, direction, damage, spawn_time):
        self.__direction = direction
        self.__pos = pygame.math.Vector2(pos)
        self.__speed = BULLET_SPEED
        self.__image = bullet_image
        self.__damage = damage
        self.__rect = self.__image.get_rect(center = self.__pos)
        self.__spawn_time = spawn_time
        default_shoot.play() 

    def get_rect(self): # return the rect of the bullet
        return self.__rect
    
    def get_damage(self): # return the damage of the bullet
        return self.__damage
    
    def get_spawn_time(self): # return the spawn time of the bullet
        return self.__spawn_time

    def update(self): # update the position of the bullet
        self.__pos += self.__direction * self.__speed
        self.__rect.center = self.__pos

    def draw(self, screen): # draw the bullet
        screen.blit(self.__image, self.__rect.topleft)

#======================Item Class======================#
# a temporary item that has an image and a type and a rect
class Item():
    def __init__(self, pos, type):
        self.__type = type
        self.__image = item_images[self.__type]
        self.__rect = self.__image.get_rect(center = pos)
        self.__timer = 0 # how many frames the item has been around for

    def get_type(self): # return the type of the item
        return self.__type
    
    def get_rect(self): # return the rect of the item
        return self.__rect
    
    def update(self): # check how long the item has been around for
        self.__timer += 1
        if self.__timer > ITEM_TIME:
            return True # true returned if the item should be removed from the list
        elif self.__timer > ITEM_TIME - ITEM_FLASH_TIME:
            if self.__timer % (ITEM_FLASH_TIME//9) == 0: # flip the image on and off 9 times
                self.__image = None if self.__image else item_images[self.__type]
        return False

    def draw(self, screen): # draw the item
        if self.__image:
            screen.blit(self.__image, self.__rect)

#======================Score Class======================#
# a temporary display of a killed enemie's score
class Score():
    def __init__(self, font, colour, score, rect, alpha=255):
        self.__font = font.new_colour_copy(colour, alpha=alpha)
        self.__score = str(score)
        self.__rect = rect
        self.__timer = 0

    def update(self): # check how long the score has been around for
        self.__timer += 1
        if self.__timer > SCORE_LENGTH:
            return True # true returned if the score should be removed from the list
        return False

    def draw(self, screen): # draw the score
        self.__font.render(screen, self.__score, (self.__rect.centerx, self.__rect.top + PIXEL_RATIO), alignment=CENTER)

#======================Enemy Class======================#
# a base class for all the different enemy types
class Enemy():
    def __init__(self, pos, settings, initial_image, flying):
        self._pos = pygame.math.Vector2(pos)
        self._prev_pos = self._pos.copy() # pos reverted to previous pos if a collision occurs
        self._health = settings["HEALTH"] # settings is a dictionary of the health, speed, and score
        self._speed = settings["SPEED"]
        self.__score = settings["SCORE"]
        self._image = initial_image
        self._timer = 0
        self.__flying = flying # whether the enemy is flying or not
        self._rect = self._image.get_rect(center = self._pos)
        self.__red = False
        self.__hit_timer = 0

    def get_flying(self): # return whether the enemy is flying or not
        return self.__flying
    
    def get_score(self): # return the score of the enemy
        return self.__score
    
    def get_rect(self): # return the rect of the enemy
        return self._rect
    
    def get_health(self): # return the health of the enemy
        return self._health
    
    def hit(self, damage=1): # damage the enemy
        self._health -= damage
        self.__red = True # temporarily red after hit
        self.__hit_timer = 0
        if self._health == 0:
            enemy_killed.play()
    
    def draw(self, screen): # draw the enemy
        self.__hit_timer += 1
        if self.__hit_timer == HIT_TIME: 
            self.__red = False
        screen.blit(self._image, (self._pos[X] - EIGHT_PIXELS/2, self._pos[Y] - EIGHT_PIXELS/2))
        # if the enemy was hit recently, blit a slightly transparent red version of the enemy's image over the enemy
        if self.__red:
            screen.blit(pygame.mask.from_surface(self._image).to_surface(setcolor=(255,0,0,100), unsetcolor=(0,0,0,0)), (self._pos[X] - EIGHT_PIXELS/2, self._pos[Y] - EIGHT_PIXELS/2))

#======================Default Enemy Class======================#
# ground enemy, the first enemy the player sees
# moves towards the player in straight lines with random influence
class DefaultEnemy(Enemy):
    def __init__(self, pos, direction):
        super().__init__(pos, DEFAULT_ENEMY, default_enemy_images[direction][1], False)
        self.__direction_change_time = 0 # last time the direction was changed
        self.__random_time = 0 # time until direction is next changed
        self.__direction = direction # direction the enemy is currently facing
        self.__images = default_enemy_images # 2d array of animation frames in rows for directions

    def __move(self): # return velocities for the enemy based on its direction
        if self.__direction == LEFT:
            velocity_x = -self._speed
            velocity_y = 0
        elif self.__direction == RIGHT:
            velocity_x = self._speed
            velocity_y = 0
        elif self.__direction == UP:
            velocity_x = 0
            velocity_y = -self._speed
        elif self.__direction == DOWN:
            velocity_x = 0
            velocity_y = self._speed
        return velocity_x, velocity_y
    
    def __change_direction(self, player_pos): # check for and change the direction of the enemy
        x_distance = player_pos[X] - self._pos[X]
        y_distance = player_pos[Y] - self._pos[Y]
        if abs(x_distance) > abs(y_distance): # initially direction is picked based upon distance to player
            if x_distance < 0:
                self.__direction = LEFT
            else:
                self.__direction = RIGHT
        else:
            if y_distance < 0:
                self.__direction = UP
            else:
                self.__direction = DOWN
        self.__direction_change_time = self._timer

        # if the enemy is between 2 and 8 grid cells from the player, chance for random direction
        if 2*EIGHT_PIXELS < (x_distance**2 + y_distance**2)**0.5 < 8*EIGHT_PIXELS:
            self.__random_time = randint(FPS//4, FPS) # random time before next direction check between 15 and 60 frames
            random_int = randint(-1,3) # 2/5 chance to move randomly
            if random_int <= 1: # only accepts -1, 0, or 1, can add to direction to turn left / right
                self.__direction = (self.__direction + random_int) % 4 # mod 4 as there are 4 directions

    def __check_collisions(self, velocity_x, velocity_y, game_rect, collidables, enemy_rects): # check for collisions
        # doesn't need to be pixel perfect like for the player
        # simply, if a collision is detected after the enemy moves, the enemy returns to their previous position
        collision = False

        if self._rect.collidelistall(collidables):
            collision = True # collision is true if any collision between the enemy and a collidable object

        if ((self._rect.left <= game_rect.left and velocity_x < 0) 
                or (self._rect.top <= game_rect.top and velocity_y < 0) 
                or (self._rect.right >= game_rect.right and velocity_x > 0) 
                or (self._rect.bottom >= game_rect.bottom and velocity_y > 0)):
            collision = True # collision is true if any collision between the enemy and the game sides
            
        enemy_rects.remove(self._rect) # remove the enemy's rect from the list
        if self._rect.collidelistall(enemy_rects):
            collision = True

        if collision: # if there is a collision, return the enemy to their previous position
            self._pos = self._prev_pos.copy()
            self._rect.center = self._pos
            self.__random_time = 6 # reduce random time if colliding
        
    def update(self, player_pos, game_rect, collidables, enemy_rects, player2_pos=None): # update and move the enemy
        # player_pos always supplied in one player
        # player_pos only supplied if player 1 is alive in two player
        # player2_pos only supplied if player 2 is alive in two player
        if player2_pos: # check who is closest if there is a second position to look at
            if player_pos:
                player1_distance = ((player_pos[X] - self._pos[X])**2 + (player_pos[Y] - self._pos[Y])**2)**0.5  
            else:
                player1_distance = GAME_WIDTH*EIGHT_PIXELS # arbitrarily large
            player2_distance = ((player2_pos[X] - self._pos[X])**2 + (player2_pos[Y] - self._pos[Y])**2)**0.5
            if player2_distance <= player1_distance:
                player_pos = player2_pos

        self._timer += 1

        if player_pos:
            if self._timer - self.__direction_change_time > self.__random_time:
                self.__change_direction(player_pos)
            velocity_x, velocity_y = self.__move()
            self._image = self.__images[self.__direction][trunc(((self._timer * 4)/FPS) % len(self.__images[0]))] # 4 animation frames per second
            self._prev_pos = self._pos.copy() #.copy() so that they aren't linked
            self._pos += (velocity_x, velocity_y)
            self._rect.center = self._pos # update the position of the rect
            self.__check_collisions(velocity_x, velocity_y, game_rect, collidables, enemy_rects)

#======================Fast Enemy Class======================#
# ground enemy, the second enemy the player will see
# runs straight until it meets the player in either x or y, then changes direction
class FastEnemy(Enemy):
    def __init__(self, pos, direction):
        super().__init__(pos, FAST_ENEMY, fast_enemy_images[direction][0], False)
        self.__direction = None
        self.__random_move_delay = 0 # to keep moving in a direction for n frames despite anything else
        self.__images = fast_enemy_images
    
    def __move(self): # return velocities for the enemy based on its direction
        if self.__direction == LEFT:
            velocity_x = -self._speed
            velocity_y = 0
        elif self.__direction == RIGHT:
            velocity_x = self._speed
            velocity_y = 0
        elif self.__direction == UP:
            velocity_x = 0
            velocity_y = -self._speed
        elif self.__direction == DOWN:
            velocity_x = 0
            velocity_y = self._speed
        return velocity_x, velocity_y
    
    def __check_direction(self, player_pos): # check for and change the direction of the enemy
        x_distance = player_pos[X] - self._pos[X]
        y_distance = player_pos[Y] - self._pos[Y]
        if self.__direction == None:
            if abs(x_distance) > abs(y_distance):
                self.__check_x(x_distance)
            else:
                self.__check_y(y_distance)
        elif self.__direction == UP:
            if y_distance > 0: # if reached player in y
                self.__check_x(x_distance) # swap to x movement
        elif self.__direction == DOWN:
            if y_distance < 0:
                self.__check_x(x_distance)
        elif self.__direction == LEFT:
            if x_distance > 0: # if reached player in x
                self.__check_y(y_distance) # swap to y movement
        elif self.__direction == RIGHT:
            if x_distance < 0:
                self.__check_y(y_distance)

    def __check_x(self, x_distance): # pick x direction based on an x distance
        if x_distance < 0:
            self.__direction = LEFT
        else:
            self.__direction = RIGHT

    def __check_y(self, y_distance): # pick y direction based on a y distance
        if y_distance < 0:
            self.__direction = UP
        else:
            self.__direction = DOWN

    def __check_collisions(self, velocity_x, velocity_y, game_rect, collidables, enemy_rects): # check for collisions
        collision = False

        if self._rect.collidelistall(collidables):
            collision = True

        if ((self._rect.left <= game_rect.left and velocity_x < 0) 
                or (self._rect.top <= game_rect.top and velocity_y < 0) 
                or (self._rect.right >= game_rect.right and velocity_x > 0) 
                or (self._rect.bottom >= game_rect.bottom and velocity_y > 0)):
            collision = True

        enemy_rects.remove(self._rect)

        if self._rect.collidelistall(enemy_rects):
            collision = True

        if collision:
            self._pos = self._prev_pos.copy()
            self._rect.center = self._pos
            random_int = randint(-1,3)
            if random_int <= 1:
                self.__direction = (self.__direction + random_int) % 4
            self.__random_move_delay = FPS//2 # if collision, possibly moves in a random direction for 0.5 seconds
        
    def update(self, player_pos, game_rect, collidables, enemy_rects, player2_pos=None): # update and move the enemy
        if player2_pos: # check who is closest
            if player_pos:
                player1_distance = ((player_pos[X] - self._pos[X])**2 + (player_pos[Y] - self._pos[Y])**2)**0.5  
            else:
                player1_distance = GAME_WIDTH*EIGHT_PIXELS # arbitrarily large
            player2_distance = ((player2_pos[X] - self._pos[X])**2 + (player2_pos[Y] - self._pos[Y])**2)**0.5
            if player2_distance <= player1_distance:
                player_pos = player2_pos

        self._timer += 1
        
        if player_pos:
            if self.__random_move_delay == 0: 
                self.__check_direction(player_pos)
            self._prev_pos = self._pos.copy()
            velocity_x, velocity_y = self.__move()
            self._image = self.__images[self.__direction][trunc(((self._timer * 8)/FPS) % len(self.__images[0]))] # 8 animation frames per second
            self._pos += (velocity_x, velocity_y)
            self._rect.center = self._pos
            self.__check_collisions(velocity_x, velocity_y, game_rect, collidables, enemy_rects)
            if self.__random_move_delay > 0:
                self.__random_move_delay -= 1

#======================Flying Enemy Class======================#
# flying enemy, the third enemy the player will see
# moves directly towards the player with speed varying sinusoidally
class FlyingEnemy(Enemy):
    def __init__(self, pos, direction):
        super().__init__(pos, FLYING_ENEMY, flying_enemy_images[direction][0], True)
        self.__cycle = FPS * 3 # time period of the sine wave, varies over 3 seconds
        self.__direction = direction
        self.__images = flying_enemy_images

    def __move(self, player_pos): # return velocities for the enemy based on the player position
        velocity_x = 0
        velocity_y = 0
        x_distance = player_pos[X] - self._pos[X]
        y_distance = player_pos[Y] - self._pos[Y]
        distance = (x_distance**2 + y_distance**2)**0.5 # pythagoras
        if distance != 0:
            velocity_x += self._speed * (x_distance / distance) # portion of direction in the x
            velocity_y += self._speed * (y_distance / distance) # portion of direction in the y
        return velocity_x, velocity_y
    
    def __check_direction(self, velocity_x, velocity_y): # alter direction attribute based on velocities
        if abs(velocity_y) + 0.5 > abs(velocity_x): # favour image being up or down
            if velocity_y > 0:
                self.__direction = DOWN
            else:
                self.__direction = UP
        else:
            if velocity_x > 0:
                self.__direction = RIGHT
            else:
                self.__direction = LEFT
    
    def update(self, player_pos, player2_pos=None): # update and move the enemy
        if player2_pos: # check who is closest
            if player_pos:
                player1_distance = ((player_pos[X] - self._pos[X])**2 + (player_pos[Y] - self._pos[Y])**2)**0.5  
            else:
                player1_distance = GAME_WIDTH*EIGHT_PIXELS # arbitrarily large
            player2_distance = ((player2_pos[X] - self._pos[X])**2 + (player2_pos[Y] - self._pos[Y])**2)**0.5
            if player2_distance <= player1_distance:
                player_pos = player2_pos

        self._timer += 1

        if player_pos:
            self._speed = (sin((self._timer * 2*pi) / self.__cycle) / 2) * PIXEL_RATIO/5 * FPS/60 + FLYING_ENEMY["SPEED"] # sinusoidal speed variation
            velocity_x, velocity_y = self.__move(player_pos)
            self.__check_direction(velocity_x, velocity_y) # so direction is correct for animation
            # no checking collisions for flying enemies
            self._image = self.__images[self.__direction][trunc(((self._timer * 4)/FPS) % len(self.__images[0]))] # 4 animation frames per second
            self._pos += velocity_x, velocity_y
            self._rect.center = self._pos

#======================Crow Enemy Class======================#
# flying enemy, the fourth enemy the player will see
# moves very fast in a straight line across the game, warns the player of its position before moving
class CrowEnemy(Enemy):
    def __init__(self, pos, direction, game_rect):
        super().__init__(pos, CROW_ENEMY, crow_enemy_images[direction], True)
        # crow enemy has a transparent version of the same image that follows behind them to add motion blur
        self.__blur_image = self._image.copy()
        self.__blur_image.set_alpha(100)
        self.__blur_rect = self._rect.copy()
        # a larger rect created to detect if the enemy should be killed because it has flown far off screen
        self.__large_rect = pygame.Rect((self._rect.x - EIGHT_PIXELS, self._rect.y - EIGHT_PIXELS), 
                                        (self._rect.width + 2*EIGHT_PIXELS, self._rect.height + 2*EIGHT_PIXELS))
        self.__game_rect = game_rect
        blur_distance = CROW_BLUR_DISTANCE
        if direction == RIGHT: # velocity is decided at the beginning as the enemy does not change direction
            self.__velocity = (self._speed, 0)
            self.__blur_pos = (-blur_distance, 0)
        elif direction == LEFT:
            self.__velocity = (-self._speed, 0)
            self.__blur_pos = (blur_distance, 0)
        elif direction == DOWN:
            self.__velocity = (0, self._speed)
            self.__blur_pos = (0, -blur_distance)
        elif direction == UP:
            self.__velocity = (0, -self._speed)
            self.__blur_pos = (0, blur_distance)
        # an exclamation mark is drawn for a few seconds before the enemy appears to warn the player of its location
        # position is calculated by adding 8 pixels of movement in the enemy's direction as they spawn 8 pixels off screen
        self.__exclamation_pos = pygame.math.Vector2(self._rect.topleft) + (pygame.math.Vector2(self.__velocity)*(EIGHT_PIXELS/self._speed))

    def update(self, *args): # *args to get and disregard any other arguments passed in
        if self._timer == 0:
            crow_sound.play() # sound needs to be played in update otherwise it would play when the enemy is initialised in the wave creation
        self._timer += 1
        if self._timer > CROW_PAUSE: # paused for a few seconds before moving
            self._pos += self.__velocity
            self._rect.center = self._pos
            self.__blur_rect.center = self._pos + self.__blur_pos
            self.__large_rect.center = self._pos
            if not self.__large_rect.colliderect(self.__game_rect):
                self._health = -5 # -5 is used so the sound for killing an enemy is not played

    def draw(self, screen): # draw the enemy, polymorphism necessary for blur image
        if self._timer < CROW_PAUSE // 1.5:
            screen.blit(exclamation, self.__exclamation_pos) # only visible for 2/3 of the pause time
        screen.blit(self.__blur_image, self.__blur_rect)
        screen.blit(self._image, self._rect)

#======================Tough Enemy Class======================#
# ground enemy, the fifth enemy the player will see
# similar movement to the default enemy but with less random movement
class ToughEnemy(Enemy):
    def __init__(self, pos, direction):
        super().__init__(pos, TOUGH_ENEMY, tough_enemy_images[direction][0], False)
        self.__direction_change_time = 0
        self.__random_time = 0
        self.__direction = 0
        self.__images = tough_enemy_images

    def __move(self): # return velocities for the enemy based on its direction
        if self.__direction == LEFT:
            velocity_x = -self._speed
            velocity_y = 0
        elif self.__direction == RIGHT:
            velocity_x = self._speed
            velocity_y = 0
        elif self.__direction == UP:
            velocity_x = 0
            velocity_y = -self._speed
        elif self.__direction == DOWN:
            velocity_x = 0
            velocity_y = self._speed
        return velocity_x, velocity_y
    
    def __change_direction(self, player_pos): # check for and change the direction of the enemy
        x_distance = player_pos[X] - self._pos[X]
        y_distance = player_pos[Y] - self._pos[Y]
        if abs(x_distance) > abs(y_distance):
            if x_distance < 0:
                self.__direction = LEFT
            else:
                self.__direction = RIGHT
        else:
            if y_distance < 0:
                self.__direction = UP
            else:
                self.__direction = DOWN
        self.__direction_change_time = self._timer

        if 2*EIGHT_PIXELS < (x_distance**2 + y_distance**2)**0.5 < 8*EIGHT_PIXELS:
            self.__random_time = randint(20,80) # random time before next direction check between 20 and 80 frames
            random_int = randint(-1,7) # 2/7 chance to move randomly
            if random_int <= 1:
                self.__direction = (self.__direction + random_int) % 4

    def __check_collisions(self, velocity_x, velocity_y, game_rect, collidables, enemy_rects):
        collision = False

        if self._rect.collidelistall(collidables):
            collision = True
            
        if ((self._rect.left <= game_rect.left and velocity_x < 0) 
                or (self._rect.top <= game_rect.top and velocity_y < 0) 
                or (self._rect.right >= game_rect.right and velocity_x > 0) 
                or (self._rect.bottom >= game_rect.bottom and velocity_y > 0)):
            collision = True
            
        enemy_rects.remove(self._rect)
        if self._rect.collidelistall(enemy_rects):
            collision = True

        if collision:
            self._pos = self._prev_pos.copy()
            self._rect.center = self._pos
            self.__random_time = 5 # reduce random time if colliding
        
    def update(self, player_pos, game_rect, collidables, enemy_rects, player2_pos=None):
        if player2_pos: # check who is closest
            if player_pos:
                player1_distance = ((player_pos[X] - self._pos[X])**2 + (player_pos[Y] - self._pos[Y])**2)**0.5  
            else:
                player1_distance = GAME_WIDTH*EIGHT_PIXELS # arbitrarily large
            player2_distance = ((player2_pos[X] - self._pos[X])**2 + (player2_pos[Y] - self._pos[Y])**2)**0.5
            if player2_distance <= player1_distance:
                player_pos = player2_pos

        self._timer += 1

        if player_pos:
            if self._timer - self.__direction_change_time > self.__random_time:
                self.__change_direction(player_pos)
            velocity_x, velocity_y = self.__move()
            self._image = self.__images[self.__direction][trunc(((self._timer * 3)/FPS) % len(self.__images[0]))] # 3 animation frames per second
            self._prev_pos = self._pos.copy()
            self._pos += (velocity_x, velocity_y)
            self._rect.center = self._pos
            self.__check_collisions(velocity_x, velocity_y, game_rect, collidables, enemy_rects)

#======================Spirit Enemy Class======================#
# flying enemy, the sixth and final enemy the player will see
# similar movement to the flying enemy but without the sinusoidal speed
class SpiritEnemy(Enemy):
    def __init__(self, pos, direction):
        super().__init__(pos, SPIRIT_ENEMY, spirit_enemy_images[direction], True)
        self.__images = spirit_enemy_images
        self.__direction = direction

    def __move(self, player_pos): # return velocities for the enemy based on the player position
        velocity_x = 0
        velocity_y = 0
        x_distance = player_pos[X] - self._pos[X]
        y_distance = player_pos[Y] - self._pos[Y]
        distance = (x_distance**2 + y_distance**2)**0.5 # pythagoras
        if distance != 0:
            velocity_x += self._speed * (x_distance / distance) # portion of direction in the x
            velocity_y += self._speed * (y_distance / distance) # portion of direction in the y
        return velocity_x, velocity_y
    
    def __check_direction(self, velocity_x, velocity_y): # alter direction attribute based on velocities
        if abs(velocity_x) > abs(velocity_y) + 0.5: # favour image being up or down
            if velocity_x > 0:
                self.__direction = RIGHT
            else:
                self.__direction = LEFT
        else:
            if velocity_y > 0:
                self.__direction = DOWN
            else:
                self.__direction = UP
    
    def update(self, player_pos, player2_pos=None): # update and move the enemy
        if player2_pos: # check who is closest
            if player_pos:
                player1_distance = ((player_pos[X] - self._pos[X])**2 + (player_pos[Y] - self._pos[Y])**2)**0.5  
            else:
                player1_distance = GAME_WIDTH*EIGHT_PIXELS # arbitrarily large
            player2_distance = ((player2_pos[X] - self._pos[X])**2 + (player2_pos[Y] - self._pos[Y])**2)**0.5
            if player2_distance <= player1_distance:
                player_pos = player2_pos

        self._timer += 1

        if player_pos:
            velocity_x, velocity_y = self.__move(player_pos)
            self.__check_direction(velocity_x, velocity_y)
            self._image = self.__images[self.__direction]
            self._pos += velocity_x, velocity_y
            self._rect.center = self._pos
