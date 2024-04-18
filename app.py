import pygame
import time
import threading
import math
import random
import re
import yaml
from yaml import SafeLoader


#initialising pygame
pygame.init()
pygame.display.init()

yourScore = 0       #Your Score
highScore = 0       #High Score
highplayername = "" #High Score Player Name

configPath="resources/appdata.yml"


#Variables
width=1920  #Screen Width
height=1080 #Screen Height
CenterY=height/2    #Center Screen Y
CenterX=width/2     #Center Screen X


Font1 = pygame.font.SysFont("Sans", 25)
Font2 = pygame.font.SysFont("Arial", 25)
Font3 = pygame.font.SysFont("Arial", 150)

#Movement Keys (Schema WASD)
Key=[False, False, False, False]

movementSpeed=2.5      #Movementspeed from Player
MovementSpeedBoss=1.5  #Movementspeed from Boss
projectilSpeed=5       #Projectilspeed from Player
projectilSpeedBoss=3.5 #Projectilespeed from Boss

projectilAmount=3       #Amount of Projectile the Boss shoots at once
projectilIntervall=3    #Intervall the Boss shoots Projectiles in sec.


delaytimer = 0              #Handles the Debuff delay
GUI=True                    #Is GUI enabled
stop=False                  #Are Threading Timers stopped
HitboxVisibility=False      #Is Hitbox Visible
GameOverVisibility=False   #Is GameOver Label Visible


clock =pygame.time.Clock()  #Set Clock to cap FPS


#Load Images
icon=pygame.image.load("resources/images/dinogehege.png")

backgroundRaw=pygame.image.load("resources/images/background.png")
backgroundImage=pygame.transform.scale(backgroundRaw, (width, height))

#Player1
player1=pygame.image.load("resources/images/Piratenschiff_Frame1.png")
player1_rect=player1.get_rect()

#Player2 (Player2 is a Bot)
player2=pygame.image.load("resources/images/Wizard_Frame1.png")
player2_rect=player2.get_rect()
player2_rect.x=CenterX
player2_rect.y=CenterY

#Projectil1
projectil1=pygame.image.load("resources/images/projectile.png")
projectiles=[]

#Projectil2
projectil2=pygame.image.load("resources/images/projectile2.png")
projectiles2=[]

#Screen
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Megakuul")
pygame.display.set_icon(icon)


#Label Class

class Label:

    def __init__(self, Text, ForeColor, BackColor, Location, Font, CustomSize=None):
        self.Text = Text
        self.ForeColor = ForeColor
        self.BackColor = BackColor
        self.Font = Font
        self.Location = Location
        self.active=False
        if CustomSize != None:
            self.Size = CustomSize
        else:
            self.Size = self.Font.size(Text)

        self.Rect = pygame.Rect(self.Location, self.Size)

    def draw(self):
        screen.blit(self.Font.render(self.Text, 1, self.ForeColor, self.BackColor), self.Location)

    def onClick(self, event, function, args=None):
        if event.type==pygame.MOUSEBUTTONDOWN:
            posX, posY = pygame.mouse.get_pos()
            if self.Rect.collidepoint(posX, posY):
                if args!=None:
                    function(args)
                else:
                    function()

    def onInput(self, event, BackColor, ActiveBackColor):
        if event.type==pygame.MOUSEBUTTONDOWN:
            posX, posY = pygame.mouse.get_pos()
            if self.Rect.collidepoint(posX, posY):
                self.active=True
                self.BackColor=ActiveBackColor
            else:
                self.active=False
                self.BackColor=BackColor
        if event.type==pygame.KEYDOWN:
            if self.active:
                if event.unicode=='\x08':
                    self.Text=(self.Text[:-1])
                else:
                    self.Text+=event.unicode
                    
            Font1.render(self.Text, 1, self.ForeColor)



#Funktionen

def get_screensize():
    global data
    global screen
    global width
    global height

    with open(configPath) as cf:
        data=yaml.load(cf, Loader=SafeLoader)
        width=data["ResX"]
        height=data["ResY"]
    screen=pygame.display.set_mode((width, height))

