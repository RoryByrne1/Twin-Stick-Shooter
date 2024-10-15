import pygame

from constants import *
from utility_functions import position_list, check_index
from utility_classes import CharacterDisplay

#======================Leaderboard Class======================#
class Leaderboard():
    def __init__(self, db_cursor, pos, width, font, value_field, value_field_table, key_field_table, key_field="username", rows=10, record_height=10*PIXEL_RATIO, highlight_key=None, position_colour=SLIGHT_GREY, display_characters=False, characters_field="custom_character"):
        self._database = db_cursor
        self._value_field_table = value_field_table
        self._value_field = value_field
        self._key_field = key_field
        self._key_field_table = key_field_table
        self.__display_characters = display_characters
        self.__characters_field = characters_field
        self.__highlight_key = highlight_key
        self._rows = rows
        self.__rect = pygame.Rect(pos, (width, record_height*rows + (rows+1)*PIXEL_RATIO))
        
        key_fields = self._fetch_key_fields()

        values = self.__fetch_values()

        if display_characters:
            characters = self.__fetch_custom_characters()
        else:
            characters = None

        positions = position_list(1, rows)
        self.__records = []
        for i in range(len(positions)):
            highlight = False
            if check_index(key_fields, i):
                key_field = key_fields[i][0]
                if highlight_key in key_field:
                    highlight = True
            else:
                key_field = ""
            self.__records.append(LeaderboardRecord((pos[X]+PIXEL_RATIO, pos[Y] + i*record_height + (i+1)*PIXEL_RATIO), (width-2*PIXEL_RATIO, record_height), font, positions[i], key_field, values[i][0] if check_index(values, i) else None, character_hex=characters[i][0] if display_characters and check_index(values, i) else None, position_colour=position_colour, highlight=highlight))

    def _fetch_key_fields(self):
        key_fields_query = f"""SELECT {self._key_field_table}.{self._key_field} 
                               FROM {self._key_field_table}, {self._value_field_table} 
                               WHERE {self._key_field_table}.{self._key_field} = {self._value_field_table}.{self._key_field}
                               ORDER BY {self._value_field_table}.{self._value_field} DESC
                               LIMIT {self._rows}"""
        return self._database.execute(key_fields_query).fetchall()

    def __fetch_values(self):
        values_query = f"""SELECT {self._value_field} 
                           FROM {self._value_field_table}
                           ORDER BY {self._value_field} DESC
                           LIMIT {self._rows}"""
        return self._database.execute(values_query).fetchall()
    
    def __fetch_custom_characters(self):
        characters_query = f"""SELECT {self._key_field_table}.{self.__characters_field} 
                                FROM {self._key_field_table}, {self._value_field_table}
                                WHERE {self._key_field_table}.{self._key_field} = {self._value_field_table}.{self._key_field}
                                ORDER BY {self._value_field_table}.{self._value_field} DESC
                                LIMIT {self._rows}"""
        return self._database.execute(characters_query).fetchall()

    def update(self): # requery all data in the leaderboard
        key_fields = self._fetch_key_fields()
        for i in range(len(self.__records)):
            if check_index(key_fields, i):
                self.__records[i].update_key_field(key_fields[i][0])

        values = self.__fetch_values()
        for i in range(len(self.__records)):
            if check_index(values, i):
                self.__records[i].update_value(values[i][0])

        if self.__display_characters:
            characters = self.__fetch_custom_characters()
            for i in range(len(self.__records)):
                if check_index(characters, i):
                    self.__records[i].update_character_display(characters[i][0])  

        for record in self.__records:
            if self.__highlight_key in record.get_key_field(): 
                record.set_highlight(True)
            else:
                record.set_highlight(False)

    def draw(self, screen):
        pygame.draw.rect(screen, TEXT_BUTTON_HOVER_COLOUR, self.__rect)
        for record in self.__records:
            record.draw(screen)

