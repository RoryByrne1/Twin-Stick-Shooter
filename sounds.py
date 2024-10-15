from pygame import mixer

mixer.init()

button_click = mixer.Sound("assets/sounds/button click.wav")
hover_effect = mixer.Sound("assets/sounds/hover effect.wav")

default_shoot = mixer.Sound("assets/sounds/gun sounds/pew sound.wav")
enemy_killed = mixer.Sound("assets/sounds/famitracker/score.wav")
crow_sound = mixer.Sound("assets/sounds/enemy sounds/crow.mp3")
player_hit_sound = mixer.Sound("assets/sounds/famitracker/death3.wav")
player_death_sound = mixer.Sound("assets/sounds/famitracker/death2.wav")
power_up = mixer.Sound("assets/sounds/famitracker/life_up.wav")
crate_thud = mixer.Sound("assets/sounds/thud.wav")
bomb_sound = mixer.Sound("assets/sounds/famitracker/bomb.wav")

item_sounds = [bomb_sound, power_up, power_up, power_up, None, power_up, power_up]

all_sound_volumes = {default_shoot:      0.2,
                     crow_sound:         0.4, 
                     button_click:       0.4, 
                     hover_effect:       0.4, 
                     player_hit_sound:   0.5, 
                     player_death_sound: 0.5, 
                     power_up:          0.5, 
                     enemy_killed:       0.5, 
                     crate_thud:         0.5,
                     bomb_sound:         0.8}
