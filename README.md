A wallpaper setting script written in Bash.

Made for the Cinnamon desktop environment though I'm sure other window managers wouldn't mind it.

Generates wallpaperSetter.conf & wallpaperSetter.db in its dir during first run.

Updates the db if it's older than 24h in age.

The DB holds the relative file path and the resolution of the file (Thanks ImageMagick)

---------------------------------------------------------------

Set random backgrounds automatically from $HOME/Wallpapers (Or another configured directory)
Usage examples:
./wallpaperSetter (optional extras: -help -debug -regendb/-regen)
