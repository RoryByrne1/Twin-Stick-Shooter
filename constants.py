from utility_functions import create_hex_dictionary, round_to_nearest
import json

#======================Loading Settings======================#
try:
    with open("settings.json", "r") as file:  # open the settings file in read mode
        settings = json.load(file)            # set the settings to the data in the save file
except FileNotFoundError:     
    settings = {'volume' : 0.50, 'size' : 5}               # if no file, create new settings dictionary
    with open("settings.json", "w") as file:  # create new file and put the settings into it
        json.dump(settings, file)

#======================General Constants======================#
BACKGROUND_SIZE = (BACKGROUND_WIDTH, BACKGROUND_HEIGHT) = (192, 144) # 4:3
PIXEL_RATIO = settings['size']
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT) = (PIXEL_RATIO*BACKGROUND_WIDTH, PIXEL_RATIO*BACKGROUND_HEIGHT) # 5 screen pixels per game pixel
EIGHT_PIXELS = 8*PIXEL_RATIO # makes positioning easier to read, comprehend, and change
GAME_WIDTH = 16
GAME_HEIGHT = 16
FPS = 60

UP = 0
LEFT = 1
CENTER = DOWN = 2
RIGHT = 3

X = 0
Y = 1

#======================Player======================#
# all speeds are in terms of FPS and PIXEL_RATIO so will adjust with any changes
PLAYER_SPEED = 0.55 * PIXEL_RATIO * (60/FPS) # * 60 as the speed was found at 60FPS
FIRE_RATE = 0.25 * FPS
BULLET_SPEED = 1.25 * PIXEL_RATIO * (60/FPS)
BULLET_LIFETIME = 5 * FPS

#======================Enemies======================#
DEFAULT_ENEMY = {"HEALTH" : 1,
                 "SPEED"  : 0.24 * PIXEL_RATIO * (60/FPS),
                 "SCORE"  : 10}
FAST_ENEMY = {"HEALTH" : 2,
              "SPEED"  : 0.45 * PIXEL_RATIO * (60/FPS),
              "SCORE"  : 30}
FLYING_ENEMY = {"HEALTH" : 1,
                "SPEED"  : 0.38 * PIXEL_RATIO * (60/FPS),
                "SCORE"  : 20}
CROW_ENEMY = {"HEALTH" : 1,
              "SPEED"  : 1.2 * PIXEL_RATIO * (60/FPS),
              "SCORE"  : 30}
TOUGH_ENEMY = {"HEALTH" : 2,
               "SPEED"  : 0.22 * PIXEL_RATIO * (60/FPS),
               "SCORE"  : 20}
SPIRIT_ENEMY = {"HEALTH" : 3,
                "SPEED"  : 0.28 * PIXEL_RATIO * (60/FPS),
                "SCORE"  : 40}

CROW_PAUSE = 2*FPS
CROW_BLUR_DISTANCE = 2*PIXEL_RATIO

HIT_TIME = int(0.1 * FPS)
SCORE_LENGTH = 0.25*FPS

#======================Enemy Spawning======================#
INDEX_MULTIPLIER = 2.5
DELAY_MULTIPLIER = 1.6
MIN_FRAMES = 12

#======================Items======================#
BOMB = 0
SHOES = 1
RAPID_FIRE = 2
SHOTGUN = 3
TIME_FREEZE = 4
BACKWARDS_SHOT = 5
HEART = 6

SHOES_LENGTH = 8*FPS
RAPID_FIRE_LENGTH = 8*FPS
SHOTGUN_LENGTH = 8*FPS
TIME_FREEZE_LENGTH = 4*FPS
BACKWARDS_SHOT_LENGTH = 8*FPS

ITEM_CHANCE_1P = 10  # one in
ITEM_CHANCE_2P = 8
ITEM_TIME = 6 * FPS
ITEM_COUNTDOWN = FPS//2
ITEM_FLASH_TIME = round_to_nearest(2 * FPS, 9)
SHOE_MULTIPLIER = 1.4
RAPID_FIRE_MULTIPLIER = 0.7**2
SHOTGUN_RATE_MULTIPLIER = 1/0.7
SCREEN_SHAKE_LENGTH = 0.4*FPS
BOMB_RANGE = 7*EIGHT_PIXELS

