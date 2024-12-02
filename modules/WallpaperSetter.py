#!/usr/bin/env python
from PIL      import Image
from dateutil import parser
import PIL
import datetime
import hashlib
import magic
import os
import re

class WallpaperSetter:
    def __init__(self, config, database, debug=False):
  
        self.config    = config
        self.database  = database
        self.debug     = debug
        self.directory = re.sub(r'(?<!\\)\$[A-Za-z_][A-Za-z0-9_]*', '', os.path.expandvars(config['directory']))
  
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

