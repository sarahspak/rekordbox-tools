# rekordbox-tools
Tools to make rekordbox less shitty


## Prerequisites  

Install: 
- https://github.com/sarahspak/Tidal-Media-Downloader
```bash
pyenv virtualenv 3.10.11 tidal-dl
pip3 install tidal-dl --upgrade 
source bin/activate
```
- https://github.com/sarahspak/spotify_to_tidal (optional)
```bash
pyenv virtualenv 3.10.11 spotify-to-tidal
pip3 install spotify-to-tidal --upgrade
source bin/activate
```

## How to use

1. If you have a Spotify playlist, first convert it to a Tidal playlist by using the spotify_to_tidal tool. 
```bash
source venv/bin/activate 
python3 sync.py --uri <PLAYLIST_URI_TO_SYNC>
```
2. Then run
```bash
python main.py -l <TIDAL_PLAYLIST_URI> -o <OUTPUT_DIRECTORY>
```


## installing pyrekordbox
requires sqlcipher, which is a PITA to install. 

I ended up cloning the amalgamation and sqlcipher and bringing the sqlite3.c and sqlite3.h files into sqlicipher: 
```bash
brew install openssl 
git clone https://github.com/coleifer/sqlcipher3
git clone https://github.com/geekbrother/sqlcipher-amalgamation

cp sqlcipher-amalgamation/src/sqlite3.[ch] sqlcipher3/
```


Then I ran the following commands from my `sqlcipher3` directory, with the environment for rekordbox-tools activated:
```bash
cd ~/repos/rekordbox-tools/
source venv/bin/activate

cd ~/repos/sqlcipher3/
export CFLAGS="-I/opt/homebrew/opt/openssl@3/include"
export LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl@3/include"
export PKG_CONFIG_PATH="/opt/homebrew/opt/openssl@3/lib/pkgconfig"
python3 setup.py build_static build
python3 setup.py install
```


