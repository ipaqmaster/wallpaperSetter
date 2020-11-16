# About

A wallpaper script written in Bash.

Reads a config file generated on first run.
Searches for wallpapers in a directory and makes an sqlite3 database to keep track of their paths and resolution. Updates if over a day old on next run or when manually requested via argument. (Or if it discovers a wallpaper went missing)

Made for the Cinnamon desktop environment though I'm sure most window managers would be fine.

# Usage

`./wallpaperSetter`

   Runs. Tries to pick native resolution wallpapers or a span wallpaper for all monitors by default. If no match it tries all.

`-help`

   Spills the beans

`-regendb/-regen`

   Regenerates the image database for your configured wallpaper dir.

`-debug`

   Makes the script more talkative.


## Dependencies
* awk     (gawk)
* date    (coreutils)
* dirname (coreutils)
* feh
* imagemagick
* logger  (util-linux)
* xrandr  (xorg-xrandr)
