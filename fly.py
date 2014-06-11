# fly.py - chairflying helper implemented with and dependent upon pygame library
# Author: nitor
# Date: Jun 2014
#
#########################
#
# MIT/Expat License
#
# Copyright (C) 2014 K. Brett Mulligan
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#########################

import pygame, sys, math
from pygame.locals import *

# main program config
debug = True
paused = True
mute = False
res = (1200, 600) # resolution
borderWidth = 10
bottomPad = 2
fps = 60
title = 'chairflyer'
timeInc = 9 # seconds

waypointsFilename = "waypoints.txt"


# player startup values
startingPoints = 0
startingLives = 5

# control values
hdgChange = 1
kiasChange = 1

# color presets
red = pygame.Color(255,0,0)
green = pygame.Color(0,255,0)
blue = pygame.Color(0,0,255)
lightBlue = pygame.Color(200,200,255)
white = pygame.Color(255,255,255)
black = pygame.Color(0,0,0)

def gray (val):
    return pygame.Color(val,val,val)
    
def recip (heading):
    return (heading + 180) % 360 

def distance (a, b):
    return math.sqrt(abs(a[0] - b[0])**2 + abs(a[1] - b[1])**2)
    
# Class defs
class Player:

    def __init__(self, pts, level):

        self.pts = pts
        self.level = level

    pts = 0
    level = 0
    lives = startingLives

    def getPoints(self):
        return self.pts

    def addPoints(self, newPoints):
        self.pts += newPoints

    def setPoints(self, newPoints):
        self.pts = newPoints

    def takeLife(self):
        self.lives -= 1

    def setLives(self, newLives):
        self.lives = newLives

    def getLives(self):
        return self.lives

    def addLife(self):
        self.lives += 1
    
class Game:

    level = 0

    def __init__(self):
        level = 1

    def setLevel(self, lvl):
        self.level = lvl

    def getLevel(self):
        return self.level
        
        
        
