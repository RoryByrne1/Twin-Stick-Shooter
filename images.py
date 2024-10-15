from pygame import display, image, transform, mask

from constants import PIXEL_RATIO, SCREEN_SIZE, BACKGROUND_COLOUR, SPIRIT_ENEMY_COLOUR, WHITE
from utility_functions import colour_swap

display.init()
display.set_mode(SCREEN_SIZE)  # display must be initialised and a video mode set for image loading and manipulation

# all images are scaled up by PIXEL_RATIO to ensure a consistent pixel size

#======================Enemies======================#
default_back_image1 = transform.scale_by(image.load("assets/images/enemies/default enemy/goblin_back1.png").convert_alpha(), PIXEL_RATIO)
default_back_image2 = transform.scale_by(image.load("assets/images/enemies/default enemy/goblin_back2.png").convert_alpha(), PIXEL_RATIO)
default_back_image3 = transform.scale_by(image.load("assets/images/enemies/default enemy/goblin_back3.png").convert_alpha(), PIXEL_RATIO)
default_back_image4 = transform.scale_by(image.load("assets/images/enemies/default enemy/goblin_back4.png").convert_alpha(), PIXEL_RATIO)
default_left_image1 = transform.scale_by(image.load("assets/images/enemies/default enemy/goblin_left1.png").convert_alpha(), PIXEL_RATIO)
default_left_image2 = transform.scale_by(image.load("assets/images/enemies/default enemy/goblin_left2.png").convert_alpha(), PIXEL_RATIO)
default_left_image3 = transform.scale_by(image.load("assets/images/enemies/default enemy/goblin_left3.png").convert_alpha(), PIXEL_RATIO)
default_left_image4 = transform.scale_by(image.load("assets/images/enemies/default enemy/goblin_left4.png").convert_alpha(), PIXEL_RATIO)
default_front_image1 = transform.scale_by(image.load("assets/images/enemies/default enemy/goblin_front1.png").convert_alpha(), PIXEL_RATIO)
default_front_image2 = transform.scale_by(image.load("assets/images/enemies/default enemy/goblin_front2.png").convert_alpha(), PIXEL_RATIO)
default_front_image3 = transform.scale_by(image.load("assets/images/enemies/default enemy/goblin_front3.png").convert_alpha(), PIXEL_RATIO)
default_front_image4 = transform.scale_by(image.load("assets/images/enemies/default enemy/goblin_front4.png").convert_alpha(), PIXEL_RATIO)
default_right_image1 = transform.scale_by(image.load("assets/images/enemies/default enemy/goblin_right1.png").convert_alpha(), PIXEL_RATIO)
default_right_image2 = transform.scale_by(image.load("assets/images/enemies/default enemy/goblin_right2.png").convert_alpha(), PIXEL_RATIO)
default_right_image3 = transform.scale_by(image.load("assets/images/enemies/default enemy/goblin_right3.png").convert_alpha(), PIXEL_RATIO)
default_right_image4 = transform.scale_by(image.load("assets/images/enemies/default enemy/goblin_right4.png").convert_alpha(), PIXEL_RATIO)
default_enemy_images = [[default_back_image1,default_back_image2,default_back_image3,default_back_image4],
                        [default_left_image1,default_left_image2,default_left_image3,default_left_image4],
                        [default_front_image1,default_front_image2,default_front_image3,default_front_image4],
                        [default_right_image1,default_right_image2,default_right_image3,default_right_image4]]