#======================Two Player Leaderboard Class======================#
class TwoPlayerLeaderboard(Leaderboard):
    def __init__(self, db_cursor, pos, width, font, value_field, value_field_table, key_field_table, key_field="username", key_field1="player1_name", key_field2="player2_name", rows=10, record_height=10*PIXEL_RATIO, highlight_key=None, position_colour=SLIGHT_GREY, display_characters=False, characters_field="custom_character"):
        self._key_field1 = key_field1
        self._key_field2 = key_field2
        super().__init__(db_cursor, pos, width, font, value_field, value_field_table, key_field_table, key_field=key_field, rows=rows, record_height=record_height, highlight_key=highlight_key, position_colour=position_colour, display_characters=display_characters, characters_field=characters_field)

    def _fetch_key_fields(self): # polymorphism
        key_fields1_query = f"""SELECT {self._key_field_table}.{self._key_field} 
                               FROM {self._key_field_table}, {self._value_field_table} 
                               WHERE {self._key_field_table}.{self._key_field} = {self._value_field_table}.{self._key_field1}
                               ORDER BY {self._value_field_table}.{self._value_field} DESC
                               LIMIT {self._rows}"""
        key_fields2_query = f"""SELECT {self._key_field_table}.{self._key_field} 
                               FROM {self._key_field_table}, {self._value_field_table} 
                               WHERE {self._key_field_table}.{self._key_field} = {self._value_field_table}.{self._key_field2}
                               ORDER BY {self._value_field_table}.{self._value_field} DESC
                               LIMIT {self._rows}"""
        fields1 = self._database.execute(key_fields1_query).fetchall()
        fields2 = self._database.execute(key_fields2_query).fetchall()
        key_fields = []
        for i in range(len(fields1)):
            key_fields.append((f"{fields1[i][0]} + {fields2[i][0]}", ))
        return key_fields

