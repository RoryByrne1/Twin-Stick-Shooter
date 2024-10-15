#======================Imports======================#
from sys import exit
from math import trunc
import sqlite3
import json
import pygame

from constants import *
from database_functions import *
from utility_functions import split, colour_swap
from game import Game
from customise_classes import ColourGrid, DrawingGrid
from utility_classes import ImageButton, TextButton, Font, CharacterDisplay, Slider, TextBox
from leaderboard_classes import Leaderboard, TwoPlayerLeaderboard, Podium
from sounds import all_sound_volumes, button_click
from images import (default_front_image2, small_font_image, medium_font_image, big_font_image, huge_font_image, 
                    settings_image, customise_image, return_image, cursor_image, item_images, up_arrow_image)

#======================Loading and Creating the Database======================#
db_connection = sqlite3.connect("testing.db")
db_cursor = db_connection.cursor() 
db_create_database(db_cursor, db_connection) # already handles whether or not the tables exist

#======================Initialising======================#
pygame.init()
pygame.key.set_repeat(500, 100) # pressed keys generate new events every 100 ms after 500 ms
pygame.mixer.set_num_channels(10)
pygame.mouse.set_visible(False)

screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("UNTITLED GUN GAME")
pygame.display.set_icon(default_front_image2)

clock = pygame.time.Clock()

#======================Fonts======================#
small_font = Font(small_font_image, CHARACTER_LIST, WHITE, 2*PIXEL_RATIO)
medium_font = Font(medium_font_image, CHARACTER_LIST_U, WHITE, 5*PIXEL_RATIO)
big_font = Font(big_font_image, CHARACTER_LIST_U, WHITE, 4*PIXEL_RATIO, character_spacing=2*PIXEL_RATIO)
huge_font = Font(huge_font_image, CHARACTER_LIST_U, WHITE, 6*PIXEL_RATIO, character_spacing=2*PIXEL_RATIO)

#======================Quit Function======================#
def quit():
    db_cursor.close()
    db_connection.close()
    pygame.quit()
    exit()

#======================Set Volume Function======================#
def set_volume():
    for sound in all_sound_volumes.keys():
        sound.set_volume(all_sound_volumes[sound] * settings['volume'])

#======================Main Menu function======================#
def main_menu(username):
    one_player_button = TextButton((2*EIGHT_PIXELS, 7.5*EIGHT_PIXELS), (10*EIGHT_PIXELS, 4*EIGHT_PIXELS), "SINGLE"+NEW_LINE+"PLAYER", big_font)
    two_player_button = TextButton((2*EIGHT_PIXELS, 12*EIGHT_PIXELS), (10*EIGHT_PIXELS, 2*EIGHT_PIXELS), "TWO PLAYER", medium_font)
    settings_button = ImageButton((2*EIGHT_PIXELS, 14.5*EIGHT_PIXELS), (2*EIGHT_PIXELS, 2*EIGHT_PIXELS), settings_image)
    customise_button = ImageButton((20.5*EIGHT_PIXELS, 3.5*EIGHT_PIXELS), (2*EIGHT_PIXELS, 2*EIGHT_PIXELS), customise_image)
    leaderboard_button = TextButton((14*EIGHT_PIXELS, 14.5*EIGHT_PIXELS), (8*EIGHT_PIXELS, 2*EIGHT_PIXELS), "LEADERBOARDS"+NEW_LINE+"+ STATISTICS", small_font)
    log_out_button = TextButton((4.5*EIGHT_PIXELS, 14.5*EIGHT_PIXELS), (3.5*EIGHT_PIXELS, 2*EIGHT_PIXELS), "LOG"+NEW_LINE+"OUT", small_font)
    quit_button = TextButton((8.5*EIGHT_PIXELS, 14.5*EIGHT_PIXELS), (3.5*EIGHT_PIXELS, 2*EIGHT_PIXELS), "QUIT", small_font)

    player_character = db_get_character(username, db_cursor)
    character_display = CharacterDisplay((16*EIGHT_PIXELS, 2.5*EIGHT_PIXELS), 4, GRASS_GREEN, player_character, extra_border_colour=CHARACTER_DISPLAY_BORDER)

    leaderboard = Leaderboard(db_cursor, (13*EIGHT_PIXELS, 7.5*EIGHT_PIXELS), 10*EIGHT_PIXELS, small_font, "score", "SinglePlayerGames", "Players", rows=5, record_height=9*PIXEL_RATIO, highlight_key=username)

    title_font_silver = huge_font.new_colour_copy(SILVER)
    title_font_white = huge_font.new_colour_copy(WHITE)
    title_top = 7*PIXEL_RATIO
    title_left = 10*PIXEL_RATIO
    
    mpos = pygame.mouse.get_pos()
    display_mouse = True
    while True:
        click = False # if the user has clicked in the current frame
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                quit() # quit if the user has tried to quit
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
            elif event.type == pygame.KEYDOWN: 
                display_mouse = False # turn the mouse off when the user types

        screen.fill(BACKGROUND_COLOUR)

        previous_mpos = mpos
        mpos = pygame.mouse.get_pos()
        if mpos != previous_mpos:
            display_mouse = True

        # update buttons
        one_player_button.update(mpos, click)
        two_player_button.update(mpos, click)
        settings_button.update(mpos, click)
        customise_button.update(mpos, click)
        leaderboard_button.update(mpos, click)
        quit_button.update(mpos, click)
        log_out_button.update(mpos, click)

        # check buttons
        if one_player_button.get_clicked(): 
            player_character = db_get_character(username, db_cursor)
            highscore = db_get_1p_highscore(username, db_cursor)
            play = True
            while play:
                game_data = game(player_character, highscore)
                if game_data:
                    play = score_screen(username, *game_data, highscore)
                else: # if no game_data, they quit mid_game
                    play = False
            leaderboard.update()
            mpos = pygame.mouse.get_pos() # reset mouse cursor
        
        elif two_player_button.get_clicked():
            username_two = login(title="PLAYER TWO LOGIN:", button_text="START", blocked_names=[username]) # can't login as yourself
            if username_two: # if no username_two, the user pressed return
                player1_character = db_get_character(username, db_cursor)
                player2_character = db_get_character(username_two, db_cursor)
                highscore = db_get_2p_highscore(username, db_cursor)
                play = True
                while play:
                    game_data = game(player1_character, highscore, players=2, player2_hex=player2_character)
                    if game_data:
                        play = score_screen(username, *game_data, highscore, username_two=username_two)
                    else: # if no game_data, they quit mid_game
                        play = False
            mpos = pygame.mouse.get_pos()
        
        elif settings_button.get_clicked():
            settings_screen()
            mpos = pygame.mouse.get_pos()

        elif customise_button.get_clicked():
            player_character = db_get_character(username, db_cursor)
            customise(player_character, username)
            player_character = db_get_character(username, db_cursor)
            character_display.hex_to_grid(player_character) # update character display
            mpos = pygame.mouse.get_pos()

        elif leaderboard_button.get_clicked():
            leaderboards(username)
            mpos = pygame.mouse.get_pos()

        elif log_out_button.get_clicked():
            return
        
        elif quit_button.get_clicked():
            quit()

        # draw everything to the screen
        one_player_button.draw(screen)
        two_player_button.draw(screen)
        settings_button.draw(screen)
        customise_button.draw(screen)
        leaderboard_button.draw(screen)
        quit_button.draw(screen)
        log_out_button.draw(screen)
        
        title_font_silver.render(screen, "UNTITLED"+NEW_LINE+"GUN GAME", (title_left, title_top), alignment=LEFT)
        title_font_white.render(screen, "N", (title_left + 14*PIXEL_RATIO, title_top))
        title_font_white.render(screen, "E", (title_left + 78*PIXEL_RATIO, title_top))
        title_font_white.render(screen, "A", (title_left + 62*PIXEL_RATIO, title_top + 26*PIXEL_RATIO))

        medium_font.render(screen, username, (18*EIGHT_PIXELS, 1*EIGHT_PIXELS), alignment=CENTER)
        character_display.draw(screen)

        leaderboard.draw(screen)

        if not (mpos[X] == 0 or mpos[X] == SCREEN_WIDTH - 1 or mpos[Y] == 0 or mpos[Y] == SCREEN_HEIGHT - 1) and display_mouse:
            screen.blit(cursor_image, mpos)

        pygame.display.update()
        clock.tick(FPS)

