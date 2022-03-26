import re
from typing import List

from bs4 import BeautifulSoup
import requests


def request_artist_info(
    artist_name: str,
    page: int,
    genius_api_token: str
):
    """
    Get artist object from Genius API
    """
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + genius_api_token}
    search_url = base_url + '/search?per_page=10&page=' + str(page)
    data = {'q': artist_name}
    # Get Genius.com song url's from artist object
    response = requests.get(search_url, data=data, headers=headers)
    return response


def request_song_urls(
    artist_name: str,
    song_cap: int,
    genius_api_token: str,
    exclusion_string: str = None
):
    page = 1
    songs = []

    while True:
        response = request_artist_info(artist_name, page, genius_api_token)
        # Collect up to song_cap song objects from artist
        json = response.json()
        song_info = []
        for hit in json['response']['hits']:
            hit_artist_name = hit['result']['primary_artist']['name'].lower()
            if exclusion_string is not None:
                if exclusion_string in hit_artist_name:
                    continue
            if artist_name.lower() in hit_artist_name:
                song_info.append(hit)

        # Collect song URL's from song objects
        for song in song_info:
            if (len(songs) < song_cap):
                url = song['result']['url']
                songs.append(url)
            
        if (len(songs) == song_cap):
            break
        else:
            page += 1

    print('Found {} songs by {}'.format(len(songs), artist_name))
    return songs


def scrape_song_lyrics(url: str):
    """
    Scrape lyrics from a Genius.com song URL
    """
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics_div = html.find('div', id='lyrics-root')
    if lyrics_div is None:
        return None
    lyrics = lyrics_div.get_text(separator='|', strip=True)
    return lyrics


def clean_song_lyrics(
    lyrics: List[str],
    exlusion_characters: List[str] = ["/", "[", "]", "{", "}", "(", ")", ":", "*", "+"]
):
    lyrics = re.sub(r'[\(\[].*?[\)\]]', '', lyrics)
    lyrics = lyrics.replace('\' ', ' ')
    lyrics = lyrics.split("|")[1:-2]
    
    lyrics = [line[2:] if line[:2] == ', ' else line for line in lyrics]
    lyrics = list(filter(lambda x: x != '', lyrics))
    lyrics = list(filter(lambda x: x != ',', lyrics))
    # exclude lines with special characters:
    for char in exlusion_characters:
        lyrics = list(filter(lambda x: char not in x, lyrics))
    return lyrics
