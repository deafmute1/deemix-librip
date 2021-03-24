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
Usage: deemix_librip.py [OPTIONS] SOURCES...

  Supported SOURCES values (may specify multiple):  
      lastfm      use lastfm as a source of artists  
      spotify     use spotify as a source of artists 
      config      generates a deemix default config at ./config/config.json if file does not exist, and exits. 

Options:
  --lazy                   Run lazy artist match instead of interactive
                           (download all search matches for artists)

  --lazy-accuracy INTEGER  Under lazy mode, download only the first INTEGER
                           matches

  --limit INTEGER          Set maximum number of artists fetch from each
                           source (Default: 500)

  --help                   Show this message and exit.
```

## Unattended usage 
This script for obvious reasons may have a very long runtime. You may want to consider running on a long uptime machine (e.g. a server) in tmux or screen. If you run under `--lazy` mode, the script requires no human intervention _after_ you enter your deezer arl cookie. The script only needs user intervention whilst fetching artists in order to authenticate to the APIs. This processes should not take more then a few minutes.

## Authenticating to APIs. 
For lastfm, you need to generate an api key [here](https://secure.last.fm/login?next=/api/account/create). The required information is public and no further auth is needed. 

For spotify, you need to generate a client id and its corresponding secret [here](https://developer.spotify.com/dashboard/). After creation, go into your created application, select `Edit Settings` and set the redirect uri to `https://example.com`. You will also need to provide access to your account. The script will provide a link to a spotify OAuth login. AFter login, it will redirect you to a URL beinning with "https://example.com". Copy and paste this whole URL into the script when prompted.  

## deezer2?
The deezer2 folder contains the deezer-python library modified to be in the `deezer2` namespace instead of the `deezer` namespace. This is because deezer-py, a dependancy of deemix, also uses that namespace. See deezer2/LICENSE for copyright details concerning that folder. 

## Copyright 
Copyright 2020 deemix-librip
Licensed under the terms of the GPL3 or optionally, any later versions. 