fast_up_image1 = transform.scale_by(image.load("assets/images/enemies/fast enemy/mushroom_up1.png").convert_alpha(), PIXEL_RATIO)
fast_up_image2 = transform.scale_by(image.load("assets/images/enemies/fast enemy/mushroom_up2.png").convert_alpha(), PIXEL_RATIO)
fast_left_image1 = transform.scale_by(image.load("assets/images/enemies/fast enemy/mushroom_left1.png").convert_alpha(), PIXEL_RATIO)
fast_left_image2 = transform.scale_by(image.load("assets/images/enemies/fast enemy/mushroom_left2.png").convert_alpha(), PIXEL_RATIO)
fast_down_image1 = transform.scale_by(image.load("assets/images/enemies/fast enemy/mushroom_down1.png").convert_alpha(), PIXEL_RATIO)
fast_down_image2 = transform.scale_by(image.load("assets/images/enemies/fast enemy/mushroom_down2.png").convert_alpha(), PIXEL_RATIO)
fast_right_image1 = transform.scale_by(image.load("assets/images/enemies/fast enemy/mushroom_right1.png").convert_alpha(), PIXEL_RATIO)
fast_right_image2 = transform.scale_by(image.load("assets/images/enemies/fast enemy/mushroom_right2.png").convert_alpha(), PIXEL_RATIO)
fast_enemy_images = [[fast_up_image1,fast_up_image2],
                     [fast_left_image1,fast_left_image2],
                     [fast_down_image1,fast_down_image2],
                     [fast_right_image1,fast_right_image2]]

flying_up_image1 = transform.scale_by(image.load("assets/images/enemies/flying enemy/flying_up1.png").convert_alpha(), PIXEL_RATIO)
flying_up_image2 = transform.scale_by(image.load("assets/images/enemies/flying enemy/flying_up2.png").convert_alpha(), PIXEL_RATIO)
flying_left_image1 = transform.scale_by(image.load("assets/images/enemies/flying enemy/flying_left1.png").convert_alpha(), PIXEL_RATIO)
flying_left_image2 = transform.scale_by(image.load("assets/images/enemies/flying enemy/flying_left2.png").convert_alpha(), PIXEL_RATIO)
flying_down_image1 = transform.scale_by(image.load("assets/images/enemies/flying enemy/flying_down1.png").convert_alpha(), PIXEL_RATIO)
flying_down_image2 = transform.scale_by(image.load("assets/images/enemies/flying enemy/flying_down2.png").convert_alpha(), PIXEL_RATIO)
flying_right_image1 = transform.scale_by(image.load("assets/images/enemies/flying enemy/flying_right1.png").convert_alpha(), PIXEL_RATIO)
flying_right_image2 = transform.scale_by(image.load("assets/images/enemies/flying enemy/flying_right2.png").convert_alpha(), PIXEL_RATIO)
flying_enemy_images = [[flying_up_image1,flying_up_image2],
                       [flying_left_image1,flying_left_image2],
                       [flying_down_image1,flying_down_image2],
                       [flying_right_image1,flying_right_image2]]

crow_up_image = transform.scale_by(image.load("assets/images/enemies/crow enemy/crow_enemy_up.png").convert_alpha(), PIXEL_RATIO)
crow_left_image = transform.scale_by(image.load("assets/images/enemies/crow enemy/crow_enemy_left.png").convert_alpha(), PIXEL_RATIO)
crow_down_image = transform.scale_by(image.load("assets/images/enemies/crow enemy/crow_enemy_down.png").convert_alpha(), PIXEL_RATIO)
crow_right_image = transform.scale_by(image.load("assets/images/enemies/crow enemy/crow_enemy_right.png").convert_alpha(), PIXEL_RATIO)
crow_enemy_images = [crow_up_image, crow_left_image, crow_down_image, crow_right_image]

