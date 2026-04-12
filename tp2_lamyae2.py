############################# 
# tp2 #
# Your name: Lamyae El Bouchikhi
# Your andrew id: lelbouch
#################################################

#TP1 - Scotty Texas Hold'em
from cmu_graphics import *
import random

# Constants for better organization
buttonWidth = 140
buttonHeight = 60
buttonSpacing = 40

#Setting up the window and starting the game
def playTexasHoldem():
    runApp(800, 600)

def onAppStart(app):
    app.mode = "start"
    app.width = 800
    app.height = 600
    app.pot = 0
    app.deck = createDeck() # create deck ONCE
    app.myCards = getMyCards(app) # deal cards ONCE
    
    # Phase system
    app.phase = "preflop"
    app.communityCards = []
    app.actionsThisRound = 0
    
    # NEW: Player state tracking
    app.foldedPlayers = [False, False, False, False]  # Tracks who folded
    app.hasBetThisRound = False  #track if anyone bet this round
    app.lastActions = ["", "", "", ""]  #stores last action for each player
    app.minBet = 20 
    app.amountsBetThisRound = [0, 0, 0, 0]
    app.playerCards = [
        getPlayerCards(app),
        getPlayerCards(app),
        getPlayerCards(app),
        app.myCards
        ]
    
    #player data structure
    app.playersData = [
        {'name': 'Player1', 'money': 2000},
        {'name': 'Player2', 'money': 2000}, 
        {'name': 'Player3', 'money': 2000},
        {'name': 'You', 'money': 2000}
    ]
    app.players = ['p1', 'p2', 'p3', 'you']
    app.currentPLayer = app.players[0]
    app.raiseAmount = 30  #default raise amount
    app.callAmount = 20   # Amount needed to call
    app.currentPlayerIndex = 0 # index in players list
    app.turnTimer = 0 # counts time
    app.waitingForPlayer = False # only true when it's YOUR turn

def onKeyPress(app, key):
    if key=='s' and app.mode=="start":
        app.mode="play"
    if app.mode == "showwinners" and key.lower() == "r":
        startNextRound(app)
        
def startNextRound(app):
    #Resets state for new round but keeps player balances
    #Remove players with no money
    indicesToRemove = []
    for i in range(len(app.playersData)):
        player = app.playersData[i]
        if player['money'] <= 0:
            app.foldedPlayers[i] = True
            indicesToRemove.append(i)
    # Reset deck, hands, community cards
    app.deck = createDeck()
    random.shuffle(app.deck)
    app.myCards = getMyCards(app)
    
    app.communityCards = []
    app.pot = 0
    app.foldedPlayers = [False if i not in indicesToRemove else True for i in range(4)]
    app.lastActions = ["", "", "", ""]
    app.amountsBetThisRound = [0, 0, 0, 0]
    app.phase = "preflop"
    app.currentPlayerIndex = 0
    app.mode = "play"
    app.playerCards = [
        getPlayerCards(app),
        getPlayerCards(app),
        getPlayerCards(app),
        app.myCards
        ]
    

def onStep(app):
    if app.mode != "play":
        return
        
    currentIndex = app.currentPlayerIndex
    
    #Skips folded players
    if app.foldedPlayers[currentIndex]:
        app.actionsThisRound += 1
        advanceTurn(app)
        return
    
    # If it's YOU then wait for click (do nothing here)
    if currentIndex == 3:
        app.waitingForPlayer = True
        return
        
    # bot player timer
    app.turnTimer += 1
    #waits for arnd 3 seconds
    if app.turnTimer >= 50:
        botAction(app)
        advanceTurn(app)