class Aircraft:

    wingOffsetX = 0
    wingOffsetY = 0
    
    def __init__(self):
        self.wingOffsetX = self.wgSpan
        self.wingOffsetY = self.length * 2
        
    hdg = 0
    alt = 0
    x = 0
    y = 0
    kias = 0
    ktas = 0
    gs = 0
    weight = 110 # in K-lbs
    
    maxKIAS = 310  # airframe restriction
    minKIAS = 90   # approx stall speed
    
    length = 50
    wgSpan = 50
    horzStabSpan = 20
    wgRoot = 0.2           # given in proportion of length from nose to tail
    stabRoot = 0.8         # given in proportion of length from nose to tail
    
    color = white
    
    # state
    isLead = False
    lead = None
    
    goal = None             # waypoint pos goal (x, y)
    goalHDG = 0
    goalKIAS = 210
    goalDistance = 5        # distance to next waypoint when it will sequence to the next
    
    # most change possible over one time increment
    hdgChange = 1
    kiasChange = 1
    
    waypoints = []
    
    
    def getPos(self):
        return (self.x, self.y)
        
    def setPos(self, npos):
        self.x = npos[0]
        self.y = npos[1]
        
    def getNosePos(self):
        return self.getPos()
        
    def getTailPos(self):
        dAng = 0 - self.hdg
        dRad = dAng * math.pi/180
        dX = math.sin(dRad) * self.length
        dY = math.cos(dRad) * self.length
        return (self.x + dX, self.y + dY)
        
    def getWgRoot(self):
        dAng = 0 - self.hdg
        dRad = dAng * math.pi/180
        dX = math.sin(dRad) * self.wgRoot * self.length
        dY = math.cos(dRad) * self.wgRoot * self.length
        return (self.x + dX, self.y + dY)
       
    def getRWgPos(self):
        dAng = 0 - self.hdg + 90
        dRad = dAng * math.pi/180
        dX = math.sin(dRad) * self.wgSpan/2
        dY = math.cos(dRad) * self.wgSpan/2
        return (self.getWgRoot()[0] + dX, self.getWgRoot()[1] + dY)
        
    def getLWgPos(self):
        dAng = 0 - self.hdg - 90
        dRad = dAng * math.pi/180
        dX = math.sin(dRad) * self.wgSpan/2
        dY = math.cos(dRad) * self.wgSpan/2
        return (self.getWgRoot()[0] + dX, self.getWgRoot()[1] + dY)
        
    def getStabRoot(self):
        dAng = 0 - self.hdg
        dRad = dAng * math.pi/180
        dX = math.sin(dRad) * self.stabRoot * self.length
        dY = math.cos(dRad) * self.stabRoot * self.length
        return (self.x + dX, self.y + dY)
        
    def getRStabPos(self):
        dAng = 0 - self.hdg + 90
        dRad = dAng * math.pi/180
        dX = math.sin(dRad) * self.horzStabSpan/2
        dY = math.cos(dRad) * self.horzStabSpan/2
        return (self.getStabRoot()[0] + dX, self.getStabRoot()[1] + dY)
        
    def getLStabPos(self):
        dAng = 0 - self.hdg - 90
        dRad = dAng * math.pi/180
        dX = math.sin(dRad) * self.horzStabSpan/2
        dY = math.cos(dRad) * self.horzStabSpan/2
        return (self.getStabRoot()[0] + dX, self.getStabRoot()[1] + dY)
        
    def getHDG(self):
        return self.hdg
        
    def setHDG(self, newHDG):
        self.hdg = abs(newHDG % 360)
        
    def getGS(self):
        return self.kias
        
    def getKIAS(self):
        return self.kias
        
    def setKIAS(self, newKIAS):
        if (newKIAS < self.minKIAS):
            self.kias = self.minKIAS
        elif (newKIAS > self.maxKIAS):
            self.kias = self.maxKIAS
        else:
            self.kias = newKIAS
        
    
    def updatePos(self, time):
        if (self.isLead):
            pass
        else:
            if self.getLead() != None:
                self.setGoal(self.getLead().getWingPos())
                
        dAng = self.hdg
        dRad = dAng * math.pi/180
        dX = math.sin(dRad) * self.getGS()/3600 * time
        dY = -math.cos(dRad) * self.getGS()/3600 * time
        
        self.x = self.x + dX
        self.y = self.y + dY
        
    def getWingPos(self):
        dAng = 20 - self.hdg
        dRad = dAng * math.pi/180
        dX = math.sin(dRad) * self.wingOffsetY
        dY = math.cos(dRad) * self.wingOffsetY
        return (self.x + dX, self.y + dY)
        
    def setIsLead(self, isLd):
        self.isLead = isLd

    def setLead(self, newLd):
        self.lead = newLd
        
    def getLead(self):
        return self.lead
        
    def getGoal(self):
        return self.goal
        
    def setGoal(self, newGoal):
        self.goal = newGoal
        
    def turnLeft(self):
        self.setHDG(self.getHDG() - self.hdgChange)
    
    def turnRight(self):    
        self.setHDG(self.getHDG() + self.hdgChange)
        
    def speedUp(self):
        self.setKIAS(self.getKIAS() + self.kiasChange)
    
    def slowDown(self):
        self.setKIAS(self.getKIAS() - self.kiasChange)
        
    def stepTowardGoal(self):
        # HDG
        # find the difference between current HDG and goal HDG
        self.determineGoalHDG()
        
        diffHDG = (self.getGoalHDG() - self.getHDG()) % 360
         
        if (diffHDG > 1 and diffHDG < 180):
            self.turnRight()
        elif (diffHDG < -1 or diffHDG > 180):
            self.turnLeft()
        else:
            pass
   
        # AIRSPEED
        # find the difference between current KIAS and goal KIAS         
        diffKIAS = self.getKIAS() - self.getGoalKIAS()
        if (diffKIAS < -0.1):
            self.speedUp()
        elif (diffKIAS > 0.1):
            self.slowDown()
        else:
            pass

    def determineGoalHDG(self):
        # make sure there's a goal
        if self.goal == None:
            pass
        else:
            # determine where my goal is in relation to me
            delX = self.goal[0] - self.x
            delY = self.goal[1] - self.y

            if (delX > 0 and delY > 0):                         # goal in quadrant 2
                self.setGoalHDG(90 + abs(math.degrees(math.atan(delY/delX))))
            elif (delX > 0 and delY < 0):                       # goal in quadrant 1
                self.setGoalHDG(0 + abs(math.degrees(math.atan(delX/delY))))
            elif (delX < 0 and delY > 0):                       # goal in quadrant 3
                self.setGoalHDG(180 + abs(math.degrees(math.atan(delX/delY))))
            elif (delX < 0 and delY < 0):                       # goal in quadrant 4
                self.setGoalHDG(270 + abs(math.degrees(math.atan(delY/delX))))
            else:
                pass
                
    def setGoalHDG(self, newHDG):
        self.goalHDG = newHDG
    
    def getGoalHDG(self):
        return self.goalHDG
    
    def setGoalKIAS(self, newKIAS):
        self.goalKIAS = newKIAS
    
    def getGoalKIAS(self):
        return self.goalKIAS
        
    def loadWaypoints(self, newSet):
        self.waypoints = list(newSet)
        self.setGoal(self.waypoints[0].getPos())
        
    def hasArrived(self):
        return (distance(self.getPos(), self.getGoal()) < self.goalDistance)
    
    def arrive(self):
        #move on to the next waypoint
        if (self.waypoints):
            self.setGoal(self.waypoints.pop(0).getPos())
        
   
