A wallpaper setting script written in Bash.

Made for the Cinnamon desktop environment on Linux Mint but could work elsewhere when given the tools.

---------------------------------------------------------------
Designed as a passive script which changes wallpapers based on the configured wallpaper directory and a cronjob.
I've realized I don't want to lose it over installs so here it is.

This script can be called at any time by a global shortcut, by shell or by an automated task to keep your desktop fresh.

I have this cronjob to run it hourly between 9-5pm quietly:
  0 9-17 * * 1-5 /path/to/wallpaperSetter >/dev/null 2>&1