#======================Game Function======================#
# for both one and two players
def game(player_hex, highscore, players=1, player2_hex=None):
    game = Game((4*EIGHT_PIXELS, 1*EIGHT_PIXELS), player_hex, FENCE_LIST, players=players, player2_hex=player2_hex) 
    
    if players == 1: # no item storage in 2 player
        item_store_rect = pygame.Rect((1*EIGHT_PIXELS - 2*PIXEL_RATIO, 2*EIGHT_PIXELS - 2*PIXEL_RATIO), (2.5*EIGHT_PIXELS, 2.5*EIGHT_PIXELS))
  
    highscore_font = small_font.new_colour_copy(MINOR_TEXT)

    # for when the game is paused
    pause_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pause_surface.fill(PAUSE_COLOUR)
    pause_settings_button = TextButton((SCREEN_WIDTH//2 - 7.5*EIGHT_PIXELS//2, 8*EIGHT_PIXELS),(7.5*EIGHT_PIXELS, 1.5*EIGHT_PIXELS),"SETTINGS", medium_font, background_colour=None, hover_background_colour=(128, 128, 128, 55))
    pause_exit_button = TextButton((SCREEN_WIDTH//2 - 10.5*EIGHT_PIXELS//2, 9.5*EIGHT_PIXELS),(10.5*EIGHT_PIXELS, 1.5*EIGHT_PIXELS), "EXIT TO MENU", medium_font, background_colour=None, hover_background_colour=(128, 128, 128, 55))
   
    mpos = pygame.mouse.get_pos()
    display_mouse = True
    pause = False
    while True:
        click = False
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
            elif event.type == pygame.KEYDOWN:
                display_mouse = False
                if event.key == pygame.K_ESCAPE:
                    button_click.play()
                    pause = not pause

        screen.fill(BACKGROUND_COLOUR)

        previous_mx_my = (mpos)
        mpos = pygame.mouse.get_pos()
        if not display_mouse and (mpos) != previous_mx_my:
            display_mouse = True
        
        if not pause:
            game.update(event_list)            

        # draw everything to the screen
        game.draw(screen)

        medium_font.render(screen, f"SCORE: {game.get_score()}", (4*EIGHT_PIXELS, 0))
        highscore_font.render(screen, f"HIGHSCORE: {highscore}", (20*EIGHT_PIXELS, 17*EIGHT_PIXELS + 1*PIXEL_RATIO), alignment=RIGHT)

        if players == 1:
            # draw item
            pygame.draw.rect(screen, PALER_BACKGROUND, item_store_rect)
            if game.get_player_item() != None: # can be 0
                screen.blit(pygame.transform.scale_by(item_images[game.get_player_item()], 2), (item_store_rect.centerx - EIGHT_PIXELS, item_store_rect.centery - EIGHT_PIXELS))
            
            # draw lives
            for i in range(0, game.get_player_lives()):
                screen.blit(item_images[HEART], (1*EIGHT_PIXELS + i%2*EIGHT_PIXELS, 4.5*EIGHT_PIXELS + i//2*EIGHT_PIXELS))

            # end the game if the player is dead
            if game.get_player_lives() == 0:
                return game.get_time_score(), game.get_enemy_score(), game.get_enemies_killed(), game.get_bullets_shot(), game.get_items_used()
            
        elif players == 2:
            # draw lives
            player1_lives, player2_lives = game.get_player_lives()
            for i in range(0, player1_lives):
                screen.blit(item_images[HEART], (2.5*EIGHT_PIXELS, 1.5*EIGHT_PIXELS + i*EIGHT_PIXELS))
            for i in range(0, player2_lives):
                screen.blit(item_images[HEART], (20.5*EIGHT_PIXELS, 1.5*EIGHT_PIXELS + i*EIGHT_PIXELS))

            # end the game if both players are dead
            if player1_lives <= 0 and player2_lives <= 0:
                return game.get_time_score(), game.get_enemy_score(), game.get_enemies_killed(), game.get_bullets_shot(), game.get_items_used()

        if pause:
            # update pause-relevant buttons
            pause_exit_button.update(mpos, click)
            pause_settings_button.update(mpos, click)

            # check for pause-relevant button presses
            if pause_settings_button.get_clicked():
                settings_screen(size=False) # can't change screen size in game menu
                mpos = pygame.mouse.get_pos()
            if pause_exit_button.get_clicked():
                return None
                
            # draw pause-relevant things
            screen.blit(pause_surface, (0,0))
            big_font.render(screen, "||"+NEW_LINE+"PAUSED", (SCREEN_WIDTH//2, 4*EIGHT_PIXELS), alignment=CENTER)
            pause_exit_button.draw(screen)
            pause_settings_button.draw(screen)
            
        if not (mpos[X] == 0 or mpos[X] == SCREEN_WIDTH - 1 or mpos[Y] == 0 or mpos[Y] == SCREEN_HEIGHT - 1) and display_mouse:
            screen.blit(cursor_image, mpos)

        pygame.display.update()
        clock.tick(FPS)

#======================Score Screen Function======================#
# and updates the database
def score_screen(username, time_score, enemy_score, enemies_killed, bullets_shot, items_used, highscore, username_two=None):
    score = trunc(time_score) + enemy_score

    # update the database
    if not username_two:
        db_add_to_stats(username, db_cursor, db_connection, games_played=1, enemies_killed=enemies_killed, bullets_shot=bullets_shot, items_used=items_used)
        db_insert_1p_score(username, score, db_cursor, db_connection)
    else:
        db_insert_2p_score(username, username_two, score, db_cursor, db_connection)

    if score > highscore:
        new_highscore = True
        highscore = score
    else:
        new_highscore = False
    
    # time_score counts the seconds
    time_minutes = str(trunc(time_score//60)) 
    time_seconds = str(trunc(time_score%60)).rjust(2, "0")

    highscore_font = small_font.new_colour_copy(MINOR_TEXT)
    right_bound = 12.5*EIGHT_PIXELS # used for positioning

    if not username_two:
        leaderboard = Leaderboard(db_cursor, (14*EIGHT_PIXELS, 5.5*EIGHT_PIXELS), 9*EIGHT_PIXELS, small_font, "score", "SinglePlayerGames", "Players", rows=10, record_height=7*PIXEL_RATIO, highlight_key=username)
        play_again_pos, play_again_size = (1.5*EIGHT_PIXELS, 11.5*EIGHT_PIXELS), (11*EIGHT_PIXELS, 3*EIGHT_PIXELS)
        return_pos, return_size = (2.5*EIGHT_PIXELS, 15*EIGHT_PIXELS), (9*EIGHT_PIXELS, 1.5*EIGHT_PIXELS)
    else:
        leaderboard = TwoPlayerLeaderboard(db_cursor, (3*EIGHT_PIXELS, 12*EIGHT_PIXELS), 18*EIGHT_PIXELS, small_font, "score", "TwoPlayerGames", "Players", rows=5, record_height=7*PIXEL_RATIO, highlight_key=username)
        play_again_pos, play_again_size = (13*EIGHT_PIXELS, 6*EIGHT_PIXELS), (10*EIGHT_PIXELS, 3*EIGHT_PIXELS)
        return_pos, return_size = (13.5*EIGHT_PIXELS, 9.5*EIGHT_PIXELS), (9*EIGHT_PIXELS, 1.5*EIGHT_PIXELS)
    
    play_again_button = TextButton(play_again_pos, play_again_size, "PLAY AGAIN", big_font)
    return_button = TextButton(return_pos, return_size, "RETURN TO MENU", small_font)

    mpos = pygame.mouse.get_pos()
    display_mouse = True
    while True:
        click = False
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
            elif event.type == pygame.KEYDOWN:
                display_mouse = False

        screen.fill(BACKGROUND_COLOUR)

        previous_mx_my = (mpos)
        mpos = pygame.mouse.get_pos()
        if (mpos) != previous_mx_my:
            display_mouse = True

        # update buttons
        play_again_button.update(mpos, click)
        return_button.update(mpos, click)

        # check buttons
        if play_again_button.get_clicked():
            return True
        if return_button.get_clicked():
            return False

        # draw everything to the screen
        big_font.render(screen, f"SCORE:", (EIGHT_PIXELS, EIGHT_PIXELS + 6*PIXEL_RATIO))
        huge_font.render(screen, f"{score}", (7.25*EIGHT_PIXELS, EIGHT_PIXELS))
        highscore_font.render(screen, f"HIGHSCORE: {highscore}", (1*EIGHT_PIXELS, 4.25*EIGHT_PIXELS))
        if new_highscore:
            small_font.render(screen, "NEW HIGHSCORE!", (7.25*EIGHT_PIXELS,3*PIXEL_RATIO))

        small_font.render(screen, f"TIME ALIVE:", (1*EIGHT_PIXELS, 6.5*EIGHT_PIXELS))
        small_font.render(screen, f"{time_minutes}:{time_seconds}", (right_bound, 6.5*EIGHT_PIXELS), alignment=RIGHT)
        small_font.render(screen, f"ENEMIES KILLED:", ((1*EIGHT_PIXELS, 7.5*EIGHT_PIXELS)))
        small_font.render(screen, f"{enemies_killed}", (right_bound, 7.5*EIGHT_PIXELS), alignment=RIGHT)
        small_font.render(screen, f"BULLETS SHOT:", ((1*EIGHT_PIXELS, 8.5*EIGHT_PIXELS)))
        small_font.render(screen, f"{bullets_shot}", (right_bound, 8.5*EIGHT_PIXELS), alignment=RIGHT)
        small_font.render(screen, f"ITEMS USED:", ((1*EIGHT_PIXELS, 9.5*EIGHT_PIXELS)))
        small_font.render(screen, f"{items_used}", (right_bound, 9.5*EIGHT_PIXELS), alignment=RIGHT)

        leaderboard.draw(screen)
        play_again_button.draw(screen)
        return_button.draw(screen)

        if not (mpos[X] == 0 or mpos[X] == SCREEN_WIDTH - 1 or mpos[Y] == 0 or mpos[Y] == SCREEN_HEIGHT - 1) and display_mouse:
            screen.blit(cursor_image, mpos)

        pygame.display.update()
        clock.tick(FPS)

#======================Customisation Function======================#
def customise(character_hex, username):
    # character display that shows the character that the user has saved
    saved_character = CharacterDisplay((4*EIGHT_PIXELS, 1.5*EIGHT_PIXELS), 4, GRASS_GREEN, character_hex, extra_border_colour=CHARACTER_DISPLAY_BORDER) 
    # character display that shows the character that the user is currently customising
    custom_character = CharacterDisplay((2*EIGHT_PIXELS, 7*EIGHT_PIXELS), 8, GRASS_GREEN, character_hex, extra_border_colour=CHARACTER_DISPLAY_BORDER) 

    width = 8
    hat_height = 3

    # splits the hex between the hat and the select grids, select hex split into colours
    hat_hex = character_hex[-COLOUR_DEPTH*hat_height*width:]
    select_hex = split(character_hex[:-COLOUR_DEPTH*hat_height*width], COLOUR_DEPTH) 

    select_x = 12*EIGHT_PIXELS
    select_y = 8*EIGHT_PIXELS

    # creates each colour grid for each body part of the custom character with their initial colours
    skin_select = ColourGrid((select_x, select_y), SKIN_COLOURS, 4, hex_colour=select_hex[0])
    jacket_select = ColourGrid((select_x + 6*EIGHT_PIXELS, select_y), JACKET_COLOURS, 4, hex_colour=select_hex[1])
    shirt_select = ColourGrid((select_x, select_y + 3*EIGHT_PIXELS), SHIRT_COLOURS, 4, hex_colour=select_hex[2])
    trouser_select = ColourGrid((select_x + 6*EIGHT_PIXELS, select_y + 3*EIGHT_PIXELS), TROUSER_COLOURS, 4, hex_colour=select_hex[3])
    eye_select = ColourGrid((select_x + EIGHT_PIXELS, select_y + 6*EIGHT_PIXELS), EYE_COLOURS, 4, hex_colour=select_hex[4], locked_list=[((0,1), db_cursor, username, 'enemies_killed', ENEMY_ACHIEVEMENT)])
    gun_select = ColourGrid((select_x + 7*EIGHT_PIXELS, select_y + 6*EIGHT_PIXELS), GUN_COLOURS, 4, hex_colour=select_hex[5], locked_list=[((0,1), db_cursor, username, 'bullets_shot', BULLET_ACHIEVEMENT)])
    select_grids = [skin_select, jacket_select, shirt_select, trouser_select, eye_select, gun_select]
    select_texts = ["SKIN", "JACKET", "SHIRT", "TROUSERS", "EYES", "GUN"] # text to be displayed

    
    # creates the hat drawing grid with the initial hat hex
    draw_hat_grid = DrawingGrid((13*EIGHT_PIXELS, 3.5*EIGHT_PIXELS), width, hat_height, HAT_COLOURS, initial_hex=hat_hex)

    up_arrow = colour_swap(up_arrow_image, WHITE, PALER_BACKGROUND)

    save_button = TextButton((3*EIGHT_PIXELS, 16*EIGHT_PIXELS), (5.5*EIGHT_PIXELS, 1.5*EIGHT_PIXELS), "SAVE", medium_font, disabled=True)
    return_button = ImageButton((EIGHT_PIXELS//2, EIGHT_PIXELS//2), (2*EIGHT_PIXELS, 2*EIGHT_PIXELS), return_image)

    custom_hex = character_hex

    clicking = False # if the left mouse button is down
    mpos = pygame.mouse.get_pos()
    display_mouse = True
    while True:
        click = False # if the left mouse button has just been pressed in the current frame
        unclick = False # if the left mouse button has just been unpressed in the current frame
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicking = True
                    click = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    clicking = False
                    unclick = True
            elif event.type == pygame.KEYDOWN:
                display_mouse = False

        screen.fill(BACKGROUND_COLOUR)

        previous_mx_my = (mpos)
        mpos = pygame.mouse.get_pos()
        if (mpos) != previous_mx_my:
            display_mouse = True
        
        # update the grids and buttons
        draw_hat_grid.update(mpos, clicking, click, unclick)
        for grid in select_grids:
            grid.update(mpos, click)
        save_button.update(mpos, click)
        return_button.update(mpos, click)

        changed = False

        # if the hat drawing grid has changed, update the hat of the custom character display
        if draw_hat_grid.get_changed():
            changed = True
            custom_character.hat_hex_to_grid(draw_hat_grid.grid_to_hex())
        
        # if a colour grid is changed, update the relevant part of the custom character
        for grid in select_grids:
            if grid.get_changed():
                changed = True
                custom_character.update_pattern(select_grids.index(grid), grid.get_selected().get_colour()) 
        
        if changed:
            custom_hex = "" # create a new empty custom_hex variable
            for grid in select_grids:
                custom_hex += grid.selected_to_hex() # first part of the hex string is the 6 colours representing each part
            custom_hex += draw_hat_grid.grid_to_hex() # second part is the bitmap of the hat grid 

        if character_hex == custom_hex: # if the character is unchanged
            save_button.set_disabled(True)
        else:
            save_button.set_disabled(False)

        if save_button.get_clicked():
            character_hex = custom_hex
            saved_character.hex_to_grid(character_hex) # convert the saved character to the new hex
            db_set_character(username, character_hex, db_cursor, db_connection)
        elif return_button.get_clicked():
            return # no need to return anything as it already updates the dataabse
        
        # draw everything to the screen
        saved_character.draw(screen)
        custom_character.draw(screen)
        screen.blit(up_arrow, (5*EIGHT_PIXELS, 5*EIGHT_PIXELS + 6*PIXEL_RATIO))
        draw_hat_grid.draw(screen)
        medium_font.render(screen, "CUSTOMISATION STUDIO", (12*EIGHT_PIXELS, 1*PIXEL_RATIO), alignment=CENTER)
        for i in range(len(select_grids)):
            grid = select_grids[i] # used multiple times, makes the code shorter and easier to read
            grid.draw_border_rect(screen) # draws a border for the grid
            grid.draw(screen)
            # write the relevant text above each grid
            small_font.render(screen, select_texts[i], (grid.get_rect().centerx,  grid.get_rect().y + EIGHT_PIXELS + 3*PIXEL_RATIO), alignment=CENTER) 
        save_button.draw(screen)
        return_button.draw(screen)

        if not (mpos[X] == 0 or mpos[X] == SCREEN_WIDTH - 1 or mpos[Y] == 0 or mpos[Y] == SCREEN_HEIGHT - 1) and display_mouse:
            screen.blit(cursor_image, mpos)

        pygame.display.update()
        clock.tick(FPS)

#======================Leaderboards and Statistics Function======================#
def leaderboards(username):
    one_player_tab_button = TextButton((3*EIGHT_PIXELS, 1*EIGHT_PIXELS), (4.5*EIGHT_PIXELS, 2*EIGHT_PIXELS), "SINGLE"+NEW_LINE+"PLAYER", small_font, hold=False, pressed=True)
    two_player_tab_button = TextButton((7.5*EIGHT_PIXELS, 1*EIGHT_PIXELS), (4.5*EIGHT_PIXELS, 2*EIGHT_PIXELS), "TWO"+NEW_LINE+"PLAYER", small_font, hold=False)
    stat_podiums_tab_button = TextButton((12*EIGHT_PIXELS, 1*EIGHT_PIXELS), (4.5*EIGHT_PIXELS, 2*EIGHT_PIXELS), "PODIUMS", small_font, hold=False)
    my_stats_tab_button = TextButton((16.5*EIGHT_PIXELS, 1*EIGHT_PIXELS), (4.5*EIGHT_PIXELS, 2*EIGHT_PIXELS), "MY"+NEW_LINE+"STATS", small_font, hold=False)
    return_button = ImageButton((EIGHT_PIXELS//2, EIGHT_PIXELS//2), (2*EIGHT_PIXELS, 2*EIGHT_PIXELS), return_image)

    # single player tab
    one_player_leaderboard = Leaderboard(db_cursor, (3*EIGHT_PIXELS, 3*EIGHT_PIXELS), 18*EIGHT_PIXELS, small_font, "score", "SinglePlayerGames", "Players", rows=10, highlight_key=username, display_characters=True)
    
    # two player tab
    two_player_leaderboard = TwoPlayerLeaderboard(db_cursor, (3*EIGHT_PIXELS, 3*EIGHT_PIXELS), 18*EIGHT_PIXELS, small_font, "score", "TwoPlayerGames", "Players", rows=10, highlight_key=username)

    # podiums tab
    podiums_rect = pygame.Rect((3*EIGHT_PIXELS, 3*EIGHT_PIXELS), (18*EIGHT_PIXELS, 14*EIGHT_PIXELS))
    games_played_rect = pygame.Rect((3*EIGHT_PIXELS, 3*EIGHT_PIXELS), (18*EIGHT_PIXELS, EIGHT_PIXELS + PIXEL_RATIO))
    enemies_killed_rect = pygame.Rect((3*EIGHT_PIXELS, 10*EIGHT_PIXELS), (18*EIGHT_PIXELS, EIGHT_PIXELS + PIXEL_RATIO))
    games_played_podium = Podium(db_cursor, 'games_played', (12*EIGHT_PIXELS, 8.5*EIGHT_PIXELS + PIXEL_RATIO), 2*EIGHT_PIXELS, 3, 2, medium_font, small_font)
    enemies_killed_podium = Podium(db_cursor, 'enemies_killed', (12*EIGHT_PIXELS, 15.5*EIGHT_PIXELS + PIXEL_RATIO), 2*EIGHT_PIXELS, 3, 2, medium_font, small_font)

    # personal statistics tab
    player_stats = db_get_stats(username, db_cursor)
    my_stats_rect = pygame.Rect((3*EIGHT_PIXELS, 3*EIGHT_PIXELS), (18*EIGHT_PIXELS, 4*EIGHT_PIXELS + PIXEL_RATIO))
    my_stats_x = my_stats_rect.left + 2*PIXEL_RATIO
    my_stats_y = my_stats_rect.top + 2*PIXEL_RATIO
    my_stats_spacing = EIGHT_PIXELS

    current_tab = 1
    mpos = pygame.mouse.get_pos()
    display_mouse = True
    while True:
        click = False
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
            elif event.type == pygame.KEYDOWN:
                display_mouse = False

        screen.fill(BACKGROUND_COLOUR)

        previous_mpos = mpos
        mpos = pygame.mouse.get_pos()
        if mpos != previous_mpos:
            display_mouse = True

        # update buttons
        one_player_tab_button.update(mpos, click)
        two_player_tab_button.update(mpos, click)
        stat_podiums_tab_button.update(mpos, click)
        my_stats_tab_button.update(mpos, click)
        return_button.update(mpos, click)

        # check buttons, unpress every other button and swap tabs if a tab button is pressed
        if one_player_tab_button.get_clicked():
            two_player_tab_button.unpress()
            stat_podiums_tab_button.unpress()
            my_stats_tab_button.unpress()
            current_tab = 1
        elif two_player_tab_button.get_clicked():
            one_player_tab_button.unpress()
            stat_podiums_tab_button.unpress()
            my_stats_tab_button.unpress()
            current_tab = 2
        elif stat_podiums_tab_button.get_clicked():
            one_player_tab_button.unpress()
            two_player_tab_button.unpress()
            my_stats_tab_button.unpress()
            current_tab = 3
        elif my_stats_tab_button.get_clicked():
            one_player_tab_button.unpress()
            two_player_tab_button.unpress()
            stat_podiums_tab_button.unpress()
            current_tab = 4
        elif return_button.get_clicked():
            return

        # draw everything to the screen
        one_player_tab_button.draw(screen)
        two_player_tab_button.draw(screen)
        stat_podiums_tab_button.draw(screen)
        my_stats_tab_button.draw(screen)
        return_button.draw(screen)
        
        medium_font.render(screen, "LEADERBOARDS", (12*EIGHT_PIXELS, 0), alignment=CENTER)
        
        match current_tab:
            case 1: # single player leaderboard tab
                one_player_leaderboard.draw(screen)
            case 2: # two player leaderboard tab
                two_player_leaderboard.draw(screen)
            case 3: # podiums tab
                pygame.draw.rect(screen, TEXT_BUTTON_BACKGROUND_COLOUR, podiums_rect)
                pygame.draw.rect(screen, TEXT_BUTTON_HOVER_COLOUR, games_played_rect)
                pygame.draw.rect(screen, TEXT_BUTTON_HOVER_COLOUR, enemies_killed_rect)
                games_played_podium.draw(screen)
                enemies_killed_podium.draw(screen)
                small_font.render(screen, "GAMES PLAYED", (12*EIGHT_PIXELS, 3*EIGHT_PIXELS + 2*PIXEL_RATIO), alignment=CENTER)
                small_font.render(screen, "ENEMIES KILLED", (12*EIGHT_PIXELS, 10*EIGHT_PIXELS + 2*PIXEL_RATIO), alignment=CENTER)
            case 4: # personal stats tab
                pygame.draw.rect(screen, TEXT_BUTTON_HOVER_COLOUR, my_stats_rect)
                small_font.render(screen, "GAMES PLAYED:", (my_stats_x, my_stats_y))
                small_font.render(screen, "ENEMIES KILLED:", (my_stats_x, my_stats_y + my_stats_spacing))
                small_font.render(screen, "BULLETS SHOT:", (my_stats_x, my_stats_y + 2*my_stats_spacing))
                small_font.render(screen, "ITEMS USED:", (my_stats_x, my_stats_y + 3*my_stats_spacing))
                small_font.render(screen, str(player_stats[0]), (my_stats_rect.right - 2*PIXEL_RATIO, my_stats_y), alignment=RIGHT)
                small_font.render(screen, str(player_stats[1]), (my_stats_rect.right - 2*PIXEL_RATIO, my_stats_y + 1*my_stats_spacing), alignment=RIGHT)
                small_font.render(screen, str(player_stats[2]), (my_stats_rect.right - 2*PIXEL_RATIO, my_stats_y + 2*my_stats_spacing), alignment=RIGHT)
                small_font.render(screen, str(player_stats[3]), (my_stats_rect.right - 2*PIXEL_RATIO, my_stats_y + 3*my_stats_spacing), alignment=RIGHT)
                
        if not (mpos[X] == 0 or mpos[X] == SCREEN_WIDTH - 1 or mpos[Y] == 0 or mpos[Y] == SCREEN_HEIGHT - 1) and display_mouse:
            screen.blit(cursor_image, mpos)
            
        pygame.display.update()
        clock.tick(FPS)

#======================Settings Function======================#
def settings_screen(size=True):
    return_button = ImageButton((EIGHT_PIXELS//2, EIGHT_PIXELS//2), (2*EIGHT_PIXELS, 2*EIGHT_PIXELS), return_image)
    save_button = TextButton((SCREEN_WIDTH//2 - 5*EIGHT_PIXELS//2, 12*EIGHT_PIXELS), (5*EIGHT_PIXELS, 1.5*EIGHT_PIXELS), "SAVE", medium_font, disabled=True)
    volume_slider = Slider((SCREEN_WIDTH//2 - 9*EIGHT_PIXELS//2, 6.5*EIGHT_PIXELS), (9*EIGHT_PIXELS, 4*PIXEL_RATIO), 0, 100, settings['volume'] * 100)
    if size:
        size_slider = Slider((SCREEN_WIDTH//2 - 9*EIGHT_PIXELS//2, 10*EIGHT_PIXELS), (9*EIGHT_PIXELS, 4*PIXEL_RATIO), 1, 6, settings['size'])

    mpos = pygame.mouse.get_pos()
    display_mouse = True
    saved = False
    while True:
        click = False
        unclick = False
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    unclick = True
            elif event.type == pygame.KEYDOWN:
                display_mouse = False

        screen.fill(BACKGROUND_COLOUR)

        previous_mx_my = (mpos)
        mpos = pygame.mouse.get_pos()
        if (mpos) != previous_mx_my:
            display_mouse = True

        # update buttons and sliders
        return_button.update(mpos, click)
        save_button.update(mpos, click)
        volume_slider.update(click, unclick, mpos)
        if size:
            size_slider.update(click, unclick, mpos)

        # check if settings have been changed from their initial value
        if round(volume_slider.get_value()) / 100 == settings['volume'] and (not size or (size and round(size_slider.get_value()) == settings['size'])):
            save_button.set_disabled(True)
        else:
            save_button.set_disabled(False)

        # check buttons
        if save_button.get_clicked():
            settings['volume'] = round(volume_slider.get_value()) / 100
            if size:
                settings['size'] = round(size_slider.get_value())

            # overwrite settings on file
            with open("settings.json", "w") as file:
                json.dump(settings, file) 

            saved = False
        elif return_button.get_clicked():
            return
            
        if not saved and not pygame.mixer.get_busy(): # changes only when a sound is not being played
            set_volume()
            saved = True

        # draw everything to the screen
        medium_font.render(screen, "SETTINGS", (SCREEN_WIDTH//2, 3*EIGHT_PIXELS), alignment=CENTER)
        small_font.render(screen, f"VOLUME: {round(volume_slider.get_value())}%", (SCREEN_WIDTH//2, 5*EIGHT_PIXELS), alignment=CENTER)
        if size:
            small_font.render(screen, f"SIZE: {round(size_slider.get_value())}", (SCREEN_WIDTH//2, 8.5*EIGHT_PIXELS), alignment=CENTER)

        return_button.draw(screen)
        save_button.draw(screen)
        volume_slider.draw(screen)
        if size:
            size_slider.draw(screen)

        if not (mpos[X] == 0 or mpos[X] == SCREEN_WIDTH - 1 or mpos[Y] == 0 or mpos[Y] == SCREEN_HEIGHT - 1) and display_mouse:
            screen.blit(cursor_image, mpos)

        pygame.display.update()
        clock.tick(FPS)

#======================Login Function======================#
def login(title="LOGIN:", button_text="LOGIN", blocked_names=[]): # title so that i can use the same function for adding the second player
    valid_names = db_get_all_usernames(db_cursor)

    for name in blocked_names:
        try:
            valid_names.remove(name)
        except ValueError: # blocked name not used by a player
            pass

    name_box = TextBox((SCREEN_WIDTH//2 - 35*PIXEL_RATIO//2, 5*EIGHT_PIXELS), (36*PIXEL_RATIO, 16*PIXEL_RATIO), medium_font, small_font, 4, name="NAME", allowed_strings=valid_names, allowed_characters=UPPER_ALPHABET)
    pin_box = TextBox((SCREEN_WIDTH//2 - 35*PIXEL_RATIO//2, 68*PIXEL_RATIO), (36*PIXEL_RATIO, 16*PIXEL_RATIO), medium_font, small_font, 4, name="PIN", allowed_characters=NUMBERS, hide=True)
    login_button = TextButton((SCREEN_WIDTH//2 - 6*EIGHT_PIXELS//2, 12*EIGHT_PIXELS), (6*EIGHT_PIXELS, 16*PIXEL_RATIO), button_text, medium_font, disabled=True)
    return_button = ImageButton((EIGHT_PIXELS//2, EIGHT_PIXELS//2), (2*EIGHT_PIXELS, 2*EIGHT_PIXELS), return_image)

    mpos = pygame.mouse.get_pos()
    display_mouse = True
    while True:
        click = False
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
            elif event.type == pygame.KEYDOWN:
                display_mouse = False
                
        screen.fill(BACKGROUND_COLOUR)

        previous_mx_my = (mpos)
        mpos = pygame.mouse.get_pos()
        if (mpos) != previous_mx_my:
            display_mouse = True

        # update buttons and text boxes
        name_box.update(mpos, click, event_list)
        pin_box.update(mpos, click, event_list)
        login_button.update(mpos, click)
        return_button.update(mpos, click)

        # if both text boxes have valid inputs, allow the login button to be pressed
        if name_box.get_valid() and pin_box.get_valid():
            login_button.set_disabled(False)
        else:
            login_button.set_disabled(True)

        # check buttons
        if login_button.get_clicked():
            username_tuple = db_find_player(name_box.get_text(), pin_box.get_text(), db_cursor)
            if username_tuple:
                return username_tuple[0]
            else:
                pin_box.display_message("INCORRECT PIN")
        elif return_button.get_clicked():
            return None

        # draw everything to the screen
        medium_font.render(screen, title, (SCREEN_WIDTH//2, 3*EIGHT_PIXELS), alignment=CENTER)
        name_box.draw(screen)
        pin_box.draw(screen)
        login_button.draw(screen)
        return_button.draw(screen)

        if not (mpos[X] == 0 or mpos[X] == SCREEN_WIDTH - 1 or mpos[Y] == 0 or mpos[Y] == SCREEN_HEIGHT - 1) and display_mouse:
            screen.blit(cursor_image, mpos)

        pygame.display.update()
        clock.tick(FPS)

#======================Create Account Function======================#
def create_account():
    taken_names = db_get_all_usernames(db_cursor)

    name_box = TextBox((SCREEN_WIDTH//2 - 35*PIXEL_RATIO//2, 5*EIGHT_PIXELS), (36*PIXEL_RATIO, 16*PIXEL_RATIO), medium_font, small_font, 4, name="NAME", not_allowed_strings=taken_names, allowed_characters=UPPER_ALPHABET)
    pin_box = TextBox((SCREEN_WIDTH//2 - 35*PIXEL_RATIO//2, 68*PIXEL_RATIO), (36*PIXEL_RATIO, 16*PIXEL_RATIO), medium_font, small_font, 4, name="PIN", allowed_characters=NUMBERS, hide=True)
    create_button = TextButton((SCREEN_WIDTH//2 - 6*EIGHT_PIXELS//2, 12*EIGHT_PIXELS), (6*EIGHT_PIXELS, 16*PIXEL_RATIO), "CREATE", medium_font, disabled=True)
    return_button = ImageButton((EIGHT_PIXELS//2, EIGHT_PIXELS//2), (2*EIGHT_PIXELS, 2*EIGHT_PIXELS), return_image)

    mpos = pygame.mouse.get_pos()
    display_mouse = True
    while True:
        click = False
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
            elif event.type == pygame.KEYDOWN:
                display_mouse = False

        screen.fill(BACKGROUND_COLOUR)

        previous_mx_my = (mpos)
        mpos = pygame.mouse.get_pos()
        if (mpos) != previous_mx_my:
            display_mouse = True

        # update buttons and textboxes
        name_box.update(mpos, click, event_list)
        pin_box.update(mpos, click, event_list)
        create_button.update(mpos, click)
        return_button.update(mpos, click)

        # if both text boxes have valid inputs, allow the create account button to be pressed
        if name_box.get_valid() and pin_box.get_valid():
            create_button.set_disabled(False)
        else:
            create_button.set_disabled(True)

        # check buttons
        if create_button.get_clicked():
            db_insert_player(name_box.get_text(), pin_box.get_text(), db_cursor, db_connection)
            return name_box.get_text()
        elif return_button.get_clicked():
            return None
        
        # draw everything to the screen
        medium_font.render(screen, "CREATE ACCOUNT:", (SCREEN_WIDTH//2, 3*EIGHT_PIXELS), alignment=CENTER)
        name_box.draw(screen)
        pin_box.draw(screen)
        create_button.draw(screen)
        return_button.draw(screen)

        if not (mpos[X] == 0 or mpos[X] == SCREEN_WIDTH - 1 or mpos[Y] == 0 or mpos[Y] == SCREEN_HEIGHT - 1) and display_mouse:
            screen.blit(cursor_image, mpos)

        pygame.display.update()
        clock.tick(FPS)
    
#======================Upon-Open Menu function======================#
def open_screen():
    login_button = TextButton((SCREEN_WIDTH//2 - 6*EIGHT_PIXELS//2, 4*EIGHT_PIXELS), (6*EIGHT_PIXELS, 2.25*EIGHT_PIXELS), "LOGIN", medium_font)
    create_account_button = TextButton((SCREEN_WIDTH//2 - 14*EIGHT_PIXELS//2, 8*EIGHT_PIXELS), (14*EIGHT_PIXELS, 2.25*EIGHT_PIXELS), "CREATE ACCOUNT", medium_font)
    quit_button = TextButton((SCREEN_WIDTH//2 - 5*EIGHT_PIXELS//2, 12*EIGHT_PIXELS), (5*EIGHT_PIXELS, 2.25*EIGHT_PIXELS), "QUIT", medium_font)

    mpos = pygame.mouse.get_pos()
    display_mouse = True
    while True:
        click = False
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
            elif event.type == pygame.KEYDOWN:
                display_mouse = False

        screen.fill(BACKGROUND_COLOUR)

        previous_mx_my = (mpos)
        mpos = pygame.mouse.get_pos()
        if (mpos) != previous_mx_my:
            display_mouse = True

        # update buttons
        login_button.update(mpos, click)
        create_account_button.update(mpos, click)
        quit_button.update(mpos, click)

        # check buttons
        if login_button.get_clicked():
            username = login()
            if username:
                main_menu(username)
        elif create_account_button.get_clicked():
            username = create_account()
            if username:
                main_menu(username)
        elif quit_button.get_clicked():
            quit()

        # draw everything to the screen
        login_button.draw(screen)
        create_account_button.draw(screen)
        quit_button.draw(screen)

        if not (mpos[X] == 0 or mpos[X] == SCREEN_WIDTH - 1 or mpos[Y] == 0 or mpos[Y] == SCREEN_HEIGHT - 1) and display_mouse:
            screen.blit(cursor_image, mpos)

        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    set_volume()
    open_screen()
