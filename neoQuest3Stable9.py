import csv
import math
import random
import time
import pygame
import pygame.freetype 

unitSize=40; #this is the square size of each tile in pixels.

state="MAP";#states are MAP, MENU, TITLE, INVENTORY, EQUPIMENT, and COMBAT
previousState="";#this is used to go back to a previous menu in certain contexts.
firstTimeInState=True;

windowWidth=1200;
visibleWidth=9;
visibleHeight=9;
viewOffsetX=math.floor(visibleWidth/2);
viewOffsetY=math.floor(visibleHeight/2);
borderWidth=visibleWidth+2;
borderHeight=visibleHeight+2;
playerX=3;
playerY=3;
mapGUIOffsetx=unitSize*2;
mapGUIOffsetY=unitSize*2;
textOffset=unitSize*(visibleHeight+4)#

dialogFlag=False;
combatFlag=False;

intendedMoveX=0;
intendedMoveY=0;

u=0;

encounterRate=20;# 1/X encounter rate

combatUIOffsetX=520;
combatUIOffsetY=unitSize;
partyVerticalOffset=500;

currentMapName="noMAP";
currentMapData=[];
currentEncounterTable=[0];
tileSetName="plains";

currentDialogLine=0;
currentDialogData=[];
currentDialogSelection=0;
dialogNPCResponse="";
dialogOptions=[];
dialogDestinations=[];
optionCount=0;

mapWidth=2;
mapHeight=2;
visibleMap = [[0 for i in range(visibleWidth)] for j in range(visibleHeight)]

healthbarMaxSize=unitSize*2;
healthbarBackgroundColor=(64,64,84);
healthbarStartColor=pygame.Color(0,255,0,0);#a max healthbar is this.
healthbarEndColor=pygame.Color(255,0,0,0); # an empty health bar is this color.

partyTable=[];
enemyTable=[];
partyList=[];
enemyList=[];
enemyPictures=[];
textEffectList=[];
damageToDeal=0;

goldCount=50;

textRiseSpeed=1;
textRandomRange=5;
textLifespan=90;#how many frames to appear for.
delayTimer=200;

lastCheckpointMap="plains2"; #name of the last map you hit a checkpoint on.
lastCheckPointCoords=(5,5);#where the player should respawn after hitting a checkpoint.
lastCheckPointTileSet="plains";

#### UI images) #####

playerTile=pygame.image.load("images/jeranSmall.png");
playerTileLeft=pygame.image.load("images/jeranSmall.png");
playerTileRight=pygame.image.load("images/jeranSmallFlip.png");
borderTile=pygame.image.load("images/border.png");
textBox=pygame.image.load("images/textBox.png");
clearArrow=pygame.image.load("images/clearArrow.gif");
selectionArrow=pygame.image.load("images/arrow.png");
selectionImage=pygame.image.load("images/selectionImage.png");
menuBackground=pygame.image.load("images/menuBG.png");
turnArrowClear=pygame.image.load("images/arrowClear.png");
turnArrowParty=pygame.image.load("images/currentTurn.png");
turnArrowEnemy=pygame.image.load("images/currentTurnFlip.png");

### Party Draw Images ####

jeranNeutral=pygame.image.load("images/jeran.gif");
lishaNeutral=pygame.image.load("images/lisha.gif");
kassNeutral=pygame.image.load("images/kass.gif");
kaylaNeutral=pygame.image.load("images/kayla.gif");


####  map tile images   #####
###these images will swap out depending on the level.
errorTile=pygame.image.load("images/error.gif");
floorTile=pygame.image.load("images/grs.gif");
terrainATile=pygame.image.load("images/hilg.gif");
terrainBTile=pygame.image.load("images/forg.gif");
terrainCTile=pygame.image.load("images/wtr.gif");
terrainDTile=pygame.image.load("images/hwt4.gif");
checkPointTile=pygame.image.load("images/Chkpt.gif");
wallTile=pygame.image.load("images/mntg.gif");
transTileA=pygame.image.load("images/castle.gif");
transTileB=pygame.image.load("images/city.gif");
transTileC=pygame.image.load("images/grs_vlg.gif");

bumpList=["w","C","D","N"]; #tile letters that should be unpassable.

######   pygame nonsense   ######
canvas = pygame.Surface((windowWidth,(visibleWidth+8)*unitSize))
combatCanvas=pygame.Surface((windowWidth,880))#this one only appears in the combat phase.
window = pygame.display.set_mode((windowWidth,(visibleWidth+8)*unitSize))
pygame.display.set_caption("NeoQuest3")
pygame.freetype.init()
dialogFont = pygame.freetype.Font("Comic Book.otf",unitSize*.5)
UIFont = pygame.freetype.Font("ComicHelvetic_Medium.otf",unitSize)
damageFont = pygame.freetype.Font("Arcadepix Plus.ttf",unitSize*.5)
pygame.mixer.init();
pygame.mixer.set_num_channels(99);
bumpSound=pygame.mixer.Sound("sounds/bump.wav");
enemyEncounterSound=pygame.mixer.Sound("sounds/enemyEncounter.wav");
hitEnemySound=pygame.mixer.Sound("sounds/hitEnemy.wav");
enemyDeathSound=pygame.mixer.Sound("sounds/enemypoof.wav");
partyDeathSound=pygame.mixer.Sound("sounds/partyDeathSound.wav");
invalidSelectionSound=pygame.mixer.Sound("sounds/invalidSelection.wav");
winSound=pygame.mixer.Sound("sounds/tada.wav");
partyAttackSound=pygame.mixer.Sound("sounds/partyHit.wav");
healSound=pygame.mixer.Sound("sounds/healSound.wav");
levelUpSound=pygame.mixer.Sound("sounds/levelUp.wav");
clock = pygame.time.Clock()
clock.tick(10)#we dont need +120hz

####################inventory Varbs######################
p0Weapons=["sword","bigger sword","biggest sword"];
p1Weapons=["cardboard scimitar","tri-scimitar","ancient scimitar"];
pWeapons=["dual pikes","double spikes","twice hammers"];
p3Weapons=["test tube","flask","big beaker"];

p0Armor=["chain mail","iron armor","steel plate"];
p1Armor=["cardboard sheild","metal sheild","magic sheild"];
p2Armor=["tunic","plate armor","military uniform"];
p3Armor=["a big hat","a giant floppy hat","Kuvara's Cap"];

p0Wand=["Mystical Teapot of Doom","Borovans Cement Mixer","Wand of Flamebolt"];
p1Wand=["Weird Scarab","Super Sand Grain","Wand of Ultranova"];
p2Wand=["Iced Wand","Werelupe Claw Necklace","Wand of Dark Nova"];
p3Wand=["Bunson Burner","heating mantle", "induction coil"];


#currentInventory=["cookie tin", "zebra", "conditioner", "pair of goggles","bowl","mouse pad","keyboard"];
#currentInventory=["cookie tin", "zebra", "conditioner", "pair of goggles","bowl","mouse pad","keyboard","umbrella","pencil","tennis racket","sun glasses","ocarina","spatula","game system","beaded bracelet","sunscreen","teddies","rope","cars","eye liner"]
currentInventory=["Weak Potion","Strong Potion","Weak Potion","Strong Potion","Weak Potion","Strong Potion","Weak Potion","Strong Potion","Weak Potion","Strong Potion"];
invMenuSelection=0;#currently selected slot in the inventory menu.
inventoryPageSize=8;#how many items are displayed in one page.
totalInventoryPages=1; #how many pages we have to divide things up into. this will equal len(currentInventory)/inventoryPageSize
currentInventoryPage=0;

####################pause menu variables################
currentPauseMenuSelection=0;
pauseMenuOptions=[
    "Inventory",
    "Equipment",
    "Options",
    "Quit",
    "Save"];#this menu will also gain the "Level Up" option once enough EXP is gained. But it will lose the "level up" once

###########  inventory Variables  ###############
exclusiveInventory=[];#this will be a list of every item in the game that there is only one of. (Equipment and Key items) Once an item is collected in the overworld, a function will attempt to move it from this list to the main inventory. This prevents multiple copies from being recieved.
#commonItems=[];#this is a list of items that there is an infinite number of. They would be in shops, and are just added to the inventory in exchange for gold. 



####### Combat Variables #######

partySize=4;#how many party members we have unlocked. (max is 4
currentTurn=0;
turnOrder=[];
enemyCount=1;
enemySelection=-1;
enemyMenuSelection=0;
currentPartyTurn=0;
combatMenuMainOptions=[
    "Attack",
    "Spell",
    "Wait",    
    "Item"]
enemyMenuDisplayOffsetY=240;
weaponNames="woodensword","iron sword"," steel sword"," sharp blade"," super blade","mega blade"


####################################################################
####################### Generic Functions #############################
##################################################################

def lerp(a, b, t):
    return a*(1 - t) + b*t;

def clamp(num,min_value,max_value):
   return max(min(num,max_value),min_value);