tough_back_image1 = transform.scale_by(image.load("assets/images/enemies/tough enemy/tough_back1.png").convert_alpha(), PIXEL_RATIO)
tough_back_image2 = transform.scale_by(image.load("assets/images/enemies/tough enemy/tough_back2.png").convert_alpha(), PIXEL_RATIO)
tough_back_image3 = transform.scale_by(image.load("assets/images/enemies/tough enemy/tough_back3.png").convert_alpha(), PIXEL_RATIO)
tough_back_image4 = transform.scale_by(image.load("assets/images/enemies/tough enemy/tough_back4.png").convert_alpha(), PIXEL_RATIO)
tough_left_image1 = transform.scale_by(image.load("assets/images/enemies/tough enemy/tough_left1.png").convert_alpha(), PIXEL_RATIO)
tough_left_image2 = transform.scale_by(image.load("assets/images/enemies/tough enemy/tough_left2.png").convert_alpha(), PIXEL_RATIO)
tough_left_image3 = transform.scale_by(image.load("assets/images/enemies/tough enemy/tough_left3.png").convert_alpha(), PIXEL_RATIO)
tough_left_image4 = transform.scale_by(image.load("assets/images/enemies/tough enemy/tough_left4.png").convert_alpha(), PIXEL_RATIO)
tough_front_image1 = transform.scale_by(image.load("assets/images/enemies/tough enemy/tough_front1.png").convert_alpha(), PIXEL_RATIO)
tough_front_image2 = transform.scale_by(image.load("assets/images/enemies/tough enemy/tough_front2.png").convert_alpha(), PIXEL_RATIO)
tough_front_image3 = transform.scale_by(image.load("assets/images/enemies/tough enemy/tough_front3.png").convert_alpha(), PIXEL_RATIO)
tough_front_image4 = transform.scale_by(image.load("assets/images/enemies/tough enemy/tough_front4.png").convert_alpha(), PIXEL_RATIO)
tough_right_image1 = transform.scale_by(image.load("assets/images/enemies/tough enemy/tough_right1.png").convert_alpha(), PIXEL_RATIO)
tough_right_image2 = transform.scale_by(image.load("assets/images/enemies/tough enemy/tough_right2.png").convert_alpha(), PIXEL_RATIO)
tough_right_image3 = transform.scale_by(image.load("assets/images/enemies/tough enemy/tough_right3.png").convert_alpha(), PIXEL_RATIO)
tough_right_image4 = transform.scale_by(image.load("assets/images/enemies/tough enemy/tough_right4.png").convert_alpha(), PIXEL_RATIO)
tough_enemy_images = [[tough_back_image1,tough_back_image2,tough_back_image3,tough_back_image4],
                        [tough_left_image1,tough_left_image2,tough_left_image3,tough_left_image4],
                        [tough_front_image1,tough_front_image2,tough_front_image3,tough_front_image4],
                        [tough_right_image1,tough_right_image2,tough_right_image3,tough_right_image4]]

spirit_up_image = transform.scale_by(image.load("assets/images/enemies/spirit enemy/spirit_back.png").convert_alpha(), PIXEL_RATIO)
spirit_left_image = transform.scale_by(image.load("assets/images/enemies/spirit enemy/spirit_left.png").convert_alpha(), PIXEL_RATIO)
spirit_down_image = transform.scale_by(image.load("assets/images/enemies/spirit enemy/spirit_front.png").convert_alpha(), PIXEL_RATIO)
spirit_right_image = transform.scale_by(image.load("assets/images/enemies/spirit enemy/spirit_right.png").convert_alpha(), PIXEL_RATIO)
spirit_enemy_images = [spirit_up_image, spirit_left_image, spirit_down_image, spirit_right_image]
for i in range(len(spirit_enemy_images)):
    face_mask = mask.from_threshold(spirit_enemy_images[i], (255,255,255), threshold=(1, 1, 1, 255))
    face = face_mask.to_surface(setcolor=(245,245,245),unsetcolor=(0,0,0,0))
    body_mask = mask.from_threshold(spirit_enemy_images[i], (255,0,0), threshold=(1, 1, 1, 255)) # pixels to be turned transparent are red
    face.blit(body_mask.to_surface(setcolor=((25,0,25,200)), unsetcolor=(0,0,0,0)), (0,0))
    spirit_enemy_images[i] = face


#======================Game======================#
white_flowers1_image = transform.scale_by(image.load("assets/images/game/white flowers.png").convert_alpha(), PIXEL_RATIO)
white_flowers2_image = transform.scale_by(image.load("assets/images/game/white flowers2.png").convert_alpha(), PIXEL_RATIO)

grass1_image = transform.scale_by(image.load("assets/images/game/grass.png").convert_alpha(), PIXEL_RATIO)
grass2_image = transform.scale_by(image.load("assets/images/game/grass2.png").convert_alpha(), PIXEL_RATIO)
grass3_image = transform.scale_by(image.load("assets/images/game/grass3.png").convert_alpha(), PIXEL_RATIO)