def botAction(app):
    
    playerIndex = app.currentPlayerIndex
    
    #for randomness
    #prints a float between 0 and 100
    rand = random.random() * 100
    
    #Checks if checking option is available (no one has bet this round)
    canCheck = not app.hasBetThisRound
    
    if canCheck and rand < 30 and app.phase != 'preflop':  # 30% check if available
        #CHECK
        app.lastActions[playerIndex] = "Check"
        app.actionsThisRound += 1
        
    elif rand < 85:  # 55% call (85-30=55% when check available, 85% when theyre not)
        #CALL
        if app.callAmount <= app.playersData[playerIndex]['money']:
            app.pot += app.callAmount
            app.playersData[playerIndex]['money'] -= app.callAmount
            app.lastActions[playerIndex] = f"Call ${app.callAmount}"
            app.hasBetThisRound = True
            app.amountsBetThisRound[playerIndex] = app.callAmount
        else:
            # Fold if can't afford to call
            app.foldedPlayers[playerIndex] = True
            app.lastActions[playerIndex] = "Fold"
            app.amountsBetThisRound[playerIndex] = 'f'
        app.actionsThisRound += 1
        
    elif rand < 95:  # 10% raise
        # RAISE
        raiseAmount = random.choice([30, 40, 50, 60])  # Random raise amounts
        totalBet = app.callAmount + raiseAmount
        
        if totalBet <= app.playersData[playerIndex]['money']:
            app.pot += totalBet
            app.amountsBetThisRound[playerIndex] = totalBet
            app.maxBet = totalBet
            app.playersData[playerIndex]['money'] -= totalBet
            app.callAmount = totalBet  # Update call amount for other players
            app.lastActions[playerIndex] = f"Raise +${raiseAmount}"
            app.hasBetThisRound = True
        else:
            # Call instead if can't afford to raise
            if app.callAmount <= app.playersData[playerIndex]['money']:
                app.amountsBetThisRound[playerIndex] = app.callAmount
                app.pot += app.callAmount
                app.playersData[playerIndex]['money'] -= app.callAmount
                app.lastActions[playerIndex] = f"Call ${app.callAmount}"
                app.hasBetThisRound = True
            else:
                app.foldedPlayers[playerIndex] = True
                app.lastActions[playerIndex] = "Fold"
        app.actionsThisRound += 1
        
    else: # 5% fold
        # FOLD
        app.foldedPlayers[playerIndex] = True
        app.lastActions[playerIndex] = "Fold"
        app.actionsThisRound += 1
        app.amountsBetThisRound[playerIndex] = 'f'
        
        
def roundCanNotRepeat(app):
    amount = None
    
    for money in app.amountsBetThisRound:
        if money == 'f':
            continue
        if amount is None:
            amount = money
        elif money != amount:
            return False
    
    return True

def advanceTurn(app):
    #Advance to next player or next phase
    # Counting active players
    activePlayers = 0
    for folded in app.foldedPlayers:
        if not folded:
            activePlayers += 1
    
    #If only one player left, end game #to be modified
    if activePlayers <= 1:
        app.mode = "gameover"
        return
    
    #Checking if all active players have acted this round
    if app.actionsThisRound >= 4 and roundCanNotRepeat(app):
        advancePhase(app)
        return
    
    #Moving on to next player
    app.currentPlayerIndex = (app.currentPlayerIndex + 1) % 4
    app.turnTimer = 0
    app.waitingForPlayer = False
    
    
def determineWinners(app):
    #Computes the winners and distributes the pot
    bestName, winners = getWinners(app.playerCards, app.communityCards, app.foldedPlayers)
    app.winningCombo = bestName
    app.winnerIndexes = winners
    #split rewards if a tie exists
    #if winners:
    share = app.pot // len(winners)
    for i in winners:
        app.playersData[i]['money'] += share
    app.pot = 0  # pot is emptied after distribution