def rotateArray(targetArray):
    pivot = []
    for row in targetArray:
      for column, cell in enumerate(row):
        if len(pivot) == column: pivot.append([])
        pivot[column].append(cell)
    return pivot;

def forceCombatDisplayUpdate():
    for a in partyList:
        a.display();
    for a in enemyList:
        a.display();
    window.blit(canvas,(0,0))#write new pixels to display
    pygame.display.update()#draw#



def forceDisplayUpdate():
    canvas.blit(combatCanvas,(combatUIOffsetX,combatUIOffsetY));
    window.blit(canvas,(0,0))#write new pixels to display
    pygame.display.update()#draw

###################################################################################################
#############################   Map functions  ###########################################################
###################################################################################################
def loadMap(mapName): #map files should be saved with the delimter being ,
    global currentMapData,currentMapName;
    try:
        datafile=open(mapName+".csv","r");
        currentMapData=csv.reader(datafile,delimiter=",");
        currentMapName=mapName;
        currentMapData=list(currentMapData);# convert the csv object into a 2d array.
        currentMapData=rotateArray(currentMapData);#its rotated from what youd expect. 
        mapWidth=len(currentMapData[0]);
        mapHeight=len(currentMapData);
        loadMapEncounters(mapName);
        
    except Exception as e:
        print(e)
        currentMapName="noMap";
        currentMapData=["no map data!"];

def loadDialog(dialogName): #dialog files should be saved with the delimter being |
    global currentDialogData;
    try:
        datafile=open(dialogName+".csv","r");
        currentDialogData=csv.reader(datafile,delimiter="|");
        currentDialogData=list(currentDialogData);# convert the csv object into a 2d array.
    except Exception as e:
        print(e)
        currentDialogData=["i am error!","I am bug!",0];

def loadDialogOptions(line):
    global dialogDestinations,dialogOptions,dialogNPCResponse
    lineData=currentDialogData[line];
    dialogNPCResponse=lineData[0];
    dialogOptions=lineData[1::2];#returns every other line (skipping destinations.)
    dialogDestinations=lineData[2::2]
    while("" in dialogOptions):
        dialogOptions.remove("");
    while("" in dialogDestinations):
        dialogDestinations.remove("");


def displayDialogOptions():
    global optionCount
    print("showing options",dialogOptions);
    optionCount=len(dialogOptions);
    for a in range(0,optionCount):
        displayText(dialogOptions[a],(13,45,110),dialogFont,unitSize,unitSize*(visibleHeight+5+(.5*a))); #start the dialog optiosn at row 8+map. 

def blitSelectionArrow():
    canvas.blit(clearArrow,(0,unitSize*(visibleHeight+3)));#clear out the previous arrow
    canvas.blit(selectionArrow,(0,unitSize*(visibleHeight+5+(currentDialogSelection*.5))-(unitSize*.25)));#3 accounts for border top/bottom, 2 margins, and 2 lines of NPC text. *.5 becuase the dialog text is half height.
    
def clearDialog():
    canvas.blit(textBox,(0,unitSize*(visibleHeight+4)));
                
def viewMap(viewX,viewY):#the view will be centered on X and Y. this should almost always be the players coordinates.
    global visibleMap;
    for y in range(0,visibleHeight):
        for x in range(0,visibleWidth):
            try:
                topLeftCornerX=viewX-viewOffsetX;
                topLeftCornerY=viewY-viewOffsetY;
                tile=currentMapData[topLeftCornerX+x][topLeftCornerY+y] #ideally this system will be replaced with an out of bounds detector, rather than a try catch
                if((topLeftCornerX+x)<0):
                    tile="b";
                if((topLeftCornerY+y)<0):
                    tile="b";
                visibleMap[x][y]=tile
            except:
                visibleMap[x][y]="b"

def loadMapEncounters(mapName):
    global currentEncounterTable;
    if(mapName=="plains2"):
        currentEncounterTable=[0,1,2,3];
    if(mapName=="plains3"):
        currentEncounterTable=[2,3,4,5];
    if(mapName=="castle1"):
        currentEncounterTable=[6,7,8,9];
    if(mapName=="castle2"):
        currentEncounterTable=[6,8,10,11];
    if(mapName=="plains2"):
        currentEncounterTable=[0,1,2,3];
                
def changeTileSet(setName):
    global tileSetName,errorTile,floorTile,terrainATile,terrainBTile,terrainCTile,terrainDTile,wallTile,transTileA,transTileBtransTileC,checkPointTile; 
    tileSetName=setName;
    if(tileSetName=="plains"):
        errorTile=pygame.image.load("images/error.gif");
        floorTile=pygame.image.load("images/grs.gif");
        terrainATile=pygame.image.load("images/hilg.gif");
        terrainBTile=pygame.image.load("images/forg.gif");
        terrainCTile=pygame.image.load("images/wtr.gif");
        terrainDTile=pygame.image.load("images/hwt4.gif");
        checkPointTile=pygame.image.load("images/grsChkpt.gif");
        wallTile=pygame.image.load("images/mntg.gif");
        transTileA=pygame.image.load("images/castle.gif");
        transTileB=pygame.image.load("images/city.gif");
        transTileC=pygame.image.load("images/grs_vlg.gif");
        
    if(tileSetName=="castle"):
        errorTile=pygame.image.load("images/error.gif");
        floorTile=pygame.image.load("images/dungeon.gif");
        terrainATile=pygame.image.load("images/dn_chr_l.gif");
        terrainBTile=pygame.image.load("images/dn_bed.gif");
        terrainCTile=pygame.image.load("images/dungeon_barrel.gif");
        terrainDTile=pygame.image.load("images/dungeon_pillar.gif");
        checkPointTile=pygame.image.load("images/dnchkPt.gif");
        wallTile=pygame.image.load("images/hf.gif");
        transTileA=pygame.image.load("images/dn_str_up.gif");
        transTileB=pygame.image.load("images/dn_str_dn.gif");
        transTileC=pygame.image.load("images/cv_exit.gif");
    

def transition(transData):
    global playerX;
    global playerY;
    loadMap(transData[1]);#get the map into memory
    changeTileSet(transData[2]);
    playerCoords=transData[3].split('-');
    playerX=int(playerCoords[0]);
    playerY=int(playerCoords[1]);

def parseMapTileData(dataString):
    dataList=dataString.split(',');
    for a in range(0,len(dataList)):
        dataList[a]=dataList[a].split('=')[1];#strip everything from the left of the ='s out of the data. this might change.     
    return dataList;

def displayText(text,color,fontType,locationX,locationY):
    fontType.render_to(canvas,(locationX,locationY),text,color) #https://stackoverflow.com/questions/20842801/how-to-display-text-in-pygame

def displayCombatText(text,color,fontType,locationX,locationY):
    fontType.render_to(combatCanvas,(locationX,locationY),text,color) #https://stackoverflow.com/questions/20842801/how-to-display-text-in-pygame
    
def displayBorder(offsetX,offsetY):
    #for the border, keep in mind that the offset is for the map inside. This means that the border's inner top left concave corner will be centered on the offset.
    blitLocationX=offsetX-unitSize;#these variables will track the location we will be blitting the sprites to.
    blitLocationY=offsetY-unitSize;
    for a in range(-1,visibleWidth):#the -1 and +1 should easily account for the offset.
        blitLocationX=blitLocationX+unitSize
        canvas.blit(borderTile,(blitLocationX,blitLocationY));
    for a in range(-1,visibleHeight):#right side
        blitLocationY=blitLocationY+unitSize
        canvas.blit(borderTile,(blitLocationX,blitLocationY));
    for a in range(-1,visibleWidth):#bottom 
        blitLocationX=blitLocationX-unitSize
        canvas.blit(borderTile,(blitLocationX,blitLocationY));
    for a in range(-1,visibleHeight):#left side 
        blitLocationY=blitLocationY-unitSize
        canvas.blit(borderTile,(blitLocationX,blitLocationY));
        
def displayMap(offsetX,offsetY):
    for a,rows in enumerate(visibleMap):
        for b,cols in enumerate(rows):
            #determine the tile to blit
            if(visibleMap[a][b]=="f"):
                blitTile=floorTile;
            elif(visibleMap[a][b]=="w"):
                blitTile=wallTile;
            elif(visibleMap[a][b]=="A"):
                blitTile=terrainATile;
            elif(visibleMap[a][b]=="B"):
                blitTile=terrainBTile;
            elif(visibleMap[a][b]=="C"):
                blitTile=terrainCTile;
            elif(visibleMap[a][b]=="D"):
                blitTile=terrainDTile;
            elif(len(visibleMap[a][b])<=1):#handle errors. after this only NPCs and Transition tiles will have more data. 
                blitTile=errorTile;
            elif(visibleMap[a][b][0]=="T"):
                transitionData=parseMapTileData(visibleMap[a][b]);#get the town data for checking.
                transTile=pygame.image.load("images/"+transitionData[0]);
                blitTile=transTile;
            elif(visibleMap[a][b][0]=="N"):
                npcData=parseMapTileData(visibleMap[a][b]);#get the town data for checking.
                NPCTile=pygame.image.load("images/"+npcData[0]);
                blitTile=NPCTile;
            elif(visibleMap[a][b][0]=="X"):
                blitTile=checkPointTile;
            else:
                blitTile=errorTile;
            canvas.blit(blitTile, (a*unitSize+offsetX,b*unitSize+offsetY));
    canvas.blit(playerTile, (viewOffsetX*unitSize+offsetX,viewOffsetY*unitSize+offsetY));#player the player's sprite int he middle of the screen
    displayBorder(offsetX,offsetY);#draw a pretty frame aroudnt he play area so it feels official

