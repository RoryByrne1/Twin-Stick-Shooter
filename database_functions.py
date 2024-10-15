from constants import DEFAULT_HEX

def db_create_database(db_cursor, db_connection): # create the database tables
    create_players_table = """CREATE TABLE IF NOT EXISTS Players (username CHAR(4) NOT NULL PRIMARY KEY, 
                                                                  pin CHAR(4) NOT NULL, 
                                                                  custom_character CHAR(60) NOT NULL,
                                                                  games_played INTEGER NOT NULL,
                                                                  enemies_killed INTEGER NOT NULL,
                                                                  bullets_shot INTEGER NOT NULL,
                                                                  items_used INTEGER NOT NULL)"""

    create_single_player_table = """CREATE TABLE IF NOT EXISTS SinglePlayerGames (game_id INTEGER PRIMARY KEY,
                                                                                  score INTEGER NOT NULL,
                                                                                  username CHAR(4) NOT NULL,
                                                                                  FOREIGN KEY (username) REFERENCES Players(username))"""

    create_two_player_table = """CREATE TABLE IF NOT EXISTS TwoPlayerGames (game_id INTEGER PRIMARY KEY,
                                                                            score INTEGER NOT NULL,
                                                                            player1_name CHAR(4) NOT NULL,
                                                                            player2_name CHAR(4) NOT NULL,
                                                                            FOREIGN KEY (player1_name) REFERENCES Players(username),
                                                                            FOREIGN KEY (player2_name) REFERENCES Players(username))"""
    
    db_cursor.execute(create_players_table)
    db_cursor.execute(create_single_player_table)
    db_cursor.execute(create_two_player_table)
    db_connection.commit()

def db_get_1p_highscore(username, db_cursor): # returns the highscore for 1 player games of a user
    highscore = db_cursor.execute("SELECT score FROM SinglePlayerGames WHERE username = ? ORDER BY score DESC", (username, )).fetchone()
    if highscore:
        return highscore[0] # take it out of the tuple
    return 0

def db_get_2p_highscore(username, db_cursor): # returns the highscore for 2 player games of a user
    highscore = db_cursor.execute("SELECT score FROM TwoPlayerGames WHERE player1_name = ? OR player2_name = ? ORDER BY score DESC", (username, username)).fetchone()
    if highscore:
        return highscore[0] # take it out of the tuple
    return 0

def db_get_character(username, db_cursor): # returns the custom character of a user
    return db_cursor.execute("SELECT custom_character FROM Players WHERE username = ?", (username, )).fetchone()[0]

def db_get_stats(username, db_cursor): # returns the statistics of a character
    return db_cursor.execute("SELECT games_played, enemies_killed, bullets_shot, items_used FROM Players WHERE username = ?", (username,)).fetchone()

def db_get_all_usernames(db_cursor): # returns all the usernames in the database in a list
    usernames = []
    rows = db_cursor.execute("SELECT username FROM Players").fetchall()
    for tuple in rows:
        usernames.append(tuple[0])
    return usernames

def db_find_player(username, pin, db_cursor): # checks if the pin for a user is correct
    return db_cursor.execute("SELECT username FROM Players WHERE username = ? and pin = ?", (username, pin)).fetchone()

def db_add_to_stats(username, db_cursor, db_connection, games_played=0, enemies_killed=0, bullets_shot=0, items_used=0): # increases the players stats
    curr_gp, curr_ek, curr_bs, curr_iu = db_get_stats(username, db_cursor)
    db_cursor.execute("UPDATE Players SET games_played = ?, enemies_killed = ?, bullets_shot = ?, items_used = ? WHERE username = ?",(curr_gp + games_played, curr_ek + enemies_killed, curr_bs + bullets_shot, curr_iu + items_used, username))
    db_connection.commit()

def db_set_character(username, character_hex, db_cursor, db_connection): # updates a player's custom character
    db_cursor.execute("UPDATE Players SET custom_character = ? WHERE username = ?", (character_hex, username))
    db_connection.commit()

def db_insert_player(username, pin, db_cursor, db_connection): # adds a new player to the database
    db_cursor.execute("INSERT INTO Players VALUES(?,?,?,?,?,?,?)",(username, pin, DEFAULT_HEX, 0, 0, 0, 0))
    db_connection.commit()

def db_insert_1p_score(username, score, db_cursor, db_connection): # adds a new 1 player score
    db_cursor.execute("INSERT INTO SinglePlayerGames(score, username) VALUES(?, ?)",(score, username))
    db_connection.commit()

def db_insert_2p_score(username1, username2, score, db_cursor, db_connection): # adds a new 2 player score
    db_cursor.execute("INSERT INTO TwoPlayerGames(score, player1_name, player2_name) VALUES(?, ?, ?)",(score, username1, username2))
    db_connection.commit()
