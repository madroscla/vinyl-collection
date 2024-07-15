"""Functions pulling and formatting raw API data."""

import discogs_client

from . import config
from . import discogs_scrape

# Connecting to the API and setting it to my collection
d = discogs_client.Client(config.client_name, user_token=config.api_token)
me = d.identity()

def get_album_year(item):
    """Pulls the album/single release year from master release.

       Not every entry is under a master release (e.g. there has
       only been one release of an album/single and thus it is its
       own master); in that case, it repeats the entry's release year.
    """
    if item.master is None:
        return item.year
    else:
        return item.master.year

def get_artist_info(item, field):
    """Creates a list of either artist names or artist IDs.

       Result depends on given variable 'field.'

       Artists that have names written in different styles (e.g. Japanese)
       sometimes get counted twice, so this also removes any duplicates.
    """
    artists = []
    match field:
        case 'name':
            for i in item.artists:
                artists.append(i.name.title())
        case 'id':
            for i in item.artists:
                artists.append(i.id)
        case _:
            artists.append('Error')
    return list(set(artists)) 

def get_lp_quantity(item):
    """Calculates the number of LPs in release."""
    lps = 0
    for i in item.formats:
        if i['name'] == 'Vinyl':
            lps += int(i['qty'])
    return lps

def get_pressing_color(item):
    """Pulls the 'text' field from the 'formats' list.

       The 'text' field is optional, as they often contain color information
       and standard black pressings don't have color information, so this 
       function catches any potential KeyErrors.
    """
    color = []
    for i in item.formats:
        x = i.get('text', None)
        if x is not None:
            color.append(i['text'])
            
    if len(color) == 0:
        color.append('Standard Black')
    return color

def add_records():
    """Pulls data from API and outputs a list of lists.

       See python3-discogs-client documentation for 
       further details on release data. Also includes webscraped
       price data from discogs_scrape
    """
    collection = []
    for i in me.collection_folders[0].releases:
        item = d.release(i.id)
        if item.formats[0]['name'] == 'Vinyl':
            prices = discogs_scrape.get_prices(item.url)
            collection.append({
                'id': item.id,
                'title': item.title,
                'pressing_year': item.year,
                'album_year': get_album_year(item),
                'country': item.country,
                'artist': get_artist_info(item, 'name'),
                'artist_id': get_artist_info(item, 'id'),
                'format': item.formats[0]['name'],
                'lp_quantity': get_lp_quantity(item),
                'pressing': get_pressing_color(item),
                'description': item.formats[0]['descriptions'],
                'genres': item.genres,
                'styles': item.styles,
                'wants': item.community.want,
                'haves': item.community.have,
                'rating': float(str(item.community.rating)[13:16]),
                'lowest_sold_usd': prices['low'],
                'median_sold_usd': prices['median'],
                'highest_sold_usd': prices['high'],
                'url': item.url
            })
    return collection