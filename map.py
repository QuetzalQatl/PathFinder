import os
import pygame
import math
import json
import logging
from pathlib import Path

class pgeLogger():
#
# logging helper class, for debugging
# self.L(f"logging goes here {a}") 
# function at hand everywhere
#
# chance config at will to create a logger you like
#
    def __init__(self):
        p = Path('.')
        q=p/ 'Logs' / 'log.txt'
        logging.basicConfig(filename=q,
                            filemode='w',
                            format='%(asctime)s,%(msecs)d %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

        self.logger = logging.getLogger('MJS')
        
    def L(self, msg=''):
        self.logger.log(logging.DEBUG, msg) # 10 logging.DEBUG

class pixelNode():
    def __init__(self, pos=(0,0), resistance=0, myDict={}):
        self.pos=pos
        self.posString='h'+str(self.pos[0])+'v'+str(self.pos[1])
        self.resistance=resistance # could do something with this to create 'harder terrain to pass'
        self.connectedTo={}
        self.connectedTo[self.posString]=(0,self.posString)
        self.originalConnections={}
        self.myDict=myDict
        
    def goDeeper(self):
        #L.L()
        #L.L(f'goDeeper {self.posString}')
        #print(self.connectedTo)
        addThis={}
        #L.L(f"self.originalConnections{self.originalConnections}")
        for key in self.originalConnections:
            if not key==self.posString:
                #L.L(f"handling Key {key}")
                distanceAdd=self.originalConnections[key][0]
                compareConnectedTo=self.myDict[key].connectedTo
                #L.L(compareConnectedTo)
                for keyCompare in compareConnectedTo:
                    #L.L(f"handling keyCompare {keyCompare}")
                
                    try:
                        distance, via=self.connectedTo[keyCompare]
                        distanceCompare, viaCompare=compareConnectedTo[keyCompare]
                        distanceCompare=distanceCompare+distanceAdd
                        if distanceCompare<distance:
                            #L.L('distanceCompare is smaller')
                            #L.L(f'{self.posString} handling {key} distanceAdd {distanceAdd}')
                            #L.L(f"keyCompare {keyCompare} compareConnectedTo {compareConnectedTo[keyCompare]}")
                            #L.L(f"distance {distance} via {via}")
                            #L.L(f"distanceCompare {distanceCompare} viaCompare {viaCompare} key {key}")
                            viaCompare=key
                            addThis[keyCompare]=(distanceCompare, viaCompare)
                            #update!
                    except:
                        #print ('key did not exist, making new one')
                        distanceCompare, viaCompare=compareConnectedTo[keyCompare]
                        #L.L(f"distanceCompare {distanceCompare} viaCompare {viaCompare}")
                        viaCompare=key
                        distanceCompare=distanceCompare+distanceAdd
                        #L.L(f"distanceCompare {distanceCompare} viaCompare {viaCompare}")
                        addThis[keyCompare]=(distanceCompare, viaCompare)
                        
        for k in addThis:
            self.connectedTo[k]=addThis[k]
        #L.L(self.connectedTo)    

        

class mapPath():
    def __init__(self, MapSurfacePNGname='MapSurface.png'):
        self.L=pgeLogger()
        #L.L('test')
        pygame.init()

        self.MapSurfacePNGname=MapSurfacePNGname
        self.MapSurface = pygame.image.load(os.path.join('data', self.MapSurfacePNGname))
        self.width,self.height=self.MapSurface.get_size()
        
        self.myDict={}
        
        try:
            with open(os.path.join('data', self.MapSurfacePNGname+'PathInfo.json'), 'r') as fp:
                self.saveDict = json.load(fp)
                print('loaded pre calculated info')
        except:
            self.createInfo()
        
    def createInfo(self):
        print('createInfo')
        #count=0
        # create pixelNodes
        for horPos in range (0,self.width):
            for verPos in range (0,self.height):
                colorAtPos=self.MapSurface.get_at((horPos, verPos))
                if not colorAtPos[0]==255: # white = no path
                    self.myDict['h'+str(horPos)+'v'+str(verPos)]=pixelNode((horPos, verPos), colorAtPos[0], self.myDict)
         #           count=count+1
        
        #connect pixels north/south/east/west
        for horPos in range (0,self.width):
            for verPos in range (0,self.height):
                if self.isInDict('h'+str(horPos)+'v'+str(verPos)):
                    d=self.myDict['h'+str(horPos)+'v'+str(verPos)]
                    
                    # check north
                    if verPos>0: # if its 0, its at most north on map, so no need to check
                        verPosCheck=verPos-1
                        if self.isInDict('h'+str(horPos)+'v'+str(verPosCheck)):
                            d.originalConnections['h'+str(horPos)+'v'+str(verPosCheck)]=(1.0, 'h'+str(horPos)+'v'+str(verPosCheck))
                            
                    # check northWest
                    if verPos>0 and horPos>0:
                        verPosCheck=verPos-1
                        horPosCheck=horPos-1
                        if self.isInDict('h'+str(horPosCheck)+'v'+str(verPosCheck)):
                            d.originalConnections['h'+str(horPosCheck)+'v'+str(verPosCheck)]=(math.sqrt(2), 'h'+str(horPosCheck)+'v'+str(verPosCheck))
                    
                    # check west
                    if horPos>0: # if its 0, its at most west on map, so no need to check
                        horPosCheck=horPos-1
                        if self.isInDict('h'+str(horPosCheck)+'v'+str(verPos)):
                            d.originalConnections['h'+str(horPosCheck)+'v'+str(verPos)]=(1.0, 'h'+str(horPosCheck)+'v'+str(verPos))

                    # check southWest
                    if verPos<self.height and horPos>0:
                        verPosCheck=verPos+1
                        horPosCheck=horPos-1
                        if self.isInDict('h'+str(horPosCheck)+'v'+str(verPosCheck)):
                            d.originalConnections['h'+str(horPosCheck)+'v'+str(verPosCheck)]=(math.sqrt(2), 'h'+str(horPosCheck)+'v'+str(verPosCheck))

                    # check south
                    if verPos<self.height: # if its height, its at most south on map, so no need to check
                        verPosCheck=verPos+1
                        if self.isInDict('h'+str(horPos)+'v'+str(verPosCheck)):
                            d.originalConnections['h'+str(horPos)+'v'+str(verPosCheck)]=(1.0, 'h'+str(horPos)+'v'+str(verPosCheck))

                    # check southEast
                    if verPos<self.height and horPos<self.width:
                        verPosCheck=verPos+1
                        horPosCheck=horPos+1
                        if self.isInDict('h'+str(horPosCheck)+'v'+str(verPosCheck)):
                            d.originalConnections['h'+str(horPosCheck)+'v'+str(verPosCheck)]=(math.sqrt(2), 'h'+str(horPosCheck)+'v'+str(verPosCheck))

                    # check east
                    if horPos<self.width: # if its width, its at most east on map, so no need to check
                        horPosCheck=horPos+1
                        if self.isInDict('h'+str(horPosCheck)+'v'+str(verPos)):
                            d.originalConnections['h'+str(horPosCheck)+'v'+str(verPos)]=(1.0, 'h'+str(horPosCheck)+'v'+str(verPos))
                    
                    # check northEast
                    if verPos>0 and horPos<self.width:
                        verPosCheck=verPos-1
                        horPosCheck=horPos+1
                        if self.isInDict('h'+str(horPosCheck)+'v'+str(verPosCheck)):
                            d.originalConnections['h'+str(horPosCheck)+'v'+str(verPosCheck)]=(math.sqrt(2), 'h'+str(horPosCheck)+'v'+str(verPosCheck))

        oldNr=0
        newNr=self.getNumberOfConnectionsKnown()
        # fill each pixel with info:
        iterations=0
        while not oldNr==newNr:
            for horPos in range (0,self.width):
                for verPos in range (0,self.height):
                    if self.isInDict('h'+str(horPos)+'v'+str(verPos)):
                        #print('doing h'+str(horPos)+'v'+str(verPos))
                        self.myDict['h'+str(horPos)+'v'+str(verPos)].goDeeper()
            oldNr=newNr
            newNr=self.getNumberOfConnectionsKnown()
            #L.L()
            #L.L(f"getNumberOfConnectionsKnown={newNr}")
            #L.L()
            iterations=iterations+1
        
        self.saveDict={}

        for horPos in range (0,self.width):
            for verPos in range (0,self.height):
                if self.isInDict('h'+str(horPos)+'v'+str(verPos)):
                    key='h'+str(horPos)+'v'+str(verPos)
                    self.saveDict[key]=self.myDict['h'+str(horPos)+'v'+str(verPos)].connectedTo
            
        #L.L(self.saveDict)
        #os.path.join('data'
        with open(os.path.join('data', self.MapSurfacePNGname+'PathInfo.json'), 'w') as fp:
            json.dump(self.saveDict, fp)
        
    def isInDict(self, someName):
        try:
            d=self.myDict[someName]
        except:
            
            return False
        return True

    def getNumberOfConnectionsKnown(self):
        result=0
        for horPos in range (0,self.width):
            for verPos in range (0,self.height):
                if self.isInDict('h'+str(horPos)+'v'+str(verPos)):
                    #print('h'+str(horPos)+'v'+str(verPos)+':')
                    result=result+len(self.myDict['h'+str(horPos)+'v'+str(verPos)].connectedTo)
        return result
    
    def getPath(self, beginPos, endPos):
        beginPixel='h'+str(beginPos[0])+'v'+str(beginPos[1])
        endPixel='h'+str(endPos[0])+'v'+str(endPos[1])
        
        try: 
            k=self.saveDict[beginPixel]
        except:
            print (f"beginPos {beginPos} is not a path")
            return None
            
        try: 
            t=k[endPixel]
        except:
            print (f"endPos {endPos} cannot be reached from {beginPos}")
            return None
        result=[]
        distance, via=t
        
        #L.L(f"distance {distance}, via {via}")
        result.append((distance, via))
        while distance>0:
            k=self.saveDict[via]
            t=k[endPixel]
            distance, via=t    
            result.append((distance, via))
        
        return result

MapSurfacePNGname='MapSurface.png'
MP=mapPath(MapSurfacePNGname)   

fromPos=(2,1)
toPos=(15,1)
d=MP.getPath(fromPos, toPos)
print(f"path fromPos {fromPos} toPos {toPos}")
if not d is None:
    for i in d:
        print(f"distance: {i[0]} take path: {i[1]}")
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
            