def advancePhase(app):
    #Move to next phase of the game
    if app.phase == "preflop":
        app.phase = "flop"
        dealFlop(app)
    elif app.phase == "flop":
        app.phase = "turn" 
        dealTurn(app)
    elif app.phase == "turn":
        app.phase = "river"
        dealRiver(app)
    elif app.phase == "river":
        app.mode = "showwinners"
        determineWinners(app)
        return
    
    # Reset for new betting round
    app.actionsThisRound = 0
    app.currentPlayerIndex = 0
    app.turnTimer = 0
    app.waitingForPlayer = False
    app.hasBetThisRound = False # Reset betting flag
    app.callAmount = app.minBet # Reset call amount to minimum

    
    # Clear last actions
    for i in range(4):
        if not app.foldedPlayers[i]:
            app.lastActions[i] = ""

#Community card dealing functions based on the game phase:
def dealFlop(app):
    # needs 3 cards 
    for i in range(3):
        card = app.deck.pop()
        app.communityCards.append(card)

def dealTurn(app):
    # deals only one card 
    card = app.deck.pop()
    app.communityCards.append(card)

def dealRiver(app):
    # deals final card
    card = app.deck.pop()
    app.communityCards.append(card)

def drawTurnIndicator(x, y):
    drawCircle(x, y - 90, 15, fill='yellow', border='black')

def redrawAll(app):
    # Common background
    drawBackground(app)
    if app.mode == "start":
        drawStartScreen(app)
    elif app.mode == "play":
        drawGameScreen(app)
    elif app.mode == "showwinners":
        drawShowWinnersScreen(app)
        drawCommunityCards(app)
    elif app.mode == "gameover":
        drawGameOverScreen(app)
        
