#!/usr/bin/env python
# -*- coding: utf-8 -*-
  
# stdlib 
from typing import Generator, List, Iterable, Tuple
from pathlib import Path 
from pprint import pprint

# third arty
import requests
import click 
import deemix.app 
import spotipy
from spotipy.oauth2 import SpotifyOAuth 

#internal 
import deezer2 # deezer-python clashes with deezer-py (deemix dependancy) over the deezer namespace. 

@click.command()
@click.option('--config', is_flag=True, help="Generate default config and exit")
@click.option('--lazy', is_flag=True, help="Run lazy artist match instead of interactive (download all search matches for artists)")
@click.option('--limit', nargs=1, help="Set maximum number of artists ftech from source (Default: 1000)", type=int, default=500)
@click.argument('services', nargs=-1, required=True, type=str)
def main(config: bool, lazy: bool, limit: int, services: Tuple[str]) -> None:
    """ Supported services values (source of artists to download): lastfm, spotify 
    """
    config_path = Path('.').joinpath('config').resolve()
    
    if config: 
        deemix.app.Settings(config_path)
        return 
  
    dz = Deezer(config_path)
    if lazy: 
        get_artist_urls = dz.lazy_get_artist_urls
    else: 
        get_artist_urls = dz.interactive_get_artist_urls

    for service in services: 
        if service.casefold() == "lastfm".casefold():
            source = Lastfm(limit) 
            get_artist_urls(source.artist_names())
        elif service.casefold() == "spotify".casefold(): 
            source = Spotify(limit)
            get_artist_urls(source.artist_names())
    dz.download_artists()
    return 

class Lastfm: 
    def __init__(self, limit: int) -> None:
        user = click.prompt("Enter lastfm username")
        api_query = { 
            'method': 'library.getartists', 
            'api_key': 'e7c00c1ca15826ab02784b56578f9e3c',
            'user': user,
            'format': 'json',
            'page': 1 ,
            'limit': limit 
        }
        response = requests.get('https://ws.audioscrobbler.com/2.0/', params = api_query) 
        self.artists = response.json()
         
    def artist_names(self) -> Generator[str, None, None]: 
        for artist in self.artists['artists']['artist']:
            yield artist['name']

class Spotify: 
    def __init__(self, limit: int) -> None: 
        sp = spotipy.Spotify(auth_manager = SpotifyOAuth(
            scope = 'user-follow-read,user-follow-modify',
            client_id = '8a4cc5a6336747e68ca89799cb182c0c', 
            client_secret = '65e1411ad126497fb928add738d4587b', 
            redirect_uri = 'https://example.com',  
            open_browser = True 
        ))
        # as spotify api has a limit of 50 split limit into loops 
        self.artists = sp.current_user_followed_artists(50)['artists']['items']
        for i in range((limit-50)//50): 
            new_artists = sp.current_user_followed_artists(50, self.artists[-1]['id'])['artists']['items'] 
            self.artists.extend(new_artists) 
    
    def artist_names(self) -> Generator[str, None, None]:  
        for artist in self.artists:
            yield artist['name']

class Deezer:
    def __init__(self, config_path: Path) -> None: 
        self.artist_urls = []
        self.config_path = config_path

    def lazy_get_artist_urls(self, artist_iter: Iterable) -> None:   
        deezer = deezer2.Client()
        for artist in artist_iter: 
            click.echo("Searching for {}".format(artist))
            matches = deezer.search(artist, relation='artist')
            for artist in matches: 
                add_artist_url(artist.link) 

    def interactive_get_artist_urls(self, artist_iter: Iterable): 
        deezer = deezer2.Client()
        artist_urls = [] 
        for artist in artist_iter: 
            click.echo("Searching for {}".format(artist))
            matches = deezer.search(artist, relation='artist')
            
            # if we get an exact match take it and move on 
            if matches[0].name.casefold() == artist.casefold(): 
                click.echo("Exact match found, moving on")
                self.add_artist_url(matches[0].link) 
                continue 

            for i, match in enumerate(matches): 
                click.echo("{} {}".format(i, match.name))
            
            index = click.prompt('Enter a index to download corresponding artist (-1 to skip artist, -2 if you wish to select multiple artist)', type=int)
            if index == -1: 
                continue 
            elif index == -2: 
                indexes_inner = []
                index_inner = 0 
                while (index_inner != -1): 
                    index_inner = click.prompt('Enter an index (-1 to exit once finished, -2 to select all)', type=int)
                    if index_inner == -2: 
                        indexes_inner = [i for i in range(len(matches))]
                        break
                    else:  
                        indexes_inner.append(index)         
                for i in indexes_inner: 
                    self.add_artist_url(matches[i].link) 
            else:
                self.add_artist_url(matches[artist_index].link) 
       
    def add_artist_url(self, url: str) -> None: 
        if url not in self.artist_urls: 
            self.artist_urls.append(url)

    def download_artists(self) -> None:
        # Calls the cli wrapper around deemix.app.deemix
        # For the most part, we access deemix almost as high level as the interactive user 
        # passing None uses the default path from config/config.json 
        deemix_cli = app.cli(None, self.config_path) 
        deemix_cli.login() 
        deemix_cli.downloadLink(self.artist_urls, None) # As above, passing None uses bitrate from config.json 
        click.echo("Finished downloading.")


if __name__ == "__main__" : 
    main() 