def intendedMoveCheck(intendedX, intendedY):
    global intendedMoveX,intendedMoveY,dialogFlag,state
    if((playerX+intendedX)<len(currentMapData) and (playerX+intendedX)>=0):
        if((playerY+intendedY)<len(currentMapData[0]) and (playerY+intendedY)>=0):
            tile=currentMapData[playerX+intendedX][playerY+intendedY]
            if tile[0]=="T":#transitions
                transition(parseMapTileData(tile));#this will load up the next section.
                intendedMoveX=0;#set the movement to 0 so we start on the correct tile. 
                intendedMoveY=0;
            if tile[0]=="N":#npcs
                dialogFlag=True;
                npcTileData=parseMapTileData(tile);
                loadDialog(npcTileData[1])#load the dialog file that will be the 2nd cell of the data.
                clearDialog();#clear before displating
                currentDialogLine=0;#go to the start of the NPC dialog list.
                currentDialogSelection=0;#go to the start of the players Options
                loadDialogOptions(currentDialogLine) #load up the dialog data for the line we are on (0 in this case)
                displayText(dialogNPCResponse,(250,250,254),dialogFont,unitSize,unitSize*(visibleHeight+4));    #show what the NPC has to say
                displayDialogOptions(); #display all the options the player has to respond. 
                blitSelectionArrow();#pop an arrow down for the player to see the current selection. 
                intendedMoveX=0;#set the movement to 0 so we start on the correct tile. 
                intendedMoveY=0;
                previousState=state;
                state="DIALOG";
            if(tile[0]=="X"):
                processCheckPoint(tile);
            if tile[0] in bumpList:#check to see if the tile is flagged for being unpassable
                bumpSound.play();
                return False;
            else:
                return True;
        else:
            return False;
    else:
        return False;

def processCheckPoint(data):
    global lastCheckpointMap,lastCheckPointCoords,lastCheckPointTileSet;
    if("heal" in data):
        print("healing the party!");
        healSound.play();
        for a in partyList:
            a.chp=a.mxhp;#set everyone back to thier max.
            #a.heal(99999);#top everyone up
            print("new hp for", a.name," is",a.chp,"out of ",a.mxhp);
    lastCheckPointTileSet=tileSetName;#name of our current tileset.       
    lastCheckpointMap=currentMapName; #name of the last map you hit a checkpoint on.
    lastCheckPointCoords=(playerX,playerY);#save our current locations.
    print("saving our checkpoint data as: ",lastCheckpointMap,lastCheckPointCoords);
        
###################################################################################################
####### Menu Functions#####################################################################################################
###################################################################################################
def displayMenusOptions():
    #print("showing pause options",pauseMenuOptions);
    for a in range(0,len(pauseMenuOptions)):
        displayText(pauseMenuOptions[a],(80,80,99),UIFont,combatUIOffsetX+unitSize,unitSize*(4+a)); #start the options nearish the middle .
        
def blitMenuArrow():
    #canvas.blit(clearArrow,(unitSize,unitSize*3));#clear out the previous arrow
    
    canvas.blit(selectionArrow,(combatUIOffsetX,unitSize*(4.15+currentPauseMenuSelection)));
    
def executeMenuSelection(menuSelection):
    global state;
    if(menuSelection=="Quit"):
        pygame.quit();
        quit();
    if(menuSelection=="Inventory"):
        previousState=state;
        state="INVENTORY";
    if(menuSelection=="Equipment"):
        previousState=state;
        state="EQUIPMENT"
    if(menuSelection=="Options"):
        print("There are no options at this time.");
    if(menuSelection=="Save"):
        print("No save function yet.");
###################################################################################################        
########## combat functions ################################################################################################################
###################################################################################################
def loadPartyTable(): #load up the table of enemy data. Keep it in memory
    global partyTable;
    try:
        datafile=open("playerStats.csv","r");
        partyTable=csv.reader(datafile,delimiter=",");
        partyTable=list(partyTable);# convert the csv object into a 2d array.
        for a in  range(0,len(partyTable)-1):
            for b in range(1,len(partyTable[a])): #we need to skip the first entry becuase its supposed to be string
                partyTable[a][b]=int(partyTable[a][b]);#save as a converted type.
                
    except Exception as e:
        print("Some villan has messed witht he partyStats table!",e)

def loadEnemiesTable(): #load up the table of enemy data. Keep it in memory
    global enemyTable;
    try:
        datafile=open("enemyDatabase.csv","r");
        enemyTable=csv.reader(datafile,delimiter=",");
        enemyTable=list(enemyTable);# convert the csv object into a 2d array.
        for a in  range(0,len(enemyTable)-1):
            for b in range(1,len(enemyTable[a])): #we need to skip the first entry becuase its supposed to be string
                enemyTable[a][b]=int(enemyTable[a][b]);#save as a converted type.
                
    except Exception as e:
        print("Some villan has messed witht he enemy table!",e)

def randomEncounter():
    global state,enemySelection,enemyList;
    #grab the per level stats from a database here. until then, use a generic one.
    if(random.randint(1,encounterRate)<=1): #1/20 chance of getting an encounter
        previousState=state;
        state="COMBAT1"#change our control state.
        encounterCount=random.randint(1,partySize);
        encounterList=[];
        #truly clear out everything.
        for a in enemyList:
            del a;
        enemyList=[];
        for a in range(0,encounterCount):#create a randomized list of enemies.
            encounterChoice=random.choice(currentEncounterTable);#pick a random enemy fromt he table.
            encounterList.append(encounterChoice);
            enemyList.append(actor(pygame.image.load("Images/monsters/FOE ("+str(encounterChoice+1)+").gif"),enemyTable[encounterChoice],a,True));
        print("wee woo wee woo! you are encountering this:",encounterList);
        for a in enemyList:
            print (a.name)
        enemyEncounterSound.play();
        loadCurrentEnemies(encounterList);
        enemySelection=-1;
        currentTurn=0;#reset the current turn to be at the start.
        displayCombatMenu();
        
def forceEncounter():
    global state,enemySelection,enemyList;
    #grab the per level stats from a database here. until then, use a generic one.
    if(True):
        previousState=state;
        state="COMBAT1"#change our control state.
        encounterCount=random.randint(1,partySize);
        encounterList=[];
        #truly clear out everything.
        for a in enemyList:
            del a;
        enemyList=[];
        for a in range(0,encounterCount):#create a randomized list of enemies.
            encounterChoice=random.choice(currentEncounterTable);#pick a random enemy fromt he table.
            encounterList.append(encounterChoice);
            enemyList.append(actor(pygame.image.load("Images/monsters/FOE ("+str(encounterChoice+1)+").gif"),enemyTable[encounterChoice],a,True));
        print("wee woo wee woo! you are encountering this:",encounterList);
        for a in enemyList:
            print (a.name)
        enemyEncounterSound.play();
        loadCurrentEnemies(encounterList);
        enemySelection=-1;
        currentTurn=0;#reset the current turn to be at the start.
        displayCombatMenu();

def getPartyStat(partyNumber,statToGet):#statToGet can be short stat string or a number. "name"=0,"str"=1,"def"=2,"spd"=3,"intl"=4,"wis"=5,"mxhp"=6,"chp"=7,"exp"=8
    if(statToGet=="name"):
        statToGet=0;
    elif(statToGet=="str"):
        statToGet=1;
    elif(statToGet=="def"):
        statToGet=2;
    elif(statToGet=="spd"):
        statToGet=3;
    elif(statToGet=="intl"):
        statToGet=4;
    elif(statToGet=="wis"):
        statToGet=5;
    elif(statToGet=="mxhp"):
        statToGet=6;
    elif(statToGet=="chp"):
        statToGet=7;
    elif(statToGet=="exp"):
        statToGet=8;
    elif(statToGet=="lvl"):
        statToGet=9;
    elif(statToGet=="wpn"):
        statToGet=10;
    elif(statToGet=="amr"):
        statToGet=11;
    elif(statToGet=="wnd"):
        statToGet=12;
    elif(statToGet=="ffld"):
        statToGet=13;
    return partyTable[partyNumber][statToGet];