def get_highscore():
    global data
    global highScore

    with open(configPath) as cf:
        data=yaml.load(cf, Loader=SafeLoader)
        highScore=data["Highscore"]

def set_highscore(score):
    global data
    with open(configPath, 'w') as cf:

        data["Highscore"]=score
        yaml.dump(data, cf)

#Movement Output
def Movement():
    #Check Right Border
    if player1_rect.x > (width-player1.get_width()):
        if Key[1]:
            player1_rect.x-=movementSpeed*cf
        
    #Check Bottom Border
    elif player1_rect.y > (height-player1.get_height()):
        if Key[0]:
            player1_rect.y-=movementSpeed*cf
    #Check Left Border
    elif player1_rect.x < -1:
        if Key[3]:
            player1_rect.x+=movementSpeed*cf
    #Check Top Border
    elif player1_rect.y < -1:
        if Key[2]:
            player1_rect.y+=movementSpeed*cf
    #If no Border is touched execute Movement
    else:
        if Key[0]:
            player1_rect.y-=movementSpeed*cf
        if Key[1]:
            player1_rect.x-=movementSpeed*cf
        if Key[2]:
            player1_rect.y+=movementSpeed*cf
        if Key[3]:
            player1_rect.x+=movementSpeed*cf

#Movement Input
def MovementInp():
    if event.type==pygame.KEYDOWN:
        if event.key==pygame.K_w:
            Key[0]=True
        elif event.key==pygame.K_a:
            Key[1]=True
        elif event.key==pygame.K_s:
            Key[2]=True
        elif event.key==pygame.K_d:
            Key[3]=True
    if event.type==pygame.KEYUP:
        if event.key==pygame.K_w:
            Key[0]=False
        elif event.key==pygame.K_a:
            Key[1]=False
        elif event.key==pygame.K_s:
            Key[2]=False
        elif event.key==pygame.K_d:
            Key[3]=False



#Mouse Position Input

def MouseClick():
    if event.type==pygame.MOUSEBUTTONDOWN:
        global movX
        global movY
        mouspos=pygame.mouse.get_pos()
        Atan2 = math.atan2(mouspos[1]-player1_rect[1]-100, mouspos[0]-player1_rect[0]-100)

        projectilrect=projectil1.get_rect()
        projectilrect.x=player1_rect.x+100
        projectilrect.y=player1_rect.y+100
        projectiles.append([projectilrect, Atan2])

        
def ShootProjectiles(projectilType):
    global projectiles
    global yourScore
    index=0

    for projectil in projectiles:
        movX = math.cos(projectil[1]) * projectilSpeed *cf
        movY = math.sin(projectil[1]) * projectilSpeed *cf

        projectil[0].x+=movX
        projectil[0].y+=movY

        screen.blit(projectilType, projectil[0])

        if projectil[0].colliderect(player2_rect):
            projectiles.pop(index)
            yourScore+=20
        
        if projectil[0].x > width or projectil[0].x < 0 or projectil[0].y > height or projectil[0].y < 0:
            projectiles.pop(index)

        index+=1




#Schneckenbuff
def Schneckenbuff(Schneckenmode):
    global movementSpeed
    global delaytimer
    global player1
    global PlayerState

    if Schneckenmode:
        PlayerState = 2
        player1=pygame.image.load("resources/images/Schneckenbuff.png")
        movementSpeed=1
        delaytimer = time.time()
    else:
        PlayerState = 1
        player1=pygame.image.load("resources/images/Piratenschiff_Frame1.png")
        movementSpeed=2.5


#Boost away
def boostaway():
    if Key[0]:
        player1_rect.y+=movementSpeed*20*cf
    if Key[1]:
        player1_rect.x+=movementSpeed*20*cf
    if Key[2]:
        player1_rect.y-=movementSpeed*20*cf
    if Key[3]:
        player1_rect.x-=movementSpeed*20*cf

#Boss movement
Mov=True

def BossMovement():
    global Mov
    if player2_rect.x > (width-400)-player2.get_width():
        Mov=True
    elif player2_rect.x < 400:
        Mov=False

    if Mov:
        player2_rect.x-=MovementSpeedBoss*cf
    else:
        player2_rect.x+=MovementSpeedBoss*cf
    





