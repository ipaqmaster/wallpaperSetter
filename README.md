# wallpaperSetter
A local and passive script invoked on X session starting and monitor configuration changes I've realized I don't want to lose.

This script can be called at any time. Invoking it changes your wallpapers based on a set directory inside the script.

I usually bind it to a global hotkey in Cinnamon or run it on graphical session start.

You will need 'xrandr' and 'feh' installed for this to work on its own.

It checks how many monitors you have then fetches {x} new wallpapers to display on them with 'feh'.