def setPartyStat(partyNumber,statToGet,statToSet):#statToGet can be short stat string or a number. "name"=0,"str"=1,"def"=2,"spd"=3,"intl"=4,"wis"=5,"mxhp"=6,"chp"=7,"exp"=8
    if(statToGet=="name"):
        statToGet=0;
    elif(statToGet=="str"):
        statToGet=1;
    elif(statToGet=="def"):
        statToGet=2;
    elif(statToGet=="spd"):
        statToGet=3;
    elif(statToGet=="intl"):
        statToGet=4;
    elif(statToGet=="wis"):
        statToGet=5;
    elif(statToGet=="mxhp"):
        statToGet=6;
    elif(statToGet=="chp"):
        statToGet=7;
    elif(statToGet=="exp"):
        statToGet=8;
    elif(statToGet=="lvl"):
        statToGet=9;
    elif(statToGet=="wpn"):
        statToGet=10;
    elif(statToGet=="amr"):
        statToGet=11;
    elif(statToGet=="wnd"):
        statToGet=12;
    elif(statToGet=="ffld"):
        statToGet=13;
    partyTable[partyNumber][statToGet]=statToSet;

def getEnemyStat(enemyNumber,statToGet):#statToGet can be short stat string or a number. "name"=0,"str"=1,"def"=2,"spd"=3,"intl"=4,"wis"=5,"mxhp"=6,"chp"=7,"exp"=8
    referenceEnemy=currentEnemies[enemyNumber]
    if(statToGet=="name"):
        statToGet=0;
    elif(statToGet=="str"):
        statToGet=1;
    elif(statToGet=="def"):
        statToGet=2;
    elif(statToGet=="spd"):
        statToGet=3;
    elif(statToGet=="intl"):
        statToGet=4;
    elif(statToGet=="wis"):
        statToGet=5;
    elif(statToGet=="mxhp"):
        statToGet=6;
    elif(statToGet=="chp"):
        statToGet=7;
    elif(statToGet=="exp"):
        statToGet=8;
    elif(statToGet=="lvl"):
        statToGet=9;
    elif(statToGet=="wpn"):
        statToGet=10;
    elif(statToGet=="amr"):
        statToGet=11;
    elif(statToGet=="wnd"):
        statToGet=12;
    elif(statToGet=="ffld"):
        statToGet=13;
    #print("enemyNumber,statToGet",enemyNumber,statToGet);
    return currentEnemies[enemyNumber][statToGet];

def setEnemyStat(enemyNumber,statToGet,statToSet):#statToGet can be short stat string or a number. "name"=0,"str"=1,"def"=2,"spd"=3,"intl"=4,"wis"=5,"mxhp"=6,"chp"=7,"exp"=8
    referenceEnemy=currentEnemies[enemyNumber]
    if(statToGet=="name"):
        statToGet=0;
    elif(statToGet=="str"):
        statToGet=1;
    elif(statToGet=="def"):
        statToGet=2;
    elif(statToGet=="spd"):
        statToGet=3;
    elif(statToGet=="intl"):
        statToGet=4;
    elif(statToGet=="wis"):
        statToGet=5;
    elif(statToGet=="mxhp"):
        statToGet=6;
    elif(statToGet=="chp"):
        statToGet=7;
    elif(statToGet=="exp"):
        statToGet=8;
    elif(statToGet=="lvl"):
        statToGet=9;
    elif(statToGet=="wpn"):
        statToGet=10;
    elif(statToGet=="amr"):
        statToGet=11;
    elif(statToGet=="wnd"):
        statToGet=12;
    elif(statToGet=="ffld"):
        statToGet=13;
    currentEnemies[enemyNumber][statToGet]=statToSet;

def loadCurrentEnemies(enemyList):    #this function will pass a list of integers that correspond with the enemey types.
    global currentEnemies,enemyPictures,enemyCount,enemySelection;
    currentEnemies=[];#clear it out so we can fill it.
    enemyPictures=[];
    #enemySelection=-1;#when we start combat there should be no currently selected enemy.
    enemyCount=len(enemyList);
    enemyDisplayWidth=0;
    #enemySelection=-1;
    for a in range(0,enemyCount):
        enemyPictures.append(pygame.image.load("Images/monsters/FOE ("+str(enemyList[a]+1)+").gif"));#load the picture into the list of pics.
        enemyDisplayWidth=enemyDisplayWidth+enemyPictures[a].get_width();
        currentEnemies.append(list(enemyTable[enemyList[a]]));#get the nth enemy we are fighting, and find it in the table, and load that enemy's statblock into the current enemys.
    #combatCanvas.fill((5,5,5));
    canvas.blit(combatCanvas,(combatUIOffsetX,combatUIOffsetY));
    createTurnOrder();

def attackEnemy(target,attackingParty):
    hitEnemySound.play();
    defendingDef=getEnemyStat(target,"def");
    partyAttack=getPartyStat(attackingParty,"str");
    partyLevel=getPartyStat(attackingParty,"lvl");
    

    damage=(((partyAttack*(partyLevel/2))+partyWeapon)-(defendingDef/2))/2
    if(damage<=0):
        damage=1;#attacks should always do at least one damage.
    if(random.randint(0,20)==1):
        print("critical hit!");
        damage=damage*2;#critical hit!
    print("doing ", damage," damage to the foe!");




def attackParty(target,attackingEnemy):
    #print("attacking the party debug info",currentEnemies,attackingEnemy);
    defendingDef=getPartyStat(target,"def");
    enemyAttack=getEnemyStat(attackingEnemy,"str");
    enemyLevel=getEnemyStat(attackingEnemy,"lvl");
    partyArmor=getPartyStat(target,"amr");   
    damage=(((enemyAttack*(enemyLevel/2)))-((defendingDef+partyArmor)/2))/2
    if(damage<=0):
        damage=1;#attacks should always do at least one damage.
    if(random.randint(0,20)==1):
        print("critical hit!");
        damage=damage*2;#critical hit!
    print("doing ", damage," damage to partymember!",target);
    
    return damage;

def magicAttackEnemy(target,attackingParty):
    hitEnemySound.play();
    #defendingDef=getEnemyStat(target,"wis");
    #partyAttack=getPartyStat(attackingParty,"intl");

def clearTurnArrow():
    currentOffset=0;
    for a in range(0,enemyCount):
        currentOffset=currentOffset+enemyPictures[a].get_width()*.5;#offset by half
        combatCanvas.blit(turnArrowClear,(currentOffset,unitSize*4)); #plot a black square there to undo all the arrows
        #pygame.draw.rect(combatCanvas,(0,0,0),(currentOffset,unitSize*4,unitSize,unitSize));
        currentOffset=currentOffset+5+enemyPictures[a].get_width()*.5;#offset to the other half, to make a whole. (also add 5 for just some spacing.)
        
    for a in range(0,partySize):
        combatCanvas.blit(turnArrowClear,(50+(105*a),410)); #plot a black square above all our 
    #forceDisplayUpdate();

def displayTurnArrow(currentTurnNumber):
    currentOffset=0;
    clearTurnArrow();
    if(currentTurnNumber>=len(turnOrder)):#this is to fix a bug when you kill someone whos turn was at the end.
       currentTurnNumber=0;
           
    if(turnOrder[currentTurnNumber][0]=="e"):
        enemyNo=int(turnOrder[currentTurnNumber][1])
        for a in range(-1,enemyNo):
            currentOffset=currentOffset+enemyPictures[a].get_width()+5;#offset by all those other pics (and the 5 pixel buffer)
            #combatCanvas.blit(turnArrow,(currentOffset,unitSize*4)); #plot a black square there to undo all the arrows
        currentOffset=currentOffset-5-(enemyPictures[enemyNo].get_width()*.5);#offset by half the width, so that it is centered. (minus 5)   
        combatCanvas.blit(turnArrowEnemy,(currentOffset,unitSize*4));
            
    elif(turnOrder[currentTurnNumber][0]=="p"):#party member arrows are easier to calculate.
        combatCanvas.blit(turnArrowParty,(50+(105*int(turnOrder[currentTurnNumber][1])),410)); #our x value is calculated with a offset of 35 to help center it, and then a the paty number time 100.
    forceDisplayUpdate();
    #might want to update the cavnases and update the screen here.
        
#def displayHealthBar(locationX,locationY,currentValue,maxValue):
#    currentValue=clamp(currentValue,0,maxValue);    #sanatize inputs
#    percentage=currentValue/maxValue; #convert to a 0-1 value
#    pygame.draw.rect(combatCanvas,healthbarBackgroundColor,(locationX,locationY,healthbarMaxSize,unitSize*.5)); #draw background
#    lerpedColor=healthbarEndColor.lerp(healthbarStartColor,percentage); #determine the color of the bar
#    distance=lerp(healthbarMaxSize,0,percentage); #calculate how far the bar shifts over
#    pygame.draw.rect(combatCanvas,lerpedColor,(locationX+distance,locationY,healthbarMaxSize-distance,unitSize*.5));     #draw over the background the new bar.  