#Fortlaufende Events (eigene Threads)
BossState=0
PlayerState=0

class threadingTimer:
    def __init__(self, intervall, function, args=None):
        self.intervall=intervall
        self.function=function
        self.args=args
        self.Timer=None
        

    def startstopTimer(self, start):
        if start:
            if self.args!=None:
                self.Timer=threading.Timer(self.intervall, self.function, [self.args])
                self.Timer.daemon=True
                self.Timer.start()
            else:
                self.Timer=threading.Timer(self.intervall, self.function)
                self.Timer.daemon=True
                self.Timer.start()
        else:
            self.Timer.cancel()



def changeBossAnimation():
    global BossState
    global player2

    if BossState==0:
        BossState=1
        player2=pygame.image.load("resources/images/Wizard_Frame1.png")
    elif BossState==1:
        BossState=0
        player2=pygame.image.load("resources/images/Wizard_Frame2.png")

    BossAnimationSequence.startstopTimer(True)
    
def changePlayerAnimation():
    global PlayerState
    global player1

    if PlayerState==0:
        PlayerState=1
        player1=pygame.image.load("resources/images/Piratenschiff_Frame1.png")
    elif PlayerState==1:
        PlayerState=0
        player1=pygame.image.load("resources/images/Piratenschiff_Frame2.png")

    PlayerAnimationSequence.startstopTimer(True)

def bossAttack(projectilQuantity):
    global projectiles

    for index in range(projectilQuantity):

        Atan2=random.uniform(-3.0, 3.0)
        #Get Rect from Projectil2
        projectilerect=projectil2.get_rect()
        #Set Startpoint of the Projectiles
        projectilerect.x=player2_rect.x+100
        projectilerect.y=player2_rect.y+100

        projectiles2.append([projectilerect, Atan2])

    BossShootingSequence.startstopTimer(True)


def shootBossProjectiles(projectilType):
    global projectiles2
    global GUI
    index=0
    for projectil in projectiles2:
        
        movX=math.cos(projectil[1]) * projectilSpeedBoss*cf
        movY=math.sin(projectil[1]) * projectilSpeedBoss*cf

        projectil[0].x+=movX
        projectil[0].y+=movY

        screen.blit(projectilType, projectil[0])

        #Checks if Projectile Collides with Border
        if projectil[0].x > width or projectil[0].x < 0 or projectil[0].y > height or projectil[0].y < 0:
            projectiles2.pop(index)
        #Checks if Projectile Collides with Player
        if projectil[0].colliderect(player1_rect):
            projectiles2.pop(index)
            resetGame()

        index+=1

PlayerAnimationSequence = threadingTimer(0.1, changePlayerAnimation)

BossAnimationSequence = threadingTimer(0.1, changeBossAnimation)

BossShootingSequence = threadingTimer(projectilIntervall, bossAttack, projectilAmount)


#Quit game
def leaveGame():
    pygame.quit()
    exit()

def quitgame(event):
    if event.type == pygame.QUIT:
        leaveGame()

def startGame():
    global GUI
    global GameOverVisibility

    BossAnimationSequence.startstopTimer(True)

    PlayerAnimationSequence.startstopTimer(True)

    BossShootingSequence.startstopTimer(True)

    GUI=False
    GameOverVisibility=False

def resetGame():
    global GUI
    global GameOverVisibility
    global Key
    global yourScore
    global highScore
    global player1_rect
    global player2_rect

    BossAnimationSequence.startstopTimer(False)

    PlayerAnimationSequence.startstopTimer(False)

    BossShootingSequence.startstopTimer(False)

    Schneckenbuff(False)

    GUI=True
    GameOverVisibility=True

    player1_rect.x=0
    player1_rect.y=0

    player2_rect.x=CenterX
    player2_rect.y=CenterY

    Key=[False, False, False, False]
    projectiles.clear()
    projectiles2.clear()

    if yourScore>highScore:
        checkEasterEgg(nameBox.Text)

        set_highscore(yourScore)
        get_highscore()

            

    yourScore=0