#======================Individual Leaderboard Record Class======================#
class LeaderboardRecord():
    def __init__(self, pos, size, font, position, key_field, value, character_hex=None, position_colour=SLIGHT_GREY, highlight=False):
        self.__rect = pygame.Rect(pos, size)
        self.__font = font
        self.__position = position
        self.__position_font = self.__font.new_colour_copy(position_colour)
        self.__position_width = self.__font.get_text_width(position)
        self.__key_field = key_field
        self.__value = value
        self.__highlight = highlight

        match position:
            case '1st':
                display_border = GOLD
            case '2nd':
                display_border = SILVER
            case '3rd':
                display_border = BRONZE
            case _:
                display_border = PALEST_BACKGROUND
        self.__character_display = CharacterDisplay((self.__rect.x + self.__position_width + 4*PIXEL_RATIO, self.__rect.y + (self.__rect.height//2 - 4*PIXEL_RATIO)), 1, GRASS_GREEN, character_hex, extra_border_colour=display_border) if character_hex else None
    
    def set_highlight(self, highlight):
        self.__highlight = highlight

    def get_key_field(self):
        return self.__key_field

    def update_value(self, value):
        self.__value = value
    
    def update_key_field(self, key_field):
        self.__key_field = key_field

    def update_character_display(self, character_hex):
        self.__character_display.hex_to_grid(character_hex)

    def draw(self, screen):
        if self.__highlight:
            pygame.draw.rect(screen, LEADERBOARD_HIGHLIGHT_COLOUR, self.__rect)
            self.__font.render(screen, self.__position, (self.__rect.x + PIXEL_RATIO, self.__rect.y + (self.__rect.height - self.__font.get_height())//2)) # position displayed in white if it is your score
        else:
            pygame.draw.rect(screen, LEADERBOARD_DEFAULT_COLOUR, self.__rect)
            self.__position_font.render(screen, self.__position, (self.__rect.x + PIXEL_RATIO, self.__rect.y + (self.__rect.height - self.__font.get_height())//2))
        self.__font.render(screen, self.__key_field, (self.__rect.x + self.__position_width + 3*PIXEL_RATIO + (EIGHT_PIXELS + 4*PIXEL_RATIO if self.__character_display else 0), self.__rect.y + (self.__rect.height - self.__font.get_height())//2))
        if self.__character_display:
            self.__character_display.draw(screen)
        if self.__value != None: # in case a 0 is achieved
            self.__font.render(screen, str(self.__value), (self.__rect.x + self.__rect.width, self.__rect.y + (self.__rect.height - self.__font.get_height())//2), alignment=RIGHT)

#======================Podium Class======================#
class Podium():
    def __init__(self, db_cursor, field, pos, spacing, pixel_width_1st, pixel_width_others, font_1st, font_others): # pos specifies (center, bottom)
        self.__font_1st = font_1st
        self.__font_others = font_others
        self.__pixel_width_1st = pixel_width_1st
        self.__pixel_width_others = pixel_width_others
        self.__usernames = db_cursor.execute(f"SELECT username FROM Players WHERE {field} > 0 ORDER BY {field} DESC LIMIT 3").fetchall() # could try to generalise it but there is no point, only used twice on the same screen
        custom_characters = db_cursor.execute(f"SELECT custom_character FROM Players WHERE {field} > 0 ORDER BY {field} DESC LIMIT 3").fetchall()
        self.__values = db_cursor.execute(f"SELECT {field} FROM Players WHERE {field} > 0 ORDER BY {field} DESC LIMIT 3").fetchall()
        self.__character_display_1st = CharacterDisplay((pos[X] - (pixel_width_1st/2)*EIGHT_PIXELS, pos[Y] - pixel_width_1st*EIGHT_PIXELS), pixel_width_1st, GOLD, custom_characters[0][0] if check_index(custom_characters, 0) else None)
        self.__character_display_2nd = CharacterDisplay((pos[X] - (pixel_width_1st/2)*EIGHT_PIXELS - spacing - pixel_width_others*EIGHT_PIXELS, pos[Y] - pixel_width_others*EIGHT_PIXELS), pixel_width_others, SILVER, custom_characters[1][0] if check_index(custom_characters, 1) else None)
        self.__character_display_3rd = CharacterDisplay((pos[X] + (pixel_width_1st/2)*EIGHT_PIXELS + spacing, pos[Y] - pixel_width_others*EIGHT_PIXELS), pixel_width_others, BRONZE, custom_characters[2][0] if check_index(custom_characters, 2) else None)
    
    def draw(self, screen):
        self.__character_display_1st.draw(screen)
        self.__character_display_2nd.draw(screen)
        self.__character_display_3rd.draw(screen)
        if check_index(self.__usernames, 0):
            self.__font_1st.render(screen, self.__usernames[0][0], (self.__character_display_1st.get_rect().centerx, self.__character_display_1st.get_rect().top - self.__font_1st.get_height() - (self.__pixel_width_1st-1)*PIXEL_RATIO), alignment=CENTER)
            self.__font_others.render(screen, str(self.__values[0][0]), (self.__character_display_1st.get_rect().centerx, self.__character_display_1st.get_rect().bottom + self.__pixel_width_1st*PIXEL_RATIO), alignment=CENTER)
            if check_index(self.__usernames, 1):
                self.__font_others.render(screen, self.__usernames[1][0], (self.__character_display_2nd.get_rect().centerx, self.__character_display_2nd.get_rect().top - self.__font_others.get_height() - (self.__pixel_width_others-1)*PIXEL_RATIO - PIXEL_RATIO), alignment=CENTER)
                self.__font_others.render(screen, str(self.__values[1][0]), (self.__character_display_2nd.get_rect().centerx, self.__character_display_2nd.get_rect().bottom + self.__pixel_width_others*PIXEL_RATIO), alignment=CENTER)
                if check_index(self.__usernames, 2):
                    self.__font_others.render(screen, self.__usernames[2][0], (self.__character_display_3rd.get_rect().centerx, self.__character_display_3rd.get_rect().top - self.__font_others.get_height() - (self.__pixel_width_others-1)*PIXEL_RATIO - PIXEL_RATIO), alignment=CENTER)
                    self.__font_others.render(screen, str(self.__values[2][0]), (self.__character_display_3rd.get_rect().centerx, self.__character_display_3rd.get_rect().bottom + self.__pixel_width_others*PIXEL_RATIO), alignment=CENTER)
