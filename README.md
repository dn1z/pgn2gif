# pgn2gif
Generate gifs from pgn files of your chess games.

## Installation
* You need [python 3.6](https://www.python.org/downloads/) or newer installed.
* Clone the repo with `git clone https://github.com/dn1z/pgn2gif`
* In the cloned directory Run
```
pip install -r requirements.txt
```

## Usage
Run `python3.6 pgn2gif.py` with the following options:
```
Usage
    pgn2gif.py [-p | -s | -o]

Options:
    -p, --path          Path to the pgn file/folder
    -s, --speed         Speed of the pieces moving in gif
    -o, --out           Path to the gif output directory
```

__NOTE__

If you choose to run `python3.6 pgn2gif` without any other option then:

* pgn file must be present within the current working directory
* There must be a `gifs` folder present in the current working directory.

## Example

### PGN
```
1. e4 e5 2. Qh5 Ke7 3. Qxe5#
```

## GIF output
<img src="https://media.giphy.com/media/2UtkKmkhBCfv0bXHBk/giphy.gif">
