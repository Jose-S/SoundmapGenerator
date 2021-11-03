import math
import random
import csv
from collections import namedtuple
from Wiggle import calcWiggle, drawCurvesSequence
from enum import Enum 


class Timbre(Enum):
     ORGANIC = "organic"
     MECHANICAL = "mechanical"
     NONE = "none"

class Pitch(Enum):
     HIGH = "high"
     LOW = "low"
     NONE = "none"

Point = namedtuple('Point', ['x', 'y'])

RAD_60 = math.radians(60)
RAD_120 = math.radians(120)
RAD_240 = math.radians(240)
RAD_300 = math.radians(300)
DEFAULT_STROKE_WIDTH = 3

size(1512, 1512)


########### DRAW PRIMATIVES

def drawPoint(point, color):
    print(point)
    x, y = point
    fill(*color)
    oval(x-2, y-2, 4, 4)

def drawArrow(centerPoint, length, sWidth=2):
    return drawTriangle(centerPoint, length, False, sWidth, False)
    
def drawTriangle(centerPoint, length, isFilled = True, sWidth=2, isClosed=True):
    xC, yC = centerPoint
    # Some Trig used to calculate vertex
    # Tahnks to: https://math.stackexchange.com/questions/1344690/is-it-possible-to-find-the-vertices-of-an-equilateral-triangle-given-its-center
    A = (xC, yC + (math.sqrt(3)/3)*length)
    B = (xC - (length/2), yC - (math.sqrt(3)/6)*length)
    C = (xC + (length/2), yC - (math.sqrt(3)/6)*length)
    
    shape = BezierPath()
        
    if(isFilled):
        fill(0)
        strokeWidth(0)
    else:
        fill(None)
        strokeWidth(sWidth)
    shape.polygon(A, B, C, close=isClosed)
    shape.endPath()
            
    return shape
    
def drawCircle(centerPoint, r, isFilled = True, sWidth=2):
    x, y = centerPoint
    
    shape = BezierPath()
  
    if(isFilled):
        fill(0)
        strokeWidth(0)
    else:
        fill(None)
        strokeWidth(sWidth)
    shape.oval(x-r, y-r, 2*r, 2*r)
    shape.endPath()
     
    return shape

def drawZigZagLine(x, y, length, sWidth = 1, offsetMin = 5, offsetMax = 10, density = 5):
    
    inc = length // density
    
    strokeWidth(sWidth)
    path = BezierPath()
    path.moveTo((x, y))
    for i in range(1,inc):
        # random offset creates less predictable and organic shapes
        offset = random.randint(offsetMin, offsetMax)
        if(i % 2 == 0): 
            path.lineTo((x + offset, y + i*inc))
        else: 
            path.lineTo((x - offset, y + i*inc))
    path.endPath()
    return path
    
def drawWiggleLine(x, y, length, sWidth = 1):
    pt1 = Point(x, y)
    pt2 = Point(x, y + length)
    wigglePoints = calcWiggle(pt1, pt2, 36, 36, .75)
    
    strokeWidth(sWidth)
    path = BezierPath()
    path.moveTo(wigglePoints[0])
    for eachBcpOut, eachBcpIn, eachAnchor in wigglePoints[1:]:
        path.curveTo(eachBcpOut, eachBcpIn, eachAnchor)
    path.endPath()
    
    return path
    
def drawStraightLine(x, y, length, sWidth = 1):
    strokeWidth(sWidth)
    path = BezierPath()
    path.moveTo((x, y))
    path.lineTo((x, y + length))
    path.endPath()
    return path


####### DRAW PATTERNS

def drawLineRepeat(linePath, amount, gap):
    path = BezierPath()
    with savedState():
        for i in range(amount):
            # Could draw
            path.appendPath(linePath)
            path.translate(gap, 0)
    return path

def drawGrid(linePath, amount, gap, centerPoint):
    path = BezierPath()
    with savedState():
        path.appendPath(drawLineRepeat(linePath, amount, gap))
        path.rotate(90,  centerPoint)
        path.appendPath(drawLineRepeat(linePath, amount, gap))    
    return path
    

def drawShapeGrid(shapePath, amount, gap):
    path = BezierPath()
    with savedState():
        for i in range(amount):
            for j in range(amount):
                path.appendPath(shapePath)
                path.translate(gap, 0)
            path.translate(-gap*amount, gap)
        # Reset
        path.translate(gap*(amount-1), -gap*amount)
 
    return path


    
