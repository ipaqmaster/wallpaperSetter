wallpaperSetter. Made for Cinnamon on Linux Mint but could work elsewhere when given the tools.

---------------------------------------------------------------
A passive script which changes wallpapers based on the configured wallpaper directory. I've realized I don't want to lose it.

This script can be called at any time by human or cron to keep things fresh. Invoking it changes your wallpapers based on a configurable variable.

I have this cronjob to run it between 9-5pm quietly:
  0 9-17 * * 1-5 /path/to/wallpaperSetter >/dev/null 2>&1
