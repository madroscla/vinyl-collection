"""Functions pulling and formatting raw API data."""

import discogs_client

from . import config

# Connecting to the API and setting it to my collection
d = discogs_client.Client(config.client_name, user_token=config.api_token)
me = d.identity()

def get_album_year(entry):
    """Pulls the album/single release year from master release.

       Not every entry is under a master release (e.g. there has
       only been one release of an album/single and thus it is its
       own master); in that case, it repeats the entry's release year.
    """
    item = d.release(entry.id)
    if item.master is None:
        return item.year
    else:
        return item.master.year

def get_artist_info(entry, field):
    """Creates a list of either artist names or artist IDs.

       Result depends on given variable 'field.'

       Artists that have names written in different styles (e.g. Japanese)
       sometimes get counted twice, so this also removes any duplicates.
    """
    item = d.release(entry.id)
    artists = []
    match field:
        case 'name':
            for i in item.artists:
                artists.append(i.name)
        case 'id':
            for i in item.artists:
                artists.append(i.id)
        case _:
            artists.append('Error')
    return list(set(artists)) 

def check_pressing(entry):
    """Pulls the 'text' field from the 'formats' list.

       The 'text' field is optional, as they often contain color information
       and standard black pressings don't have color information, so this 
       function catches any potential KeyErrors.
    """
    item = d.release(entry.id)
    if 'text' in item.formats[0]:
        return item.formats[0]['text']
    else:
        return 'Standard Black'

def add_records():
    """Pulls data from API and outputs a list of lists.

       See python3-discogs-client documentation for 
       further details on release data.
    """
    collection = []
    for i in me.collection_folders[0].releases:
        item = d.release(i.id)
        collection.append({
            'id': item.id,
            'title': item.title,
            'year': item.year,
            'album_year': get_album_year(i),
            'country': item.country,
            'artist': get_artist_info(i, 'name'),
            'artist_id': get_artist_info(i, 'id'),
            'format': item.formats[0]['name'],
            'lp_quantity': item.formats[0]['qty'],
            'pressing': check_pressing(i),
            'description': item.formats[0]['descriptions'],
            'genres': item.genres,
            'wants': item.community.want,
            'haves': item.community.have,
            'rating': float(str(item.community.rating)[13:16]),
            'url': item.url
    })
    return collection