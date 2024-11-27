#!/usr/bin/env python
from PIL      import Image
from dateutil import parser
import PIL
import datetime
import hashlib
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
  
    def updateImageResolution(self,filePath):
        try:
            img           = PIL.Image.open(filePath)
            width, height = img.size
            columns = ["width", "height"]
            values  = [width, height]
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

    def getImageRow(self, filePath):
        return(self.database.execFetchoneDict("select * from wallpapers where path = '%s'" % filePath))
  
    def updateDb(self):
        print("Regenerating the database.")
        print("Scanning for wallpapers in: %s" % self.directory)
  
        now    = datetime.datetime.now()
        nowStr = str(now)
  
        for root, dirs, files in os.walk(self.directory):
            for filename in files:
                filePath = os.path.join(root, filename)
                if 'disabled' in filePath:
                    continue
                else:
                    result = self.getImageRow(filePath)
                    if not result: # Add the image path to the database
                        self.database.query(columns=["path", "added", "seen"], values=[filePath, nowStr, nowStr])
                        result = self.getImageRow(filePath)

                    # Update the last seen value of this file
                    self.database.query(columns=["seen"],
                                        values=[nowStr],
                                        where=[('path', '=', filePath)],
                                        mode='update')
                      
                    if not result['width'] or not result['height']:
                        self.updateImageResolution(filePath)

                    if not result['hash']:
                        self.updateImageHash(filePath)
  
  
                  
                    #columns = ["path", "seen"]
                    #values  = [filePath, nowStr]
                    #self.database.query(columns=columns, values=values)
  
  
  