class Waypoint:

    pos = (0,0)
    color = red
    radius = 3
    
    def __init__(self, newPos):
        self.pos = newPos
        self.color = red
        
    def setPos(self, newPos):
        self.pos = newPos
        
    def getPos(self):
        return self.pos
        
    def getColor(self):
        return self.color
    
# setup

pygame.init()
fpsClock = pygame.time.Clock()

windowSurfObj = pygame.display.set_mode(res)
pygame.display.set_caption(title)


fontSize = 24
fontObj = pygame.font.Font(None, fontSize)
label = 'Status: '
msg = 'Program started...'

# top level game state
game = Game()
game.setLevel(1)
player = Player(0,1)

# waypoints init
waypoints = []

def initWaypoints (filename):

    wpf = open(filename, 'r')
    if wpf == None:
        print "Error: Could not open waypoint file."
    else:
        for line in wpf:
            if line != "":
                wpData = line
                listOfValues = wpData.split(" ")
                x = int(listOfValues[0])
                y = int(listOfValues[1])
                waypoints.append(Waypoint((x,y)))
    wpf.close()

initWaypoints(waypointsFilename)

# aircraft init
lead = Aircraft()
lead.setIsLead(True)
lead.setPos((res[0]/2, res[1]/2))
lead.loadWaypoints(waypoints)

wing = Aircraft()
wing.setPos(lead.getWingPos())
wing.setLead(lead)


# input section
def processInput():
    global paused, mute, msg, debug
    
    global lead
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        
        elif event.type == MOUSEMOTION:
            if not paused:
                pass
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                leftClick(event.pos)
            elif event.button == 2:
                middleClick(event.pos)
            elif event.button == 3:
                rightClick(event.pos)
            elif event.button == 4:
                scrollUp()
            elif event.button == 5:
                scrollDown()
                
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.event.post(pygame.event.Event(QUIT))
            elif event.key == K_p:
                paused = not paused
            elif event.key == K_n:
                nextLevel()
            elif event.key == K_d:
                debug = not debug
            elif event.key == K_m or event.key == K_s:
                mute = not mute
            elif event.key == K_SPACE:
                togglePause()

def pollInputs():

    keys = pygame.key.get_pressed()
    if keys[K_LEFT]:
        if not paused:
            keyLeft()
    elif keys[K_RIGHT]:
        if not paused:
            keyRight()
    if keys[K_UP]:
        if not paused:
            keyUp()     
    elif keys[K_DOWN]:
        if not paused:
            keyDown()

def leftClick(pos):
    global msg, lead
    msg = 'left click'
    
    lead.setGoal(pos)

def rightClick(pos):
    global msg
    msg = 'right click'

def middleClick(pos):
    global msg
    msg = 'middle click'  

def scrollUp():
    global msg, lead
    msg = 'scroll up'
    
def scrollDown():
    global msg, lead
    msg = 'scroll down'
    
def keyLeft():
    global msg, lead
    msg = 'key left'
    lead.turnLeft()
    
def keyRight():
    global msg, lead
    msg = 'key right'
    lead.turnRight()
    
def keyUp():
    global msg, lead
    msg = 'key up'
    lead.setGoalKIAS(lead.getGoalKIAS() + 1)
    
def keyDown():
    global msg, lead
    msg = 'key down'
    lead.setGoalKIAS(lead.getGoalKIAS() - 1)
       
def togglePause():
    global paused
    paused = not paused
    