def combatCleanUp():
    global state,turnOrder,currentTurn,previousState;
    #awardEXP here
    #award Items here
    combatCanvas.fill((5,5,5));
    canvas.blit(combatCanvas,(combatUIOffsetX,combatUIOffsetY));
    currentTurn=0;
    enemyList=[];
    turnOrder=[];#clear out the turn order so it doesnt mess up the next time we build it.
    previousState=state;
    state="MAP";

def displayCombatMenuArrow():
    combatCanvas.blit(clearArrow,(0,enemyMenuDisplayOffsetY));
    combatCanvas.blit(selectionArrow,(0,enemyMenuDisplayOffsetY+(enemyMenuSelection*unitSize)));
  
def displayCombatMenu(): #write out the menu
    for a in range(0,len(combatMenuMainOptions)):
        displayCombatText(combatMenuMainOptions[a],(128,128,128),UIFont,unitSize,enemyMenuDisplayOffsetY+(a*unitSize)); #start the options nearish the middle .
    displayCombatMenuArrow();
    canvas.blit(combatCanvas,(combatUIOffsetX,combatUIOffsetY));

def checkCompletedEnemy():
    for a in enemyList:
        if(a.chp>0):
            return False;
    winSound.play();
    return True;

def sortTuple(tup): #this sorts tuples by thier 2nd element.
      return(sorted(tup, key = lambda x: x[1],reverse=True))  

def createTurnOrder():
    global turnOrder;
    listOfFightersAndSpeed=[];
    for a in range(0,len(currentEnemies)):
        listOfFightersAndSpeed.append(("e"+str(a),getEnemyStat(a,"spd")));
    for a in range(0,partySize):
        #if(partyList[a].chp>0):#taken this out, becuase we want dead party members in the turn order, so that if they get healed, they have turns.
        listOfFightersAndSpeed.append(("p"+str(a),getPartyStat(a,"spd")));
    listOfFightersAndSpeed=sortTuple(listOfFightersAndSpeed);
    for a in listOfFightersAndSpeed:
        turnOrder.append(a[0]);
    print("this is the turn order",turnOrder);

def updateText():#goes through our list of text objects, and removes them if they are past expiry date.
    for a in textEffectList:
        a.update();
        if(a.life<=0):
            textEffectList.remove(a);
            del a;

class actor():
    def __init__(self,image,statBlock,number,foeFlag):
        
        self.image=image;
        self.statBlock=statBlock;
        self.number=number;
        self.foeFlag=foeFlag;
        #set up stat block;
        self.name=statBlock[0];
        self.str=statBlock[1];
        self.defs=statBlock[2];
        self.spd=statBlock[3];
        self.intl=statBlock[4];
        self.wis=statBlock[5];
        self.mxhp=statBlock[6];
        self.chp=statBlock[7];
        self.exp=statBlock[8];
        self.lvl=statBlock[9];
        self.wpn=statBlock[10];
        self.amr=statBlock[11];
        self.wnd=statBlock[12];
        self.ffld=statBlock[13];#ward
        self.xCoord=540+self.number*(self.image.get_width()+5);
        if(self.foeFlag==False):#plop them down at top or bottomof the screen depending on if they are friend or foe.
            self.yCoord=partyVerticalOffset;#this is just a placeholder. this should be updated to reflect the current width of its previous people. 
        if(self.foeFlag==True):
            self.yCoord=unitSize;#this is just a placeholder. this should be updated to reflect the current width of its previous people. 
        self.alive=True;
        self.printZone=pygame.Surface((self.image.get_width(),self.image.get_width()+unitSize*.5))#create a canvas to work with the size of our image, plus a little extra for our health bar
        
    def display(self):
        self.printZone.blit(self.image,(0,0));#put our pretty picture up at the top.
        if(self.chp<=0):#check if we are still alive
            pygame.draw.line(self.printZone,(255,0,0),(0,0),(self.image.get_width(),self.image.get_height()),width=7);#cross out just the picture.
        #this draws a health bar under the image.    
        self.chp=clamp(self.chp,0,self.mxhp);#sanitize out health value. It doesnt need to be over max, or under min. 
        self.percentage=self.chp/self.mxhp;#turn to float.
        pygame.draw.rect(self.printZone,healthbarBackgroundColor,(0,self.image.get_height(),self.image.get_width(),unitSize*.5));#plot the background.
        self.lerpedColor=healthbarEndColor.lerp(healthbarStartColor,self.percentage); #determine the color of the bar
        self.distance=lerp(self.image.get_width(),0,self.percentage); #calculate how far the bar shifts over
        pygame.draw.rect(self.printZone,self.lerpedColor,(0,self.image.get_height(),self.image.get_width()-self.distance,unitSize*.5));     #draw over the background the new bar.  
        #end
        #draw Selection image
        if(enemySelection==self.number and self.foeFlag==True):
            self.printZone.blit(selectionImage,(10,10));#plot the target down on our current selection.
        #end
        updateText(); #if there is damage text to be shown, show it off now so it is on the top of the stack
        canvas.blit(self.printZone,(self.xCoord,self.yCoord));#slap this mess onto the combat canvas, where it belongs.. 
        
    def takeDamage(self,damageToTake):
        global partyList,enemyList
        self.chp=self.chp-damageToTake;
        textEffectList.append(risingText(str(damageToTake),(190,20,10),10,10,self));
        if(self.chp<=0):
            self.alive=False;
            if(self.foeFlag==True):
                enemyDeathSound.play();
            else:
                partyDeathSound.play();
        else:
            a=0;
            if(self.foeFlag==True):
               hitEnemySound.play();
            else:
               partyAttackSound.play();
            
    def heal(self,damageToHeal):
        self.chp=self.chp+damageToHeal;
        healSound.play();
        if(self.chp>=self.mxhp):
            self.chp=self.mxhp;

    def attack(self,target):
        self.damage=((self.str+self.wpn)-((target.defs+target.amr)/2))*(self.lvl/2)
        if(self.damage<=0):
            self.damage=1;#attacks should always do at least one damage.
        if(random.randint(0,20)==1):
            print("critical hit!");
            self.damage=self.damage*2;#critical hit!
        print("doing ", self.damage," damage to ",target.name);
        return self.damage;

    def gainExperience(self, expAmount):
        self.exp=self.exp+expAmount;
        previousLevel=self.lvl;
        self.lvl=math.floor(self.exp/(100+(10*self.lvl)));
        if(self.lvl>previousLevel):
            print("LEVEL UP! WOO");
            levelUpSound.play();
            self.chp=self.mxhp;#heal as a reward for leveling up!
        print("gaining experience for:",self.name,". Exp:",self.exp," level:",self.lvl);
            
class risingText:
    def __init__(self,text,color,xCoord,yCoord,actor):
        self.text=text;
        self.color=color;
        self.actor=actor;
        
        self.xCoord=xCoord+random.randint(-1*textRandomRange,textRandomRange);#add a little offset.
        self.yCoord=yCoord+random.randint(-1*textRandomRange,textRandomRange);
        self.life=textLifespan;
        #print("Creating a new floating text of string:",text," of color",color," at:",xCoord,yCoord);

    def update(self):
        self.yCoord=random.randint(0,10);#move the text up a bit.
        self.life=self.life-1;
        print("text output", (self.xCoord,self.yCoord));
        damageFont.render_to(self.actor.printZone,(self.xCoord,self.yCoord),self.text,self.color) #https://stackoverflow.com/questions/20842801/how-to-display-text-in-pygame

def checkPartyWipe():
    for a in partyList:
        if(a.chp>0):
            return False;
    return True;

def gameOver():
    global state,playerX, playerY;
    print("    --- YOU DIED ---   ");
    for a in partyList:
        a.chp=a.mxhp;
    loadMap(lastCheckpointMap);
    changeTileSet(lastCheckPointTileSet);
    playerX=lastCheckPointCoords[0];
    playerY=lastCheckPointCoords[1];
    combatCleanUp();#this will also set us back to MAP state.
    forceCombatDisplayUpdate();
    #show a game over splash screen for 5 seconds or something.
    viewMap(playerX,playerY); #update the screen
    displayMap(mapGUIOffsetx,mapGUIOffsetY); 

def turnOrderToActor(turnOrderPerson):
    if(turnOrderPerson[0]=="e"):#enemy
        return enemyList[int(turnOrderPerson[1])];
    if(turnOrderPerson[0]=="p"):#enemy
        return partyList[int(turnOrderPerson[1])];
    
######################################################################################################################################################################################################
########### Inventory Functions ##################################################################################################################
########################################################################################################################################################################################
    
