import re

import numpy as np

# Dictionary of umbrella color terms and which
# color terms apply to which umbrella term
# [NOTE: this will have to be manually updated]
color_mapping = {
    'Blue': ['blue', 'aqua', 'ocean'],
    'Purple': ['purple', 'violet'],
    'Green': ['green', 'emerald', 'glow in the dark'],
    'Yellow': ['yellow', 'gold'],
    'Pink': ['pink'],
    'Red': ['red'],
    'Orange': ['orange', 'tangerine'],
    'White': ['white', 'cream'],
    'Brown': ['brown', 'chestnut'],
    'Clear': ['clear'],
    'Picture Disc': ['picture disc'],
    'Gray': ['gray', 'grey'],
    'Black': ['black']}

def remove_parentheses(series):
    """Removes any parentheses/digits (e.g. '(27)') from artist's name.

    Discogs automatically adds numerals to some artist names to 
    differentiate them from artists/labels/etc with the same name;
    this function splits the string at the ' (' mark and only keeps 
    what's before.
    """
    series = series.apply(lambda list: [s.split(' (')[0] for s in list])
    return series

def find_region(series):
    """Converts the country string to a list of countries/regions."""
    series = series.apply(lambda s: re.split(r',|&', s) if re.search(r',|&', s) else [s])
    series = series.apply(lambda s: [string.strip() for string in s])
    series = series.apply(lambda s: ['USA' if string == 'US' else string for string in s])
    return series

def check_picture_disc(row):
    """Replaces pressing color with 'Picture Disc' when applicable."""
    if 'Picture Disc' in row['description']:
        return 'Picture Disc'
    else:
        return row['pressing']

def map_color(series):
    '''Takes pressing information, maps to 'color_mapping' dictionary.

       Sometimes pressings have more than one color (e.g. 'Green and Blue Swirl')
       so this function returns 'Multicolor' if more than one dictionary key applies.
    '''
    def assign_new_color(color):
        matched_colors = []
        for key, values in color_mapping.items():
            if any(val.lower() in color.lower() for val in values):
                matched_colors.append(key)
        if len(matched_colors) == 1:
            return matched_colors[0]
        elif len(matched_colors) > 1:
            return 'Multicolor'
        else:
            return 'Black'
    series = series.apply(assign_new_color)
    return series

def find_size(series):
    """Determines size of vinyl (12", 7", or other size) 
    
       Based on items in 'description' list, outputs a new series
    """
    l_12inch = ['LP','12\"']
    l_7inch = ['7\"']

    flag_12 = series.apply(lambda desc: any(item in l_12inch for item in desc))
    flag_7 = series.apply(lambda desc: any(item in l_7inch for item in desc))
    flag_other = np.where((flag_12 == False) & (flag_7 == False), True, False)

    conditions = [(flag_12 == True),
              (flag_7 == True),
              (flag_other == True)]
    sizes = ['12\"', '7\"', 'Other Size']
    calcs = np.select(conditions, sizes)
    return calcs

def find_type(series):
    """Determines type of release based on items in 'description' list.

       Level of priority:
            Record Store Day
            Limited Edition
            Special/Deluxe Edition
            Reissue/Repress
            Standard
    """    
    type = []
    for i in series:
        if 'Record Store Day' in i:
            type.append('Record Store Day')
        elif 'Limited Edition' in i:
            type.append('Limited Edition')
        elif ('Special Edition' in i) or ('Deluxe Edition' in i):
            type.append('Special/Deluxe Edition')
        elif ('Reissue'in i) or ('Repress'in i):
            type.append('Reissue/Repress')
        else:
            type.append('Standard')
    return type

def artist_string(artist_list):
    """Converts the 'artist' list to a string with brackets"""
    final_string = '[' + ', '.join([str(elem) for elem in artist_list]) + ']'
    return final_string

