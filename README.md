# About

A wallpaper script for my workstations. It reads a configuration file of preferences and indexes a wallpaper directory for content to display. It may even attempt to display some.

Spanning wallpapers are supported where one matches the total resolution of the graphical environment. Otherwise it sets a wallpaper for each display's native resolution. If none can be found it will do its best to pick something.

Wallpapers are tracked in a sqlite3 database file with their details. By default it attempts to re-scan once a day or manually if requested.

The `original_bash` and `original_dev` branches contain the original shell script for this project. It has since been re-written as Python in late 2024 as I wanted to tidy things up.

# Usage

`./main`

   Scans if needed and sets one or more wallpapers if possible.
   
`--help`

   Spills the beans

`--regen`

   Runs maintenance

`--debug`

   Talks more


## Dependencies
* python-magic
