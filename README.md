# About

A wallpaper script written in Bash. Reads a config file for a Wallpaper directory and uses SQLite to keep track of wallpapers and their resolutions.

Made for the Cinnamon desktop environment though I'm sure other window managers would work too.

# Usage

## Dependencies
* date    (coreutils)
* dirname (coreutils)
* feh
* imagemagick
* logger  (util-linux)
* xrandr  (xorg-xrandr)

## What it does
On first run creates wallpaperSetter.conf. Also scans the wallpaper directory and stores its findings in wallpaperSetter.db. Regenerates this if the database age is either over 24 hours or it rolls an image that isn't found on disk anymore.

The DB holds the relative file path and the resolution of the file (Thanks ImageMagick)

---------------------------------------------------------------

Set random backgrounds automatically from $HOME/Wallpapers (Or another configured directory)
## Invoking it and Args

`./wallpaperSetter`
   Runs. By default tries to pick images that match your native resolution first. If none are found it'll just pick anything.
   (Working directory does not matter)
   
`-regendb/-regen`
   Force refresh the sqlite3 db file.

`-help`
   Spills the beans

`-debug`
   Talks a little more for problem solving purposes
