#!/usr/bin/env python
from PIL        import Image
from Xlib       import X, display
from Xlib.ext   import randr
from dateutil   import parser
import PIL
import Xlib.display
import datetime
import hashlib
import magic
import os
import re
import subprocess


class WallpaperSetter:
    def __init__(self, config, database, debug=False):

        self.config    = config
        self.database  = database
        self.debug     = debug
        self.directory = re.sub(r'(?<!\\)\$[A-Za-z_][A-Za-z0-9_]*', '', os.path.expandvars(config['directory']))
        self.dbUpdated = False

        self.display       = Xlib.display.Display()
        self.screenIndex   = self.display.get_default_screen()
        self.defaultScreen = self.display.screen(self.screenIndex)
        self.root          = self.defaultScreen.root

        self.dimensions    = (self.defaultScreen.width_in_pixels,self.defaultScreen.height_in_pixels)

        if self.debug:
            print("Total display dimensions: %sx%s" % (self.dimensions))

        self.monitors = []
        # Enumerate monitors
        for monitor in self.root.xrandr_get_monitors().monitors:
            thisMonitor = {}
            thisMonitor['port']       = self.display.get_atom_name(monitor.name)
            thisMonitor['height']     = monitor.height_in_pixels
            thisMonitor['width']      = monitor.width_in_pixels
            thisMonitor['dimensions'] = "%sx%s" % (thisMonitor['width'], thisMonitor['height'])
            thisMonitor['offsetX']    = monitor.x
            thisMonitor['offsetY']    = monitor.y

            self.monitors.append(thisMonitor)

        if self.debug:
            from pprint import pprint
            pprint(self.monitors)

        # Try to determine our graphical environment through environment variables.
        if 'DESKTOP_SESSION' in os.environ:
            self.DESKTOP_SESSION = os.environ['DESKTOP_SESSION']
        else:
            print('DESKTOP_SESSION variable not set. Do not expect to be able to set wallpapers without this hint.')
            self.DESKTOP_SESSION = None

        # Check if we should update the database


        if self.dbIsStale():
            print('db is stale.')
            self.updateDb()



    def dbIsStale(self):
        if self.debug: print("Checking if the db is stale")
        result = self.database.execFetchone('select seen from wallpapers order by seen desc limit 1')

        if not result:
            return True
        else:
            result = result[0]

        latestUpdate   = parser.parse(result)
        now            = datetime.datetime.now()
        differenceUnix = now.timestamp() - latestUpdate.timestamp()

        if differenceUnix > self.config['dbStaleSeconds']:
            return True
        else:
            return False


    def loadImage(self, filePath):
        self.img       = None
        self.imgHeight = None
        self.imgWidth  = None

        # Allow clearing without opening a new image
        if filePath:
            try:
                self.img                      = PIL.Image.open(filePath)
                self.imgWidth, self.imgHeight = self.img.size
            except:
                print("Failed to open file:\t%s" % filePath)
                return False

            return True

    def updateImageMime(self, filePath):
        mime = magic.from_file(filePath, mime=True)
        if mime:
            columns = ["mime"]
            values  = [mime]
            where   = [('path', '=', filePath)]
            result  = self.database.query(columns=columns, values=values, mode='update', where=where)

    def updateImageResolution(self, filePath):
        if not self.img:
            if not self.loadImage(filePath):
                return False

        try:
            columns = ["width", "height"]
            values  = [self.imgWidth, self.imgHeight]
            where   = [('path', '=', filePath)]
            result  = self.database.query(columns=columns, values=values, mode='update', where=where)
            return result
        except:
            print("Unable to process: %s" % filePath)
            return(False)


    def updateImageHash(self, filePath):
        with open(filePath, "rb") as file:
            hash = hashlib.file_digest(file, "sha1").hexdigest()

            result = self.database.query(columns=["hash"],
                                         values=[hash],
                                         where=[('path', '=', filePath)],
                                         mode='update')
            return result


    def updateImageProfile(self, filePath):
        """Get the dominant color (profile) of an image. Slower without thumbnail"""

        if not self.img:
            if not self.loadImage(filePath):
                return False

        # Make a copy of the image and shrink it for processing.
        thumb = self.img.copy()
        thumb.thumbnail((100,100))

        width, height = thumb.size

        if thumb.mode != 'RGB':
            thumb = thumb.convert('RGB')

        r_total = 0
        g_total = 0
        b_total = 0

        count = 0
        for x in range(0, width):
            for y in range(0, height):
                pixel = thumb.getpixel((x,y))
                # Ignore a potential alpha channel in the fourth position.
                r, g, b = pixel[0], pixel[1], pixel[2]
                r_total += r
                g_total += g
                b_total += b
                count += 1

        profile = "%02x%02x%02x" % (int(r_total/count), int(g_total/count), int(b_total/count))

        result = self.database.query(columns=["profile"],
                                      values=[profile],
                                       where=[('path', '=', filePath)],
                                        mode='update')

        return result

    def getImageRow(self, filePath):
        return(self.database.execFetchoneDict("select * from wallpapers where path = '%s'" % filePath))

    def updateDb(self):
        # Avoid doing this more than once per run.
        if self.dbUpdated:
            return(self.dbUpdated)

        self.dbUpdated = True

        print("Refreshing the database.")
        print("Scanning: %s" % self.directory)

        now    = datetime.datetime.now()
        nowStr = str(now)

        for root, dirs, files in os.walk(self.directory):
            for filename in files:
                self.loadImage(None) # Reset
                filePath = os.path.join(root, filename)
                if 'disabled' in filePath:
                    continue
                else:
                    result = self.getImageRow(filePath)
                    if not result: # Add the image path to the database
                        self.database.query(columns=["path", "added", "seen"],
                                             values=[filePath, nowStr, nowStr])
                        result = self.getImageRow(filePath)

                    # Update the last seen value of this file
                    self.database.query(columns=["seen"],
                                         values=[nowStr],
                                          where=[('path', '=', filePath)],
                                           mode='update')

                    if self.debug:
                        for key in result.keys():
                            if result[key] is None:
                                print(filePath)
                                break

                    if not result['mime']:
                        if self.debug:
                            print("\tGetting mime type...")

                        self.updateImageMime(filePath)

                    if not result['width'] or not result['height']:
                        if self.debug:
                            print("\tGetting dimensions...")

                        self.updateImageResolution(filePath)

                    if not result['hash']:
                        if self.debug:
                            print("\tHashing...")

                        self.updateImageHash(filePath)

                    if not result['profile']:
                        if self.debug:
                            print("\tProfiling...")

                        self.updateImageProfile(filePath)


    def get(self, span=False):
        result = None

        # Try looking for a single image which matches the dimensions of the entire X-screen (all monitors)
        if span:
            query = "select * from wallpapers where width = '%s' and height = '%s' ORDER BY RANDOM() limit 1" % self.dimensions
            result = self.database.execFetchoneDict(query)

        # Otherwise, return an image for each display
        else:
            result = []
            for monitor in self.monitors:
                query = "select * from wallpapers where width = '%s' and height = '%s' ORDER BY RANDOM() limit 1" % (monitor['width'], monitor['height'])
                result.append(self.database.execFetchoneDict(query))


        # Return our findings, if any.
        if not result:
            return False
        else:
            return result

    def set(self, results, mode='scale', span=False):

        if self.DESKTOP_SESSION == 'xfce':
            print('Processing XFCE...')

            # Configure spanning mode and set a wide wallpaper
            if span:
                for monitor in self.monitors:
                    print(monitor)
                    subprocess.check_call(["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor%s/workspace0/image-style" % monitor['port'], "-s", "6"])

                subprocess.check_call(["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor%s/workspace0/last-image" % self.monitors[0]['port'], "-s", results['path']])

            # Otherwise configure each display and set a wallpaper for each of them.
            else:
                for monitor,result in zip(self.monitors, results):
                    if mode   == 'fill':
                        subprocess.check_call(["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor%s/workspace0/image-style" % monitor['port'], "-s", "3"]) # 3 = Stretched
                    elif mode == 'scale':
                        subprocess.check_call(["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor%s/workspace0/image-style" % monitor['port'], "-s", "4"]) # 4 = Stretched

                    # Set a wallpaper for this monitor
                    subprocess.check_call(["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor%s/workspace0/last-image" % monitor['port'], "-s", result['path']])



    def run(self, mode, span=False):
        """Try to get then set one or more backgrounds"""

        results = self.get(span=span)

        self.set(results, mode=mode, span=span)