# graphics    
def draw():
    windowSurfObj.fill(black)

    # draw background
    drawBackground(windowSurfObj)
    
    # draw border
    pygame.draw.rect(windowSurfObj, white, (borderWidth,borderWidth,res[0]-borderWidth*2,res[1]-(fontSize + bottomPad + borderWidth*2)), 1)
    
    # draw waypoints
    drawWaypoints(windowSurfObj, waypoints)
    
    # draw aircraft (last so they show up on top of everything)
    drawAircraft(windowSurfObj, lead)
    drawAircraft(windowSurfObj, wing)
    
    # debug status
    if debug:
        drawText(windowSurfObj, 'Speed: ' + str(lead.getGS()), (borderWidth, res[1] - (fontSize)))
        drawText(windowSurfObj, 'Goal HDG: ' + str(lead.getGoalHDG())[:5], (borderWidth + res[0]*1/5, res[1] - (fontSize)))
        drawText(windowSurfObj, 'Goal: ' + str(lead.getGoal()), (borderWidth + res[0]*2/5, res[1] - (fontSize)))
    else:
        drawText(windowSurfObj, 'Lives: ' + str(player.getLives()), (borderWidth, res[1] - (fontSize)))
        
    # stats
    drawText(windowSurfObj, 'Score: ' + str(player.getPoints()), (res[0]*3/5 , res[1] - (fontSize)))
    drawText(windowSurfObj, 'Level: ' + str(game.getLevel()), (res[0]*4/5 , res[1] - (fontSize)))

def drawAircraft(wso, ac):
    # fuselage
    pygame.draw.aaline(wso, ac.color, ac.getNosePos(), ac.getTailPos(), False)
    
    # wings
    pygame.draw.aaline(wso, ac.color, ac.getWgRoot(), ac.getRWgPos(), False)
    pygame.draw.aaline(wso, ac.color, ac.getWgRoot(), ac.getLWgPos(), False)
    
    # stab
    pygame.draw.aaline(wso, ac.color, ac.getStabRoot(), ac.getRStabPos(), False)
    pygame.draw.aaline(wso, ac.color, ac.getStabRoot(), ac.getLStabPos(), False)
    
    if ac.getGoal():
        pygame.draw.circle(wso, red, (int(ac.getGoal()[0]), int(ac.getGoal()[1])), 5, 1)

def drawWaypoints(wso, waypoints):
    # draw legs
    for leg in range(0, len(waypoints) - 1):
        pygame.draw.aaline(wso, waypoints[leg].color, waypoints[leg].getPos(), waypoints[leg + 1].getPos(), False)
    # draw waypoints
    for wp in waypoints:
        drawWaypoint(wso, wp)
        
def drawWaypoint(wso, wp):
    pygame.draw.circle(wso, wp.color, wp.getPos(), wp.radius, 0)

def drawBackground(wso):
    pygame.draw.circle(wso, gray(25), (res[0]/3 + 40, res[1]/3), 240)
    pygame.draw.circle(wso, gray(20), (res[0]*2/3, res[1]*2/3), 250)
    pygame.draw.circle(wso, gray(15), (res[0]*1/4, res[1]*4/5), 200)

def drawText(wso, string, coords):
    textSurfObj = fontObj.render(string, False, white)
    textRectObj = textSurfObj.get_rect()
    textRectObj.topleft = coords
    wso.blit(textSurfObj, textRectObj)

def updatePositions():
    global lead, wing
    
    if not paused:
        lead.updatePos(timeInc)
        wing.updatePos(timeInc)

def progressTowardGoals():
    global lead, wing
    
    if not paused:
        lead.stepTowardGoal()
        wing.stepTowardGoal()
        
def adjustGoals():
    global lead, waypoints
    
    if (lead.getGoal()):
        if (lead.hasArrived()):
            # success! plane reached its goal, move on to the next
            lead.arrive()
        elif ():
            
        

def outOfBounds():
    player.takeLife()
    if not paused:
        togglePause()

def checkGame():
    if player.getLives() <= 0:
        resetGame()
    
def nextLevel():
    global game

    game.setLevel(game.getLevel() + 1)

    if not paused:
        togglePause()

def resetGame():
    global game, player
    
    game.setLevel(1)
    
    if not paused:
        togglePause()
    
    player.setPoints(startingPoints)
    player.setLives(startingLives)

# main program loop
while True:

    # check status, lives, bricks, etc
    checkGame()
    
    # do AI
    progressTowardGoals()
    adjustGoals()
    
    # update positions
    updatePositions()
    
    # draw
    draw()
    
    # input
    processInput()
    pollInputs()

    # update draw
    pygame.display.update()
    fpsClock.tick(fps)

