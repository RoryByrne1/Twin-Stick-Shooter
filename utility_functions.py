from math import ceil, log

from pygame import Rect, mask

def create_hex_dictionary(list): # creates a dictionary where each item in the provided list has a hex number associated with it
    bit_depth = ceil(log(len(list), 16)) # bit depth will be the n where the number of data points are greater than 2^(n-1) but less than or equal to 2^n
    key_value_list = []
    for i in range(len(list)):
        key_value = (list[i], hex(i)[2:].zfill(bit_depth))
        key_value_list.append(key_value)
    dictionary = dict(key_value_list)
    return dictionary, bit_depth

def check_index(list, index):
    # checks if an index in a list exists
    try:
        list[index]
        return True
    except IndexError:
        return False

def split(string, part_size):  # splits a string into groups of <part_size>
    list = []
    for i in range(0, len(string), part_size):
        list.append(string[i : i+part_size])
    return list

def get_key(value, dictionary):
    key_list = list(dictionary.keys())
    value_list = list(dictionary.values())
    return key_list[value_list.index(value)]

def clip(image, x, y, width, height):  # clips an image to the rect dimensions provided
    image_copy = image.copy()
    clip_rect = Rect(x, y, width, height)
    image_copy.set_clip(clip_rect)
    clipped_image = image.subsurface(image_copy.get_clip())
    return clipped_image.copy()

def colour_swap(image, old_colour, new_colour):
    colour_mask = mask.from_threshold(image, old_colour, threshold=(1, 1, 1, 255))
    colour_change_surface = colour_mask.to_surface(setcolor=new_colour, unsetcolor=(0, 0, 0, 0))
    image_copy = image.copy()
    image_copy.blit(colour_change_surface, (0, 0))
    return image_copy

def round_to_nearest(x, nearest):
    return nearest * round(x/nearest)

def position_list(first, last): # returns a list of positional strings within the range provided
    if first <= last:
        positions = [str(i) for i in range(first, last+1)]
    else:
        positions = [str(i) for i in range(first, last-1, -1)]
    for i in range(len(positions)):
        match positions[i][-1]:
            case '1':
                if len(positions[i]) > 1:
                    if positions[i][-2] != '1':
                        positions[i] += 'st'
                    else:
                        positions[i] += 'th'
                else:
                    positions[i] += 'st'
            case '2':
                if len(positions[i]) > 1:
                    if positions[i][-2] != '1':
                        positions[i] += 'nd'
                    else:
                        positions[i] += 'th'
                else:
                    positions[i] += 'nd'
            case '3':
                if len(positions[i]) > 1:
                    if positions[i][-2] != '1':
                        positions[i] += 'rd'
                    else:
                        positions[i] += 'th'
                else:
                    positions[i] += 'rd'
            case _:
                positions[i] += 'th'
    return positions
