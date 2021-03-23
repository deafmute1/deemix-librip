# deemix-librip
A python script that pulls artists from your spotify or lastfm accounts and uses deemix to download them.
Allows full access to deemix options via its config.json file. 
You can use _any_ lastfm account as a source (no authentication is needed to access user artists), but login access is required for spotify.

## Install and run  
1. `git clone https://git.ayew.host/deafmute/deemix-librip.git && cd deemix-librip`
3. `pip install -r requirements.txt`
4. `python deemix-librip.py --config` 
5. Modify `./config/config.json` to your desire 
6. `python deemix-librip.py <services>`

## Usage
```
Usage: deemix_librip.py [OPTIONS] SERVICES...

  Supported services values (source of artists to download): lastfm, spotify

Options:
  --config         Generate default config and exit
  --lazy           Run lazy artist match instead of interactive (download all
                   search matches for artists)

  --limit INTEGER  Set maximum number of artists ftech from source (Default:
                   1000)

  --help           Show this message and exit.
```

## deezer2?
The deezer2 folder contains the deezer-python library modified to be in the `deezer2` namespace instead of the `deezer` namespace. 
This is because deezer-py, a dependancy of deemix, also uses that namespace. 
See deezer2/LICENSE for copyright details concerning that folder. 