########## DRAW TEXTURES


def drawPitchTexture(pitchType, intensity, width, centerPoint, isFilled = False, sWidth = 1):
    w = width
    # Top Right Corner Point
    gap = width / intensity
    cX, cY = centerPoint
    start = (cX - (w/2 - gap/2), cY + (w/2 - gap/2))
    
    if(pitchType =="high"):
        pitchPath = drawArrow(start, 12, sWidth)
        return drawShapeGrid(pitchPath, intensity, gap)
    elif(pitchType == "low"):
        pitchPath = drawCircle(start, 8, isFilled, sWidth)
        return drawShapeGrid(pitchPath, intensity, gap)
    else:
        pitchPath = drawTriangle(start, 12, isFilled, sWidth)
        return drawShapeGrid(pitchPath, intensity, gap)
    
    
def drawTimbreTexture(timbreType, intensity, width, centerPoint, sWidth=2):
        
    if(timbreType == "organic"):
        return drawGridTexture(drawWiggleLine, intensity, width, centerPoint, sWidth)
    elif(timbreType == "mechanical"):
        return drawGridTexture(drawZigZagLine, intensity, width, centerPoint, sWidth)
    else:
        return drawGridTexture(drawStraightLine, intensity, width, centerPoint, sWidth)
        

def drawGridTexture(path, intensity, width, centerPoint, sWidth = 1):
    r = width /2
    cX, cY = centerPoint
    xStart = cX - r
    yStart = cY - r
  
    linePath = path(xStart, yStart, width, sWidth)
    density = intensity
    return drawGrid(linePath, density, width//density, centerPoint)
                

######## DRAW SQUARE

def drawSquare(rad, centerPoint):
    squareShape = BezierPath()
    cX, cY = centerPoint
    # COUNTER-CLOCKWISE
    A = (cX + rad , cY - rad)
    B = (cX + rad , cY + rad)
    C = (cX - rad , cY + rad)
    D = (cX - rad , cY - rad)
    
    squareShape.polygon(A, B, C, D, close=False)
    squareShape.closePath()
    return squareShape

def drawTexturedSquare(timbreType, intensity, pitchType, intensityPitch, rad, centerPoint):
   clip = drawSquare(rad, centerPoint)
   
   with savedState():
        # set the path as a clipping path
       clipPath(clip)
       # print(clipPath(clip))
        # the texture will be clipped inside the path
       texture = drawTimbreTexture(timbreType, intensity, rad*2, centerPoint, 4)
       drawPath(texture);
       textureTwo = drawPitchTexture(pitchType, intensityPitch, rad*2, centerPoint, True, 3)
       drawPath(textureTwo);
          
   drawPath(clip);
   
def drawTexturedSquareGrid(soundsIter, rad, centerPoint, col=1, row=1, isTesting = False):

    # Translation Variables
    xMove = rad*2
    yMove = rad*2
    
    for i in range(row):
        for j in range(col):
            if(not isTesting):
                sound = next(soundsIter, {})
                drawTexturedSquare(
                    sound["timbreType"], 
                    int(sound["timbreIntensity"]), 
                    sound["pitchType"],
                    int(sound["pitchIntensity"]), rad, centerPoint)
            else:
                ## FOR TESTING        
                if (random.randint(0,5)%2==0):
                    drawTexturedSquare("organic", 2, "low", 2, rad, centerPoint)
                else:
                    drawTexturedSquare("mechanical", 5, "high", 5, rad, centerPoint)
                
            translate(xMove,  0)
        translate(-xMove * col, -yMove)


######### DRAW HEX


def drawHexagon(rad, centerPoint):
    hexShape = BezierPath()
    cX, cY = centerPoint
    # COUNTER-CLOCKWISE
    A = (cX + rad , cY)
    B = (cX + rad * math.cos(RAD_300), cY - rad * math.sin(RAD_300))
    C = (cX + rad * math.cos(RAD_240), cY - rad * math.sin(RAD_240))
    D = (cX - rad ,cY)
    E = (cX + rad * math.cos(RAD_120), cY - rad * math.sin(RAD_120))
    F = (cX + rad * math.cos(RAD_60), cY - rad * math.sin(RAD_60))
    
    # FOR TESTING
    # drawPoint(A, (227/255,200/255,0/255)) # yellow
    # drawPoint(B, (1,0,0)) #red
    # drawPoint(C, (0, 1, 0)) #green
    # drawPoint(D, (0,0,1)) #blue
    # drawPoint(E, (240/255,163/255,10/255)) #orange
    # drawPoint(F, (170/255, 0/255,255/255)) #purple

    hexShape.polygon(A, B, C, D, E, F, close=False)
    hexShape.closePath()
    return hexShape

def drawHexGrid(hexShape, col=1, row=1):
    xMove = (hexShape.points[0][0] - hexShape.points[2][0])
    yMove = (hexShape.points[1][1] - hexShape.points[4][1]) / 2
    print(hexShape.points, yMove)
    for i in range(row):
        for j in range(col):
            drawPath(hexShape)
            # Translate down if col is even, translate up if column is odd
            translate(xMove,  -yMove if j%2==0 else yMove)
        translate(-xMove * col, -yMove*2 if col%2==0 else -yMove)


def drawTexturedHex(timbreType, intensity, pitchType, intensityPitch, rad, centerPoint):
   clip = drawHexagon(rad, centerPoint)
   
   with savedState():
        # set the path as a clipping path
       clipPath(clip)
       # print(clipPath(clip))
        # the texture will be clipped inside the path
       texture = drawTimbreTexture(timbreType, intensity, rad*2, centerPoint, 4)
       drawPath(texture);
       textureTwo = drawPitchTexture(pitchType, intensityPitch, rad*2, centerPoint, True, 3)
       drawPath(textureTwo);
          
   drawPath(clip);


def drawTexturedHexGrid(soundsIter, rad, centerPoint, col=1, row=1, isTesting = False):

    # Some Trig
    cX, cY = centerPoint
    Ax = cX + rad
    By = cY - rad * math.sin(RAD_300)
    Cx = cX + rad * math.cos(RAD_240)
    Ey = cY - rad * math.sin(RAD_120)
    # Translation Variables
    xMove = Ax - Cx
    yMove = (By - Ey)/2
    
    for i in range(row):
        for j in range(col):
            if(not isTesting):
                sound = next(soundsIter, {})
                drawTexturedHex(
                    sound["timbreType"], 
                    int(sound["timbreIntensity"]), 
                    sound["pitchType"],
                    int(sound["pitchIntensity"]), rad, centerPoint)
            else:
                ## FOR TESTING        
                if (random.randint(0,5)%2==0):
                    drawTexturedHex("organic", 2, "low", 2, rad, centerPoint)
                else:
                    drawTexturedHex("mechanical", 5, "high", 5, rad, centerPoint)
                
            translate(xMove,  -yMove if j%2==0 else yMove)
        translate(-xMove * col, -yMove*2 if col%2==0 else -yMove)


###### RUNNER

def mapSounds(file, dimensions):
    c,r = dimensions
    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        readerIt = iter(reader)
        drawTexturedHexGrid(readerIt, 40, (65, 1415), c,r)

def mapSoundsSquare(file, dimensions):
    c,r = dimensions
    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        readerIt = iter(reader)
        drawTexturedSquareGrid(readerIt, 40, (65, 1415), c,r)
        
        
        
strokeWidth(4)
fill(None)
stroke(0)
# shape = drawHexagon(54, (65, 1415))
# # drawHexGrid(shape,18, 15)

test_hex = {
    'timbreType' : "mechanical", 
    'timbreIntensity' : 3, 
    'pitchType' : "low", 
    'pitchIntensity' : 2,}

# mapSounds("gradiant.csv", (5, 8))
# mapSounds("soundscapeData.csv", (16,12))
mapSoundsSquare("SoundscapeDataLearner.csv", (5,8))

# drawPath(drawTexturedSquare(test_hex["timbreType"],test_hex["timbreIntensity"],test_hex["pitchType"],test_hex["pitchIntensity"], 40, (100,100)))
# drawTexturedHexGrid(54, (65, 1415),8,8)

saveImage("~/School/infodesign/Project 2/texturePrimer.pdf")

#polygon((150, 100), (125, 143), (124, 143), (50, 100), (125, 143), (125, 143))

# polygon((125, 57), (75, 57), (50, 100), (75, 143), (125, 143), (150, 100))