def displayInventory(selection):
    if(len(currentInventory)==0):
        displayText("No items. oh boo :(",(20,20,45),UIFont,combatUIOffsetX+unitSize,unitSize*(4)); #start the options nearish the middle.
    if(len(currentInventory)<=8):
        for a in range(0,len(currentInventory)):
            if(a==invMenuSelection):
                displayText(currentInventory[a],(190,190,45),UIFont,combatUIOffsetX+unitSize,unitSize*(4+a)); #display with a selection
            else:
                displayText(currentInventory[a],(80,80,99),UIFont,combatUIOffsetX+unitSize,unitSize*(4+a)); #display the item name normally
        displayText("Page 1 of 1",(99,99,99),UIFont,combatUIOffsetX+unitSize,unitSize*(4+inventoryPageSize+1)); #display the static page number
    else:
        #print("printing big list",selection);
        for a in range(0,inventoryPageSize):
            indexOfItemToPrint=int(currentInventoryPage*inventoryPageSize)+a
            if(indexOfItemToPrint>=len(currentInventory)):#this is a failsafe.
                break #dont bother keeping going.
            #print("inventory number,",indexOfItemToPrint,"inventory size",len(currentInventory));
            if(indexOfItemToPrint==invMenuSelection):
                displayText(currentInventory[indexOfItemToPrint],(190,190,45),UIFont,combatUIOffsetX+unitSize,unitSize*(4+a)); #display with a selection
            else:
                displayText(currentInventory[indexOfItemToPrint],(80,80,99),UIFont,combatUIOffsetX+unitSize,unitSize*(4+a)); #display the item name normally
        displayText("Page "+str(currentInventoryPage+1)+" of "+str(1+math.floor(len(currentInventory)/inventoryPageSize)),(99,99,99),UIFont,combatUIOffsetX+unitSize,unitSize*(4+inventoryPageSize+1)); #display the page number

def useItem(item):
    global currentInventory,invMenuSelection,state;
    if(item=="Weak Potion"):
        itemUser=getItemTarget();
        itemUser.heal(10);
    if(item=="Strong Potion"):
        itemUser=getItemTarget();
        itemUser.heal(20);
        
    currentInventory.pop(invMenuSelection);
    invMenuSelection=invMenuSelection-1;#since we took an item, shift our current selection back one.
    if(invMenuSelection<0):
        invMenuSelection=0;
    if(previousState=="COMBAT2"):#end the user's turn after using an item.
        state=previousState;

def getItemTarget():
    finalTarget=-1;#get ourselves trapped in a loop.
    currentTargetSelection=0;
    while(finalTarget==-1):
        for event in pygame.event.get():
            if(event.type==pygame.KEYDOWN ): #only allow movement if we are not talking or fighting. (or people could run away)
                if(event.key==pygame.K_UP):
                    currentTargetSelection=(currentTargetSelection-1)%partySize;
                if(event.key==pygame.K_DOWN):
                    currentTargetSelection=(currentTargetSelection+1)%partySize;
                if(event.key==pygame.K_RETURN):
                    finalTarget=currentTargetSelection;#finalize out selection
                    combatCanvas.fill((5,5,5));
                    canvas.blit(combatCanvas,(combatUIOffsetX,combatUIOffsetY));#clear the screen.
                    return partyList[finalTarget];
            for a in partyList:
                if(a.number==currentTargetSelection):
                    displayText(a.name+" ("+str(a.chp)+"/"+str(a.mxhp)+")",(190,190,45),UIFont,combatUIOffsetX+unitSize,unitSize*(4+a.number)); #display with a selection
                else:
                    displayText(a.name+" ("+str(a.chp)+"/"+str(a.mxhp)+")",(90,90,45),UIFont,combatUIOffsetX+unitSize,unitSize*(4+a.number)); #display the item name normally
        window.blit(canvas,(0,0))#write new pixels to display
        pygame.display.update()#draw
        time.sleep(0.01)#unfuck the CPU
       

##############################################################################################################################################################################
##############################################################################################################################################################################
##############################################################################################################################################################################
#################################################################            Game Loop           #############################################################################
##############################################################################################################################################################################
##############################################################################################################################################################################
##############################################################################################################################################################################
##############################################################################################################################################################################
##############################################################################################################################################################################


### Game start
loadEnemiesTable(); #preload our enemies so they have some place to be referenced.
loadPartyTable();
loadMap("plains2");
#print ("your map:\n",currentMapData);
viewMap(playerX,playerY);
displayMap(mapGUIOffsetx,mapGUIOffsetY);
displayText("Neoquest 3",(170,150,50),UIFont,unitSize,unitSize*(visibleHeight+3));
clearDialog();


#load the players. this is temporary, and might be approached appropriately in the future

if(partySize>=1):
    partyList.append(actor(jeranNeutral,partyTable[0],0,False));
if(partySize>=2):
    partyList.append(actor(lishaNeutral,partyTable[1],1,False));
if(partySize>=3):
    partyList.append(actor(kassNeutral,partyTable[2],2,False));
if(partySize>=4):
    partyList.append(actor(kaylaNeutral,partyTable[3],3,False));