def drawShowWinnersScreen(app):
    # shadow background
    drawRect(0, 0, app.width, app.height, fill='black', opacity=70)
    drawLabel("Winning hand:", app.width//2, 60,
          size=30, fill='gold', bold=True)

    drawLabel(app.winningCombo, app.width//2, 88,
          size=30, fill='gold', bold=True)
    
    # Draw each player’s cards
    startPositions = [
        (app.width * 0.20, app.height * 0.25),
        (app.width * 0.80, app.height * 0.25),
        (app.width * 0.80, app.height * 0.70),
        (app.width * 0.20, app.height * 0.70)
    ]
    for i, (x, y) in enumerate(startPositions):
        cards = app.playerCards[i]
        highlight = i in app.winnerIndexes #True if player[i] is a winner
        for j, (rank, suit) in enumerate(cards):
            offsetX = -45 + j*90 #to spread cards evenly
            baseFill = 'white' if highlight else 'grey'
            drawRect(x + offsetX, y, 80, 120, fill=baseFill, border='black', align='center')
            drawLabel(f"{rank} {suit}", x + offsetX, y, size=18)
        
        color = 'gold' if highlight else 'white'
        name = app.playersData[i]['name'] if i != 3 else 'You'
        drawLabel(name, x, y - 90, size=22, fill=color, bold=True)
    
    drawLabel("Press R to start the next round", app.width//2, app.height - 50, size=25, fill='white')

def drawBackground(app):
    drawRect(0, 0, app.width, app.height, fill=gradient('lightgreen', 'seagreen', start='center'))

def drawStartScreen(app):
    drawLabel("Welcome to Scotty Texas Hold'em ♠!", app.width//2, app.height//3, bold=True, font='Segoe UI Symbol', size=42, fill='white')
    drawLabel("Welcome to Scotty Texas Hold'em ♠!", app.width//2+1, app.height//3+1, bold=True, font='Segoe UI Symbol', size=42, fill='black')
    drawLabel('Press s to start!', app.width//2, app.height//1.5, size = 35, fill='white')

def createDeck():
    deck = []
    ranks = [2,3,4,5,6,7,8,9,10,'J','Q','K','A']
    suits = ['♠','♥','♦','♣']
    for rank in ranks:
        for suit in suits:
            deck.append((rank, suit))
    return deck

def drawGameScreen(app):
    drawPot(app)
    drawMyCards(app)
    drawPlayers(app)
    drawButtons(app)
    drawCommunityCards(app)
    drawActionBubbles(app)

# Draw community cards
def drawCommunityCards(app):
    #draws community cards in the center
    if not app.communityCards: #no comcards are distributed so far
        return
        
    startX = app.width//2 - (len(app.communityCards) * 45)  #to Center the cards
    y = app.height//2 - 20
    
    for i, (rank, suit) in enumerate(app.communityCards):
        x = startX + i * 90
        # Draw card
        drawRect(x, y, 80, 120, fill='white', border='black', align='center')
        # Draw text on card
        drawLabel(f"{rank} {suit}", x, y, size=16)

def drawActionBubbles(app):
    #Draw what each player did
    positions = [
        [app.width * 0.20, app.height * 0.075], # Player1
        [app.width * 0.80, app.height * 0.075], # Player2
        [app.width * 0.80, app.height * 0.75], # Player3
        [app.width * 0.20, app.height * 0.75]  # You
    ]
    
    for i, (x, y) in enumerate(positions):
        if app.lastActions[i]:
            #Draw bubble background
            textWidth = len(app.lastActions[i]) * 8
            drawRect(x, y, textWidth+10, 20, 
                    fill='lightYellow', border='black', align='center')
            #draws action text
            drawLabel(app.lastActions[i], x, y, size=12, bold=True)



def drawPot(app):
    drawCircle(app.width//2, app.height//8, app.width//30+3)
    drawCircle(app.width//2, app.height//8, app.width//30, fill='yellow')
    drawLabel('$', app.width//2, app.height//8, size=40)
    drawLabel(f"Pot: ${app.pot}", app.width//2+1, app.height//5+1, size=20, fill='white')
    drawLabel(f"Pot: ${app.pot}", app.width//2, app.height//5, size=20)

def drawPerson(x, y, folded=False):
    width, height, radius = 70, 120, 25
    color = 'black' if folded else 'grey'
    drawArc(x, y, width, height, 0, 180, fill=color) # shoulders/body
    drawCircle(x, y - height/1.6, radius, fill=color) # head

def drawSinglePlayer(app, playerIndex, x, y):
    player = app.playersData[playerIndex]
    folded = app.foldedPlayers[playerIndex]
    
    if playerIndex == 3: # You
        color = 'black' if folded else 'white'
        drawLabel('YOU', x, y, size=50, fill=color)
        drawLabel(f"${player['money']}", x, y+30, fill=color)
    else:
        drawPerson(x, y, folded)
        color = 'black' if folded else 'white'
        drawLabel(player['name'], x, (y)//2, fill=color)
        drawLabel(f"${player['money']}", x, y+10, fill=color)

def drawPlayers(app):
    # Player positions: [x, y] coordinates
    positions = [
        [app.width * 0.20, app.height * 0.25], # Player1
        [app.width * 0.80, app.height * 0.25], # Player2
        [app.width * 0.80, app.height * 0.70], # Player3
        [app.width * 0.20, app.height * 0.65]  # You
    ]
    
    #with special adjustment for Player3 label position
    i = 0
    for x, y in positions:
        if i == 2:
            folded = app.foldedPlayers[i]
            drawPerson(x, y, folded)
            color = 'black' if folded else 'white'
            drawLabel('Player3', x, y // 1.22, fill=color)
            drawLabel(f"${app.playersData[i]['money']}", x, y + 10, fill=color)
        else:
            drawSinglePlayer(app, i, x, y)
            
        if i == app.currentPlayerIndex and not app.foldedPlayers[i]:
            drawTurnIndicator(x, y)
        i += 1

def getButtonCoordinates(app):
    startX = app.width/2.6 - (1.5 * buttonWidth + buttonSpacing)
    y = app.height/1.15
    raiseX = startX + 2 * (buttonWidth + buttonSpacing)
    boxX = raiseX + buttonWidth + buttonSpacing
    plusX = boxX + 100
    foldX = startX + 0.6*app.width
    foldY = y + buttonHeight/2 - app.height*0.15
    
    return {
        'startX': startX, 'y': y, 'boxX': boxX, 'boxY': y,
        'plusX': plusX, 'foldX': foldX, 'foldY': foldY
    }

def drawMainButtons(app, coords):
    """Draw CALL, CHECK, RAISE buttons"""
    labels = ['CALL', 'CHECK', 'RAISE']
    colors = [
        ('blue', 'lightBlue'),
        ('green', 'lightGreen'), 
        ('gold', 'yellow')
    ]
    
    for i in range(3):
        x = coords['startX'] + i * (buttonWidth + buttonSpacing)
        
        # Check if CHECK button should be disabled
        if i == 1 and app.hasBetThisRound:  # CHECK button when someone has bet
            drawRect(x, coords['y'], buttonWidth, buttonHeight, 
                    fill='darkGray', border='black', borderWidth=2, opacity=50)
            drawLabel(labels[i], x + buttonWidth/2, coords['y'] + buttonHeight/2,
                     fill='gray', bold=True)
        else:
            drawRect(x, coords['y'], buttonWidth, buttonHeight, 
                    fill=gradient(colors[i][0], colors[i][1], start='top'),
                    border='black', borderWidth=2)
            textColor = 'white' if i < 2 else 'black'
            drawLabel(labels[i], x + buttonWidth/2, coords['y'] + buttonHeight/2,
                     fill=textColor, bold=True)

def drawRaiseControls(app, coords):
    """Draw raise amount box and +/- buttons"""
    # amount display box
    drawRect(coords['boxX'], coords['boxY'], 100, buttonHeight,
            fill=None, border='black', borderWidth=2)
    drawLabel(str(app.raiseAmount), coords['boxX'] + 50, 
             coords['boxY'] + buttonHeight/2, bold=True)
    
    # plus button (right next to box)
    drawRect(coords['plusX'], coords['boxY'], 40, buttonHeight/2,
            fill='lightGrey', border='black')
    drawLabel('+', coords['plusX'] + 20, coords['boxY'] + buttonHeight/4, bold=True)
    
    # minus button (under plus, no horizontal space)
    drawRect(coords['plusX'], coords['boxY'] + buttonHeight/2, 40, buttonHeight/2,
            fill='lightGrey', border='black')
    drawLabel('-', coords['plusX'] + 20, coords['boxY'] + 3*buttonHeight/4, bold=True)

def drawFoldButton(app, coords):
    drawCircle(coords['foldX'], coords['foldY'], 30, fill='red', border='black')
    drawLabel('FOLD', coords['foldX'], coords['foldY'], fill='white', bold=True)

def drawButtons(app):
    # Only draw buttons if it's the human player's turn and they haven't folded
    if app.currentPlayerIndex == 3 and not app.foldedPlayers[3]:
        coords = getButtonCoordinates(app)
        drawMainButtons(app, coords)
        drawRaiseControls(app, coords)
        drawFoldButton(app, coords)

def getMyCards(app):
    random.shuffle(app.deck)
    myCards = []
    for i in range(2):
        card = app.deck.pop()
        myCards.append(card)
    return myCards

def getPlayerCards(app):
    random.shuffle(app.deck)
    playerCards = []
    for i in range(2):
        card = app.deck.pop()
        playerCards.append(card)
    return playerCards


def drawMyCards(app):
    x = app.width//2 - 20
    y = app.height//1.4
    count = 0
    for rank, suit in app.myCards:
        if count == 0:
            angle = -10
        else:
            angle = 10
        # draw card shape
        drawRect(x, y, 80, 120, fill='white', border='black', align='center', rotateAngle=angle)
        # draw text on card
        drawLabel(f"{rank} {suit}", x, y, size=18, rotateAngle=angle)
        x += 60
        count += 1
        
def cardValue(rank):
    #since not all cards have numerical values as ranks
    if rank == 'J': return 11
    if rank == 'Q': return 12
    if rank == 'K': return 13
    if rank == 'A': return 14
    return rank
def getRankOfCombination(cards):
    #creates a sorted list of card values ex: [14, 13, 13, 11, 10, 8, 3]
    values = sorted([cardValue(c[0]) for c in cards], reverse=True)
    #gets suits/symbols
    suits = [c[1] for c in cards]
    counts = {}
    for v in values: counts[v] = counts.get(v, 0) + 1
    #creates a dict that tracks the count of repeated ranks (useful for pairs recognition)
    # ex: {14:2....} => 2 aces
    countValues = sorted(counts.values(), reverse=True) #list of the counts of repeated ranks
    ### detects a flush
    suitCounts = {}
    for s in suits:
        suitCounts[s] = suitCounts.get(s, 0) + 1

    isFlush = False
    for count in suitCounts.values():
        if count >= 5:
            isFlush = True
            break
    ###
        
    unique = sorted(set(values), reverse=True) #unique sorted list for ranking cards
    isStraight = False
    if len(unique) >= 5:
        #checks if there r any 5 consecutive nmbrs out of 7
        for i in range(len(unique)-4):
            if unique[i] - unique[i+4] == 4:
                isStraight = True
                break
    if isFlush and isStraight and max(values) == 14: return ("Royal Flush", 1)
    if isFlush and isStraight: return ("Straight Flush", 2)
    if 4 in countValues: return ("Four of a Kind", 3)
    if 3 in countValues and 2 in countValues: return ("Full House", 4)
    if isFlush: return ("Flush", 5)
    if isStraight: return ("Straight", 6)
    if 3 in countValues: return ("Three of a Kind", 7)
    if countValues.count(2) >= 2: return ("Two Pair", 8)
    if 2 in countValues: return ("One Pair", 9)
    return ("High Card", 10)
def getWinners(playerCards, communityCards, foldedPlayers):
    ranks = [None] * len(playerCards)
    for i in range(len(playerCards)):
        if foldedPlayers[i]:
            ranks[i] = ('Folded', 100)
            continue
        cards = playerCards[i].copy()
        cards.extend(communityCards)
        name, rank = getRankOfCombination(cards)
        ranks[i] = (name, rank)
    bestRank = min(r[1] for r in ranks)
    winners = [i for i, r in enumerate(ranks) if r[1] == bestRank]
    bestName = ranks[winners[0]][0]
    return bestName, winners

# Button click detection functions
def isPlusButtonClicked(mouseX, mouseY, coords):
    #Check if plus button was clicked
    return (coords['plusX'] <= mouseX <= coords['plusX'] + 40 and 
            coords['boxY'] <= mouseY <= coords['boxY'] + buttonHeight/2)

def isMinusButtonClicked(mouseX, mouseY, coords):
    #Check if minus button was clicked
    return (coords['plusX'] <= mouseX <= coords['plusX'] + 40 and 
            coords['boxY'] + buttonHeight/2 <= mouseY <= coords['boxY'] + buttonHeight)

def handlePlusClick(app):
    #Handle plus button click
    if app.raiseAmount + 10 <= app.playersData[3]['money']:
        app.raiseAmount += 10

def handleMinusClick(app):
    #Handle minus button click
    if app.raiseAmount - 10 >= app.minBet:
        app.raiseAmount -= 10

# Game action button detection
def isCallButtonClicked(mouseX, mouseY, coords):
    #Check if CALL button was clicked
    x = coords['startX']
    return (x <= mouseX <= x + buttonWidth and 
            coords['y'] <= mouseY <= coords['y'] + buttonHeight)

def isCheckButtonClicked(mouseX, mouseY, coords):
    #Check if CHECK button was clicked
    x = coords['startX'] + buttonWidth + buttonSpacing
    return (x <= mouseX <= x + buttonWidth and 
            coords['y'] <= mouseY <= coords['y'] + buttonHeight)

def isRaiseButtonClicked(mouseX, mouseY, coords):
    #Check if RAISE button was clicked
    x = coords['startX'] + 2 * (buttonWidth + buttonSpacing)
    return (x <= mouseX <= x + buttonWidth and 
            coords['y'] <= mouseY <= coords['y'] + buttonHeight)

def isFoldButtonClicked(mouseX, mouseY, coords):
    #Check if FOLD button was clicked
    return ((mouseX - coords['foldX'])**2 + (mouseY - coords['foldY'])**2 <= 30**2)

# Player action handlers
def handlePlayerCall(app):
    #Handle player CALL action
    if app.callAmount <= app.playersData[3]['money']:
        app.pot += app.callAmount
        app.playersData[3]['money'] -= app.callAmount
        app.lastActions[3] = f"Call ${app.callAmount}"
        app.hasBetThisRound = True
        app.actionsThisRound += 1
        app.amountsBetThisRound[3] = app.callAmount
        

def handlePlayerCheck(app):
    #Handle player CHECK action
    if not app.hasBetThisRound:  # Only allow check if no one has bet
        app.lastActions[3] = "Check"
        app.actionsThisRound += 1

def handlePlayerRaise(app):
    #Handle player RAISE action
    totalBet = app.callAmount + app.raiseAmount
    if totalBet <= app.playersData[3]['money']:
        app.pot += totalBet
        app.amountsBetThisRound[3] = totalBet
        app.playersData[3]['money'] -= totalBet
        app.lastActions[3] = f"Raise +${app.raiseAmount}"
        app.callAmount = totalBet  # Update call amount for other players
        app.hasBetThisRound = True
        app.actionsThisRound += 1

def handlePlayerFold(app):
    #Handle player FOLD action
    app.foldedPlayers[3] = True
    app.lastActions[3] = "Fold"
    app.actionsThisRound += 1
    app.amountsBetThisRound[3] = 'f'

def onMousePress(app, mouseX, mouseY):
    if (app.mode != "play" or app.currentPlayerIndex != 3 or 
        app.foldedPlayers[3]):
        return  # Only allow clicks during your turn if you haven't folded
        
    coords = getButtonCoordinates(app)
    
    # PLUS click
    if isPlusButtonClicked(mouseX, mouseY, coords):
        handlePlusClick(app)
    # MINUS click  
    elif isMinusButtonClicked(mouseX, mouseY, coords):
        handleMinusClick(app)
    # Game action buttons
    elif isCallButtonClicked(mouseX, mouseY, coords):
        handlePlayerCall(app)
        advanceTurn(app)
    elif isCheckButtonClicked(mouseX, mouseY, coords) and not app.hasBetThisRound:
        handlePlayerCheck(app)
        advanceTurn(app)
    elif isRaiseButtonClicked(mouseX, mouseY, coords):
        handlePlayerRaise(app)
        advanceTurn(app)
    elif isFoldButtonClicked(mouseX, mouseY, coords):
        handlePlayerFold(app)
        advanceTurn(app)

def drawGameOverScreen(app):
    drawRect(0, 0, app.width, app.height, fill='darkGreen')
    drawLabel("Game Over!", app.width//2, app.height//2, size=60, fill='white', bold=True)
    drawLabel(f"Final Pot: ${app.pot}", app.width//2, app.height//2 + 80, size=30, fill='white')
    
    # Show remaining players
    activePlayers = []
    for i, folded in enumerate(app.foldedPlayers):
        if not folded:
            playerName = app.playersData[i]['name'] if i != 3 else 'You'
            activePlayers.append(f"{playerName}: ${app.playersData[i]['money']}")
    
    if activePlayers:
        drawLabel("Remaining Players:", app.width//2, app.height//2 + 120, size=20, fill='white')
        for i, player in enumerate(activePlayers):
            drawLabel(player, app.width//2, app.height//2 + 150 + i*25, size=16, fill='white')

# Start the game
playTexasHoldem()