fences_image = transform.scale_by(image.load("assets/images/game/fences.png").convert_alpha(), PIXEL_RATIO)
crate_image = transform.scale_by(image.load("assets/images/game/crate.png").convert_alpha(), PIXEL_RATIO)
bullet_image = transform.scale_by(image.load("assets/images/game/bullet.png").convert_alpha(), PIXEL_RATIO)
exclamation = transform.scale_by(image.load("assets/images/game/exclamation.png").convert_alpha(), PIXEL_RATIO)

#======================Buttons======================#
eraser_image = transform.scale_by(image.load("assets/images/buttons/erase_button.png").convert_alpha(), PIXEL_RATIO)
eraser_image_pressed = transform.scale_by(image.load("assets/images/buttons/erase_button_pressed.png").convert_alpha(), PIXEL_RATIO)
undo_image = transform.scale_by(image.load("assets/images/buttons/undo_button.png").convert_alpha(), PIXEL_RATIO)
redo_image = transform.scale_by(image.load("assets/images/buttons/redo_button.png").convert_alpha(), PIXEL_RATIO)
clear_image = transform.scale_by(image.load("assets/images/buttons/clear_button.png").convert_alpha(), PIXEL_RATIO)
return_image = transform.scale_by(image.load("assets/images/buttons/return_button.png").convert_alpha(), PIXEL_RATIO)
settings_image = transform.scale_by(image.load("assets/images/buttons/settings_button.png").convert_alpha(), PIXEL_RATIO)
customise_image = transform.scale_by(image.load("assets/images/buttons/customise_button.png").convert_alpha(), PIXEL_RATIO)

#======================Other======================#
cursor_image = transform.scale_by(image.load("assets/images/other/mouse_cursor.png").convert_alpha(), PIXEL_RATIO)
padlock_image = colour_swap(transform.scale_by(image.load("assets/images/other/padlock.png").convert_alpha(), PIXEL_RATIO), WHITE, BACKGROUND_COLOUR)
down_arrow_image = transform.scale_by(image.load("assets/images/other/down_arrow.png").convert_alpha(), PIXEL_RATIO)
up_arrow_image = transform.flip(down_arrow_image, False, True) # flip in y

#======================Fonts======================#
small_font_image = transform.scale_by(image.load("assets/images/fonts/small_font.png").convert_alpha(), PIXEL_RATIO) # sort and rename font files
medium_font_image = transform.scale_by(image.load("assets/images/fonts/medium_font.png").convert_alpha(), PIXEL_RATIO)
big_font_image = transform.scale_by(image.load("assets/images/fonts/big_big_font.png").convert_alpha(), PIXEL_RATIO)
huge_font_image = transform.scale_by(image.load("assets/images/fonts/massive_font.png").convert_alpha(), PIXEL_RATIO)

#======================Items======================#
bomb_image = transform.scale_by(image.load("assets/images/items/bomb.png").convert_alpha(), PIXEL_RATIO)
shotgun_image = transform.scale_by(image.load("assets/images/items/shotgun.png").convert_alpha(), PIXEL_RATIO)
shoes_image = transform.scale_by(image.load("assets/images/items/shoes.png").convert_alpha(), PIXEL_RATIO)
rapid_fire_image = transform.scale_by(image.load("assets/images/items/rapid_fire.png").convert_alpha(), PIXEL_RATIO)
time_freeze_image = transform.scale_by(image.load("assets/images/items/clock.png").convert_alpha(), PIXEL_RATIO)
backwards_shot_image = transform.scale_by(image.load("assets/images/items/backwards_shot.png").convert_alpha(), PIXEL_RATIO)
heart_image = transform.scale_by(image.load("assets/images/items/heart.png").convert_alpha(), PIXEL_RATIO)

item_images = [bomb_image, shoes_image, rapid_fire_image, shotgun_image, time_freeze_image, backwards_shot_image, heart_image]