#======================Achievements======================#
ENEMY_ACHIEVEMENT = 500    # to unlock special eye colour
BULLET_ACHIEVEMENT = 1000  # to unlock special gun colour

#======================Other======================#
BUTTON_PRESSED_DELAY = 2 * FPS

FENCE_LIST = [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,10),(0,11),(0,12),(0,13),(0,14),(0,15),
              (1,0),(1,15),(2,0),(2,15),(3,0),(3,15),(4,0),(4,15),(5,0),(5,15),
              (10,0),(10,15),(11,0),(11,15),(12,0),(12,15),(13,0),(13,15),(14,0),(14,15),
              (15,0),(15,1),(15,2),(15,3),(15,4),(15,5),(15,10),(15,11),(15,12),(15,13),(15,14),(15,15)]

#======================Colours======================#
WHITE = (255,255,255)
CUSTOMISATION_GREY = (220,220,220)
SLIGHT_GREY = (206,205,210)
GREY = (128,128,128)
PALER_GREY = (140,140,140)

BACKGROUND_COLOUR = (34,32,52)
PALISH_BACKGROUND = (50,47,70)
PALISHER_BACKGROUND = (60,57,80)
PALER_BACKGROUND = (70,67,90)
PALER_BACKGROUND2 = (80,77,100)
PALER_BACKGROUND3 = (100,97,120)
EVEN_PALER_BACKGROUND = (110,107,130)
PALEST_BACKGROUND = (160,157,163)

GRASS_GREEN = (146,156,89)
DARK_GREEN = (75,105,47)

SPIRIT_ENEMY_COLOUR = (25,0,25,180)

GOLD = (213,176,56)
SILVER = (192,192,192)
BRONZE = (140,103,33)#(149,112,42)

RED = (240,120,100)#(200,120,100)
AMBER = (220,180,100)
GREEN = (140,200,100)

PAUSE_COLOUR = (128, 128, 128, 110)

MINOR_TEXT = SLIGHT_GREY
SCORE_ALPHA = 235

LOCKED_COLOUR = GREY

BUTTON_ICON_COLOUR = WHITE
BUTTON_ICON_PRESSED_COLOUR = SLIGHT_GREY
BUTTON_BACKGROUND_COLOUR = BACKGROUND_COLOUR
BUTTON_HOVER_COLOUR = PALISH_BACKGROUND
BUTTON_DISABLED_COLOUR = PALISH_BACKGROUND

BUTTON_TEXT_COLOUR = WHITE
BUTTON_TEXT_PRESSED_COLOUR = SLIGHT_GREY
BUTTON_TEXT_DISABLED_COLOUR = BACKGROUND_COLOUR
TEXT_BUTTON_BACKGROUND_COLOUR = PALISH_BACKGROUND
TEXT_BUTTON_HOVER_COLOUR = PALISHER_BACKGROUND
TEXT_BOX_BACKGROUND = PALISH_BACKGROUND

CHARACTER_DISPLAY_BORDER = PALER_BACKGROUND

LEADERBOARD_POSITION_COLOUR = SLIGHT_GREY
LEADERBOARD_DEFAULT_COLOUR = PALER_BACKGROUND2
LEADERBOARD_HIGHLIGHT_COLOUR = PALER_BACKGROUND3

#======================Customisation======================#
HAT_COLOURS = [(237,179,120), (87,55,43), (172,50,50), (50,112,139), (232,223,50), (240,240,240), (50,45,50), (20,20,20)]
SKIN_COLOURS = [(238,195,154), (192,140,91), (141,85,36), (87,54,27)]
JACKET_COLOURS = [(102,57,49), (19,16,28), (13,84,104), (37,73,10)]
SHIRT_COLOURS = [(207,150,92), (220,220,220), (223,196,13), (40,40,40)]
TROUSER_COLOURS = [(50,60,57), (23,23,27), (16,52,75), (41,27,21)]
EYE_COLOURS = [(55,32,50), (250,245,127)]
GUN_COLOURS = [(34,32,52),(190,150,0)]
ALL_COLOURS = [None] + HAT_COLOURS + SKIN_COLOURS + JACKET_COLOURS + SHIRT_COLOURS + TROUSER_COLOURS + EYE_COLOURS + GUN_COLOURS