def checkEasterEgg(word):
    global yourScore
    #RegEx
    x=re.findall("MEGAKUUL", word.upper())
    if x:
         yourScore+=2000


def showHitbox():
    
    global HitboxVisibility
    if HitboxVisibility:
        HitboxVisibility=not HitboxVisibility
        hitboxButton.BackColor=(237, 66, 24)
    else:
        HitboxVisibility=not HitboxVisibility
        hitboxButton.BackColor=(94, 235, 52)

#Enter the GUI Start Menu
def EnterGUI(enterGUI):
    if enterGUI:
        get_highscore()

        #Loop throug GUI relevant Events
        for event in pygame.event.get():
            # check if the event is the X button 
            quitgame(event)

            Label.onClick(playButton, event, startGame)
            Label.onClick(hitboxButton, event, showHitbox)
            Label.onClick(quitButton, event, leaveGame)
            Label.onInput(nameBox, event, (255,255,255), (188, 230, 199))
        screen.fill(0)

        Label.draw(playButton)
        Label.draw(hitboxButton)
        Label.draw(nameBox)
        Label.draw(quitButton)

        highScoreLbl.Text=str(highScore)
        Label.draw(highScoreLbl)

        if GameOverVisibility:
            Label.draw(gameOverLabel)
        
        pygame.display.flip()
        return True
    else:
        return False


#On Start
get_screensize()

#GUI Elements

yourScoreLbl = Label(
    "Your Score: ", (255,255,255), (0,0,0), (width-300, 20), Font1
)

highScoreLbl = Label(
    "High Score: ", (255,255,255), (0,0,0), (50, 50), Font1
)

playButton = Label(
    "  Play  ", (0,0,0), (113, 117, 145), (width-110, height-50), Font2
)

hitboxButton = Label(
    " show Hitbox ", (0,0,0), (237, 66, 24), (width-180, height-100), Font2
)

gameOverLabel = Label(
    "Game Over", (237, 66, 24), (0,0,0), (CenterX-420, CenterY-150), Font3
)

nameBox = Label(
    "Type in your Name", (0,0,0), (255,255,255), (50,height-50), Font2
)

quitButton = Label(
    "  Exit  ", (0,0,0), (113, 117, 145), (width-180, height-50), Font2
)

while 1:
    clockraw = clock.tick(240)
    cf = clockraw/5

    if EnterGUI(GUI):
        continue
    
    
    #loop through Game relevant Events
    for event in pygame.event.get():
        #Get Movement Input
        MovementInp()
        #Get Mouse Input
        MouseClick()
        # check if the event is the X button 
        quitgame(event)

    #Start Game Stuff
     
    #Refresh Display
    pygame.display.flip()

    #clear the screen before drawing it again
    screen.fill(0)
    screen.blit(backgroundImage, (0,0))

    #Draw Labels
    yourScoreLbl.Text = "Your Score: "+str(yourScore)
    Label.draw(yourScoreLbl)

    highScoreLbl.Text = "High Score: "+str(highScore)
    Label.draw(highScoreLbl)
 
    #Draw Player
    screen.blit(player1, player1_rect)

    #Draw Boss
    BossMovement()
    screen.blit(player2, player2_rect)

    #Execute Movement
    Movement()

    #Draw Hitboxes if Mode is Active
    if HitboxVisibility:
        pygame.draw.rect(screen, (255,255,255), player2_rect, 4)
        pygame.draw.rect(screen, (255,255,255), player1_rect, 4)


    #Shoot Bossbullets
    shootBossProjectiles(projectil2)

    #Shoot Bullets
    ShootProjectiles(projectil1)

    #Check Schneckenbuffdelay
    #Vergleiche Zeit aktuell mit Delaytimer, dieser wird bei Schneckenbuff(true) gemessen. Delaytimer wird mit 0 "resetet"
    if round(time.time() - delaytimer)==3:
        Schneckenbuff(False)
        delaytimer=0


    #Check Collider
    if player1_rect.colliderect(player2_rect):
        yourScore-=5
        boostaway()
        Schneckenbuff(True)
