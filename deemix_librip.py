#!/usr/bin/env python
# -*- coding: utf-8 -*-
  
# stdlib 
from typing import Generator, List, Iterable, Tuple
from pathlib import Path 
from itertools import chain 

# third arty
import requests
import click 
from deemix.app.cli import cli
from deemix.app.settings import Settings 
import spotipy
from spotipy.oauth2 import SpotifyOAuth 

#internal 
import deezer2 # deezer-python clashes with deezer-py (deemix dependancy) over the deezer namespace. 

@click.command()
@click.option('--lazy', is_flag=True, help="Run lazy artist match instead of interactive (download all search matches for artists)")
@click.option('--lazy-accuracy', help="Under lazy mode, download only the first INTEGER matches", type=int, default=-1)
@click.option('--limit', nargs=1, help="Set maximum number of artists fetch from each source (Default: 500)", type=int, default=500)
@click.argument('sources', nargs=-1, required=True, type=str) 
def main(lazy: bool, lazy_accuracy: int, limit: int, sources: Tuple) -> None:
    """ \b
    Supported SOURCES values (may specify multiple):  
        lastfm      use lastfm as a source of artists  
        spotify     use spotify as a source of artists 
        config      generates a deemix default config at ./config/config.json if file does not exist, and exits. 
    """
    config_path = Path('.').joinpath('config').resolve()
    
    if "config" in sources: 
        Settings(config_path)
        return 

    artist_gens = [] 
    for source in sources: 
        if source.casefold() == 'lastfm'.casefold():
            library = Lastfm(limit)
        if source.casefold() == 'spotify'.casefold(): 
            library = Spotify(limit)
        artist_gens.append(library.artist_names())
    
    click.echo("Now searching deezer for your artists \n")
    dz = Deezer(config_path)
    if lazy: 
        dz.lazy_get_artist_urls(chain.from_iterable(artist_gens), lazy_accuracy)
    else: 
        dz.interactive_get_artist_urls(chain.from_iterable(artist_gens))

    dz.download_artists()
    return 

class Lastfm: 
    def __init__(self, limit: int) -> None:
        api_query = { 
            'method': 'library.getartists', 
            'api_key': click.prompt("Enter a lastfm api key"),
            'user':  click.prompt("Enter lastfm username"),
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
            client_id = click.prompt("Enter a spotify api client id"), 
            client_secret = click.prompt("Enter its matching client secret"),  
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

    def lazy_get_artist_urls(self, artist_iter: Iterable, accuracy: int) -> None:   
        deezer = deezer2.Client()
        for artist in artist_iter: 
            click.echo("\nSearching for {}".format(artist))
            matches = deezer.search(artist, relation='artist')
            
            if len(matches) == 0: 
                click.echo("No matches found")

            if accuracy > 0 and accuracy is not None:  
                matches = matches[:accuracy]

            for artist in matches: 
                self.add_artist(artist) 

    def interactive_get_artist_urls(self, artist_iter: Iterable): 
        deezer = deezer2.Client()
        artist_urls = [] 
        for artist in artist_iter: 
            click.echo("\nSearching for {}".format(artist))
            matches = deezer.search(artist, relation='artist')
            
            if len(matches) == 0: 
                click.echo("No matches found")
                continue

            # if we get an exact match take it and move on 
            if matches[0].name.casefold() == artist.casefold(): 
                click.echo("Exact match found")
                self.add_artist(matches[0]) 
                continue 

            for i, match in enumerate(matches): 
                click.echo("{} {}".format(i, match.name))
            
            index = click.prompt('Enter a index to download corresponding artist (-1 to skip artist, -2 to select multiple artist)', type=int)
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
                    self.add_artist(matches[i]) 
            else:
                self.add_artist(matches[artist_index]) 
       
    def add_artist(self, artist: deezer2.resources.Artist) -> None: 
        if artist.link not in self.artist_urls:
            self.artist_urls.append(artist.link)
            click.echo("Added artist to download list: {}".format(artist.name))

    def download_artists(self) -> None:
        # Calls the cli wrapper around deemix.app.deemix
        # For the most part, we access deemix almost as high level as the interactive user 
        # passing None uses the default path from config/config.json 
        deemix_cli = cli(None, self.config_path) 
        deemix_cli.login() 
        deemix_cli.downloadLink(self.artist_urls, None) # As above, passing None uses bitrate from config.json 
        click.echo("Finished downloading.")

if __name__ == "__main__" : 
    main() 