BITMAP_DICTIONARY, COLOUR_DEPTH = create_hex_dictionary(ALL_COLOURS)

# the pixel coordinates for each changeable aspect of the character in each direction
SKIN_FRONT, JACKET_FRONT, SHIRT_FRONT, TROUSER_FRONT, EYE_FRONT, GUN_FRONT = [(2,2),(2,3),(2,4),(2,5),(3,3),(3,4),(4,2),(4,3),(4,4),(4,5),(6,6)], [(5,1),(5,2),(5,5),(5,6),(6,2),(6,5)], [(5,3),(5,4),(6,3),(6,4)], [(7,2),(7,3),(7,4),(7,5)], [(3,2),(3,5)], [(6,1),(7,1)]
FRONT_PATTERNS = [SKIN_FRONT, JACKET_FRONT, SHIRT_FRONT, TROUSER_FRONT, EYE_FRONT, GUN_FRONT]
SKIN_BACK, JACKET_BACK, SHIRT_BACK, TROUSER_BACK, EYE_BACK, GUN_BACK = [(2,2),(2,3),(2,4),(2,5),(3,2),(3,3),(3,4),(3,5),(4,2),(4,3),(4,4),(4,5),(6,1),(6,6)], [(5,1),(5,2),(5,3),(5,4),(5,5),(5,6),(6,2),(6,3),(6,4),(6,5)], [], [(7,2),(7,3),(7,4),(7,5)], [], [(4,6)]
BACK_PATTERNS = [SKIN_BACK, JACKET_BACK, SHIRT_BACK, TROUSER_BACK, EYE_BACK, GUN_BACK]
SKIN_LEFT, JACKET_LEFT, SHIRT_LEFT, TROUSER_LEFT, EYE_LEFT, GUN_LEFT = [(2,2),(2,3),(2,4),(2,5),(3,2),(3,4),(3,5),(4,2),(4,3),(4,4),(4,5),(6,4)], [(5,2),(5,4),(5,5),(6,2),(6,5)], [(5,3),(6,3)], [(7,2),(7,3),(7,4),(7,5)], [(3,3)], [(5,0),(5,1)]
LEFT_PATTERNS = [SKIN_LEFT, JACKET_LEFT, SHIRT_LEFT, TROUSER_LEFT, EYE_LEFT, GUN_LEFT]
SKIN_RIGHT, JACKET_RIGHT, SHIRT_RIGHT, TROUSER_RIGHT, EYE_RIGHT, GUN_RIGHT = [(2,2),(2,3),(2,4),(2,5),(3,2),(3,3),(3,5),(4,2),(4,3),(4,4),(4,5),(6,3)], [(5,2),(5,3),(6,2),(6,5)], [], [(7,2),(7,3),(7,4),(7,5)], [(3,4)], [(5,4),(5,5),(5,6),(6,4)]
RIGHT_PATTERNS = [SKIN_RIGHT, JACKET_RIGHT, SHIRT_RIGHT, TROUSER_RIGHT, EYE_RIGHT, GUN_RIGHT]

#======================Character Sets======================#
UPPER_ALPHABET = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
LOWER_ALPHABET = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
NUMBERS = ['0','1','2','3','4','5','6','7','8','9']
SPECIAL_CHARACTERS = ['.',':','+','?','!','&','hidden','|',"'","%"]
CONTROLS = ["^","_","<",">",";"]
CHARACTER_LIST_U = UPPER_ALPHABET + NUMBERS + SPECIAL_CHARACTERS
CHARACTER_LIST = UPPER_ALPHABET + LOWER_ALPHABET + NUMBERS + SPECIAL_CHARACTERS + CONTROLS
NEW_LINE = '/'

DEFAULT_HEX = "09"+"0d"+"11"+"15"+"19"+"1b"+"00"+"00"+"00"+"00"+"00"+"00"+"00"+"00"+"00"+"00"+"00"+"00"+"00"+"00"+"00"+"00"+"00"+"00"+"00"+"00"+"00"+"00"+"00"+"00"