##########   game loop  ###########
while(1):
    firstTimeInState=True;
    while (state=="MAP"):
        if(firstTimeInState):
            window.blit(canvas,(0,0))#write new pixels to display
            pygame.display.update()#draw
            time.sleep(0.01)#unfuck the CPU
            firstTimeInState=False;
        onceFlag=False;
        for event in pygame.event.get():
            #### handle map navigation mode inputs.
            intendedMoveX=0;#reset the intended movement at the end of processing. 
            intendedMoveY=0;
            if(event.type==pygame.KEYDOWN ): #only allow movement if we are not talking or fighting. (or people could run away)
                if(event.key==pygame.K_LEFT):
                    intendedMoveX=-1;
                if(event.key==pygame.K_RIGHT):
                    intendedMoveX=1;
                if(event.key==pygame.K_UP):
                    intendedMoveY=-1;
                if(event.key==pygame.K_DOWN):
                    intendedMoveY=1;
                if(event.key==pygame.K_p):#########################################################################Secret debug stuff.
                    forceEncounter();
               #update the view map.
                if(intendedMoveX!=0 or intendedMoveY!=0):
                    if(intendedMoveCheck(intendedMoveX,intendedMoveY)):  
                        playerX=playerX+intendedMoveX;#commit the intentions 
                        playerY=playerY+intendedMoveY;
                        if(intendedMoveX==-1):
                            playerTile=playerTileLeft;
                        elif(intendedMoveX==1):
                            playerTile=playerTileRight;
                        viewMap(playerX,playerY);
                        displayMap(mapGUIOffsetx,mapGUIOffsetY);
                        if(onceFlag==False):
                            randomEncounter();
                            onceFlag=True;
                else:
                    bumpSound.play();
                if(event.key==pygame.K_ESCAPE):
                    previousState=state;
                    state="MENU";
            if(event.type==pygame.QUIT): #code for closing the window whent he X button is pressed
                pygame.quit();
        updateText();
        window.blit(canvas,(0,0))#write new pixels to display
        pygame.display.update()#draw
        time.sleep(0.01)#unfuck the CPU
    while (state=="SHOPPING"):
         for event in pygame.event.get():
            if(event.type==pygame.KEYDOWN):
                if(event.key==pygame.K_UP):
                    currentShoppingSelection=currentShoppingSelection-1;
                    currentShoppingSelection=(currentShoppingSelection%shopOptionCount)
                    blitSelectionArrow();
                if(event.key==pygame.K_DOWN):
                    currentShoppingSelection=currentShoppingSelection+1;
                    currentShoppingSelection=(currentShoppingSelection%shopOptionCount)
                    blitSelectionArrow();
                if(event.key==pygame.K_RETURN):
                    print("locking in selection:",currentShoppingSelection);
                    try:
                        clearDialog();#clear before displating
                        currentDialogLine=int(float(dialogDestinations[currentDialogSelection]))-1;#update the current dialog line based on the selection. Then subtract one because the dialog file is 1 indexed.
                        loadDialogOptions(currentDialogLine) #load up the data for the line we are on

                        #this is the part where we process any dialog actions. Strip the #tag from the response each time.

                        #now that we have processed any effects, we can display things. 
                        displayText(dialogNPCResponse,(250,250,254),dialogFont,unitSize,unitSize*(visibleHeight+4));    #show what the NPC has to say
                        displayDialogOptions(); #display all the options the player has to respond. 
                        currentDialogSelection=0;#return to the top of the options. 
                        blitSelectionArrow()
                        currentDialogSelection=0;#go back to top for the new page of dialog
                        
                    except Exception as e:
                        print(e);
                        print("aw fudge.");

            ####Quitting the game
            if(event.type==pygame.QUIT): #code for closing the window whent he X button is pressed
                pygame.quit();
            updateText();
            window.blit(canvas,(0,0))#write new pixels to display
            pygame.display.update()#draw
            time.sleep(0.01)#unfuck the CPU

        
    while (state=="DIALOG"):
        if(firstTimeInState):
            window.blit(canvas,(0,0))#write new pixels to display
            pygame.display.update()#draw
            time.sleep(0.01)#unfuck the CPU
            firstTimeInState=False;
        ####handle dialog mode inputs
        for event in pygame.event.get():
            if(event.type==pygame.KEYDOWN):
                print("selection",currentDialogSelection);
                if(event.key==pygame.K_UP):
                    currentDialogSelection=currentDialogSelection-1;
                    currentDialogSelection=(currentDialogSelection%optionCount)
                    #currentDialogLine=int(float(dialogDestinations[currentDialogSelection]))-1#Then subtract one because the dialog file is 1 indexed.
                    blitSelectionArrow();
                if(event.key==pygame.K_DOWN):
                    currentDialogSelection=currentDialogSelection+1;
                    currentDialogSelection=(currentDialogSelection%optionCount)
                    #currentDialogLine=int(float(dialogDestinations[currentDialogSelection]))-1#Then subtract one because the dialog file is 1 indexed.
                    blitSelectionArrow();
                if(event.key==pygame.K_RETURN):
                    print("locking in selection:",currentDialogSelection);
                    try:
                        clearDialog();#clear before displating
                        currentDialogLine=int(float(dialogDestinations[currentDialogSelection]))-1;#update the current dialog line based on the selection. Then subtract one because the dialog file is 1 indexed.
                        loadDialogOptions(currentDialogLine) #load up the data for the line we are on

                        #this is the part where we process any dialog actions. Strip the #tag from the response each time.
                        
                        if("#HEAL" in dialogNPCResponse):#this lets us escape the dialog.
                            dialogNPCResponse=dialogNPCResponse.replace("#HEAL","");
                            print(dialogNPCResponse);
                            print("healing the party!");
                            healSound.play();
                            for a in partyList:
                                a.chp=a.mxhp;#set everyone back to thier max.
                                #a.heal(99999);#top everyone up
                                print("new hp for", a.name," is",a.chp,"out of ",a.mxhp);
                        if("#EOF" in dialogNPCResponse):#this lets us escape the dialog.
                            dialogNPCResponse=dialogNPCResponse.replace("#EOF","");
                            previousState=state;
                            state="MAP";
                            clearDialog();
                        #now that we have processed any effects, we can display things. 
                        displayText(dialogNPCResponse,(250,250,254),dialogFont,unitSize,unitSize*(visibleHeight+4));    #show what the NPC has to say
                        displayDialogOptions(); #display all the options the player has to respond. 
                        currentDialogSelection=0;#return to the top of the options. 
                        blitSelectionArrow()
                        currentDialogSelection=0;#go back to top for the new page of dialog
                        
                    except Exception as e:
                        print(e);
                        print("aw fudge.");
            #clearDialog();
            #displayText(dialogOptions[currentDialogSelection],(250,250,254),dialogFont,unitSize,unitSize*(visibleHeight+6));
            
            ####Quitting the game
            if(event.type==pygame.QUIT): #code for closing the window whent he X button is pressed
                pygame.quit();
        updateText();
        window.blit(canvas,(0,0))#write new pixels to display
        pygame.display.update()#draw
        time.sleep(0.01)#unfuck the CPU




    while(state=="COMBAT1"):#phase one of combat, figure out who's turn it is. If it is an enemy turn, they should do an attack on a random party member.
        if(firstTimeInState):
            window.blit(canvas,(0,0))#write new pixels to display
            pygame.display.update()#draw
            time.sleep(0.01)#unfuck the CPU
            firstTimeInState=False;
        print("it's this persons turn right now!",turnOrderToActor(turnOrder[currentTurn]).name);
        displayTurnArrow(currentTurn);#display turn arrow, but set clear to false.
        if(turnOrder[currentTurn][0]=="e"):
            if(delayTimer<=0):
                delayTimer=100#how many loops to do
                forceCombatDisplayUpdate();
    
                targetedParty=random.randint(0,partySize-1);#minus one to account for 0 index.
                while(partyList[targetedParty].chp==0):
                    targetedParty=random.randint(0,partySize-1);#just keep picking till we find one with health. This could theoretically lead to a hang or infinite loop, but with 1/4th odd, i will take those chances. 
                partyList[targetedParty].takeDamage(enemyList[int(turnOrder[currentTurn][1])].attack(partyList[targetedParty]));#deal damage to our party actor
                #setPartyStat(targetedParty,"chp",getPartyStat(targetedParty,"chp")-attackParty(targetedParty,int(turnOrder[currentTurn][1])));
                partyAttackSound.play();
                if(checkPartyWipe()):
                    gameOver();#game over function
                    
                    break;
                forceCombatDisplayUpdate();
                displayTurnArrow(currentTurn);#clear the arrow before moving to the next one.
                forceCombatDisplayUpdate();
                currentTurn=(currentTurn+1)%(len(turnOrder));
                while(turnOrderToActor(turnOrder[currentTurn]).chp<=0):
                    print("turn order shenanigeans",turnOrder,currentTurn);
                    currentTurn=(currentTurn+1)%(len(turnOrder));#increment but loop the turn order.
            else: #if the timer is not less than 0;
                delayTimer=delayTimer-1;
        elif(turnOrder[currentTurn][0]=="p"):
            #save the partymember whose turn it is, and
            enemyMenuSelection=0;
            previousState=state;
            state="COMBAT2";
        else:
            print("turn order is broken! Malformed turnOrder entry",turnOrder[currentTurn]);


    while (state=="COMBAT2"): #Allow the player to choose what that party member does on thier turn.
        if(firstTimeInState):
            window.blit(canvas,(0,0))#write new pixels to display
            pygame.display.update()#draw
            time.sleep(0.01)#unfuck the CPU
            firstTimeInState=False;
        for event in pygame.event.get():
            if(event.type==pygame.KEYDOWN): #only allow movement if we are not talking or fighting. (or people could run away)
                if(event.key==pygame.K_j):
                    print("you win!");
                    combatCleanUp();
                if(event.key==pygame.K_UP):
                    enemyMenuSelection=enemyMenuSelection-1;
                    enemyMenuSelection=(enemyMenuSelection%len(combatMenuMainOptions));
                    displayCombatMenu();
                if(event.key==pygame.K_DOWN):
                    enemyMenuSelection=enemyMenuSelection+1;
                    enemyMenuSelection=(enemyMenuSelection%len(combatMenuMainOptions));
                    displayCombatMenu();
                    ###########################################################
                if(event.key==pygame.K_1):
                    partyList[0].takeDamage(5);
                if(event.key==pygame.K_2):
                    partyList[1].takeDamage(5);############Secret debug stuff.
                if(event.key==pygame.K_3):
                    partyList[2].takeDamage(5);
                if(event.key==pygame.K_4):
                    partyList[3].takeDamage(5);
                if(event.key==pygame.K_5):
                    enemyList[0].takeDamage(5);
                if(event.key==pygame.K_6):
                    enemyList[1].takeDamage(5);############Secret debug stuff.
                if(event.key==pygame.K_7):
                    enemyList[2].takeDamage(5);
                if(event.key==pygame.K_8):
                    enemyList[3].takeDamage(5);
                    ######################################################
                if(event.key==pygame.K_RETURN):
                    if(enemyMenuSelection==0):# we have selected attack. Move to the next phase.
                        enemySelection=-1;#start with the -1 so our do while starts at 0
                        while True:#do while! Use this to skip over dead enemies.       
                            enemySelection=(enemySelection+1)%enemyCount;
                            if(enemyList[enemySelection].chp>0):
                                break;#automatically select the first one.
                        previousState=state; 
                        state="COMBAT3";
                    if(enemyMenuSelection==1):# we have selected spells.
                        print("you dont know any spells");
                    if(enemyMenuSelection==2):# we have selected run.
                        if(random.randint(0,getPartyStat(0,"spd")!=1)):
                            print("you ran away!");
                            combatCleanUp();
                    if(enemyMenuSelection==3):# we have selected item. Move to the next phase.
                        previousState=state;
                        state="COMBATINVENTORY";
            if(event.type==pygame.QUIT): #code for closing the window whent he X button is pressed
                pygame.quit();
        for a in partyList:
            a.display();
        for a in enemyList:
            a.display();   
        window.blit(canvas,(0,0))#write new pixels to display
        pygame.display.update()#draw
        time.sleep(0.01)#unfuck the CPU

    while (state=="COMBAT3"): #now allow the player to select the enemy being attacked. 
        if(firstTimeInState):
            window.blit(canvas,(0,0))#write new pixels to display
            pygame.display.update()#draw
            time.sleep(0.01)#unfuck the CPU
            firstTimeInState=False;
        for event in pygame.event.get():
            if(event.type==pygame.KEYDOWN): #only allow movement if we are not talking or fighting. (or people could run away)
                if(event.key==pygame.K_j):
                    print("you win!");
                    combatCleanUp();
                if(event.key==pygame.K_LEFT):
                    while True:#do while! Use this to skip over dead enemies.       
                        enemySelection=(enemySelection-1)%enemyCount;
                        if(enemyList[enemySelection].chp>0):
                            break;
                if(event.key==pygame.K_RIGHT):
                    while True:#do while! Use this to skip over dead enemies.
                        enemySelection=(enemySelection+1)%enemyCount;
                        if(enemyList[enemySelection].chp>0):
                            break;
                if(event.key==pygame.K_RETURN):
                    if(enemySelection>=0 and enemySelection<enemyCount and enemyList[enemySelection].chp>0):
                        if(enemyMenuSelection==0):#check what our selection was, becuase thats what we will do next.
                            #attack animation?
                            enemyList[enemySelection].takeDamage(partyList[int(turnOrder[currentTurn][1])].attack(enemyList[enemySelection]));#this will need to be reworked later to use a list of the actor objects, rather than a intified string.
                            if(getEnemyStat(enemySelection,"chp")<=0):#that means we killed it!
                                enemyDeathSound.play();
                                partyList[int(turnOrder[currentTurn][1])].gainExperience(1);#give the player who murdered experience
                                turnOrder.remove("e"+str(enemySelection));#once it is dead, remove it from the turn order.
                            #displayTurnArrow(currentTurn,True);
                            enemySelection=-1;#clear the circle until its the next party member's turn.
                            
                        if(enemyMenuSelection==1):#spells
                            print("lightnig bolt!");
                        #displayEnemies();#update the results of our attack
                        #displayParty();
                        if(checkCompletedEnemy()): #also check to see if everyone is dead.
                            for a in enemyList:
                                for b in partyList:
                                    b.gainExperience(a.exp);
                            combatCleanUp();
                            print("you win! the state is now ",state);
                        else:
                            displayTurnArrow(currentTurn);#clear it out before the next person.
                            currentTurn=(currentTurn+1)%(len(turnOrder));
                            while(turnOrderToActor(turnOrder[currentTurn]).chp<=0):
                                print("turn order shenanigeans",turnOrder,currentTurn);
                                currentTurn=(currentTurn+1)%(len(turnOrder));#increment but loop the turn order.
                            enemySelection=-1;#clear the selection circle.
                            previousState=state;
                            state="COMBAT1";#return to the first compbat phase to find out who goes next.
                    else:
                        invalidSelectionSound.play();#either the enemy selected isnt alive, or the selection ring isnt on an enemy yet. (somehow)
            if(event.type==pygame.QUIT): #code for closing the window whent he X button is pressed
                pygame.quit();
        if(state=="COMBAT3"):#this is to check that we dont draw the actors after the combat is over
            for a in partyList:
                a.display();
            for a in enemyList:
                a.display();
        window.blit(canvas,(0,0))#write new pixels to display
        pygame.display.update()#draw
        time.sleep(0.01)#unfuck the CPU


    while (state=="MENU"):
        if(firstTimeInState):
            window.blit(canvas,(0,0))#write new pixels to display
            pygame.display.update()#draw
            time.sleep(0.01)#unfuck the CPU
            firstTimeInState=False;
        displayMenusOptions();
        for event in pygame.event.get():
            #### handle map navigation mode inputs.
            if(event.type==pygame.KEYDOWN): #only allow movement if we are not talking or fighting. (or people could run away)
                if(event.key==pygame.K_UP):
                    currentPauseMenuSelection=currentPauseMenuSelection-1;
                    currentPauseMenuSelection=(currentPauseMenuSelection%len(pauseMenuOptions));
                if(event.key==pygame.K_DOWN):
                    currentPauseMenuSelection=currentPauseMenuSelection+1;
                    currentPauseMenuSelection=(currentPauseMenuSelection%len(pauseMenuOptions));
                if(event.key==pygame.K_ESCAPE):
                    previousState=state;
                    state="MAP";#return to the map state loop.
                    viewMap(playerX,playerY);
                    displayMap(mapGUIOffsetx,mapGUIOffsetY);
                    #blit to canvas what the screen looked like before pausing. 
                if(event.key==pygame.K_RETURN):
                    executeMenuSelection(pauseMenuOptions[currentPauseMenuSelection]);#pass the next of the menu selection, becuase it's dynamic.
            ####Quitting the game
            if(event.type==pygame.QUIT): #code for closing the window whent he X button is pressed
                pygame.quit();
        updateText();
        blitMenuArrow();
        window.blit(canvas,(0,0))#write new pixels to display
        pygame.display.update()#draw
        time.sleep(0.01)#unfuck the CPU
        combatCanvas.fill((5,5,5));
        canvas.blit(combatCanvas,(combatUIOffsetX,combatUIOffsetY));

    while(state=="INVENTORY"): #when going to this state, it is important to know what the previous state was. make sure you save it under "previousState" before moving here.
        if(firstTimeInState):
            window.blit(canvas,(0,0))#write new pixels to display
            pygame.display.update()#draw
            time.sleep(0.01)#unfuck the CPU
            firstTimeInState=False;
        for event in pygame.event.get():  
            if(event.type==pygame.KEYDOWN):
                combatCanvas.fill((5,5,5));
                canvas.blit(combatCanvas,(combatUIOffsetX,combatUIOffsetY));
                if(event.key==pygame.K_ESCAPE):
                    state=previousState;#return to the map state loop.
                    combatCanvas.fill((5,5,5));
                    canvas.blit(combatCanvas,(combatUIOffsetX,combatUIOffsetY));
                    viewMap(playerX,playerY);
                    displayMap(mapGUIOffsetx,mapGUIOffsetY);
                if(event.key==pygame.K_UP and len(currentInventory)>0): #also account that we shouldnt be able to use an empty inventory 
                    invMenuSelection=(invMenuSelection-1)%len(currentInventory);
                if(event.key==pygame.K_DOWN and len(currentInventory)>0): #also account that we shouldnt be able to use an empty inventory 
                    invMenuSelection=(invMenuSelection+1)%len(currentInventory);
                if(event.key==pygame.K_RETURN and len(currentInventory)>0): #also account that we shouldnt be able to use an empty inventory 
                    useItem(currentInventory[invMenuSelection]);
                currentInventoryPage=math.floor(invMenuSelection/inventoryPageSize)#this will tells us what page we are on based on the page size.
                #canvas.fill((5,5,5)); #clear out the display so we can clearly see our text
                displayInventory(invMenuSelection);
            window.blit(canvas,(0,0))#write new pixels to display
            pygame.display.update()#draw
            time.sleep(0.01)#unfuck the CPU
            
    while(state=="COMBATINVENTORY"): #when going to this state, it is important to know what the previous state was. make sure you save it under "previousState" before moving here.
        if(firstTimeInState):
            window.blit(canvas,(0,0))#write new pixels to display
            pygame.display.update()#draw
            time.sleep(0.01)#unfuck the CPU
            firstTimeInState=False;
        for event in pygame.event.get():  
            if(event.type==pygame.KEYDOWN):
                combatCanvas.fill((5,5,5));
                canvas.blit(combatCanvas,(combatUIOffsetX,combatUIOffsetY));
                if(event.key==pygame.K_ESCAPE):
                    state=previousState;#return to the map state loop.
                    combatCanvas.fill((5,5,5));
                    canvas.blit(combatCanvas,(combatUIOffsetX,combatUIOffsetY));
                    viewMap(playerX,playerY);
                    displayMap(mapGUIOffsetx,mapGUIOffsetY);
                if(event.key==pygame.K_UP and len(currentInventory)>0): #also account that we shouldnt be able to use an empty inventory 
                    invMenuSelection=(invMenuSelection-1)%len(currentInventory);
                if(event.key==pygame.K_DOWN and len(currentInventory)>0): #also account that we shouldnt be able to use an empty inventory 
                    invMenuSelection=(invMenuSelection+1)%len(currentInventory);
                if(event.key==pygame.K_RETURN and len(currentInventory)>0): #also account that we shouldnt be able to use an empty inventory 
                    useItem(currentInventory[invMenuSelection]);#Use the Item
                    displayTurnArrow(currentTurn);#and then make it the next persons turn
                    currentTurn=(currentTurn+1)%(len(turnOrder));
                    while(turnOrderToActor(turnOrder[currentTurn]).chp<=0):
                        print("turn order shenanigeans",turnOrder,currentTurn);
                        currentTurn=(currentTurn+1)%(len(turnOrder));#increment but loop the turn order.
                    enemySelection=-1;#clear the selection circle.
                    previousState=state;
                    state="COMBAT1";#return to the first compbat phase to find out who goes next.
                currentInventoryPage=math.floor(invMenuSelection/inventoryPageSize)#this will tells us what page we are on based on the page size.
                #canvas.fill((5,5,5)); #clear out the display so we can clearly see our text
                displayInventory(invMenuSelection);
            window.blit(canvas,(0,0))#write new pixels to display
            pygame.display.update()#draw
            time.sleep(0.01)#unfuck the CPU
                           


#current issues:
    #should save the visual frame of what the canvas looks like before pausing, to immedeatly display it after unpausing. otherwise a black screen shows.
    #add menu navigation.


