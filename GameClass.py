import PlayerModule
import numpy as np
import pandas as pd
import os
import copy
from CardInterfaces import getPossiblePlays, removeCardsFromHand
from CardInterfaces import encodePlays
from PresidentNeuralNet import PresidentNet
import torch
import sys

# Class responsible for the game loop.
class Game:
    def __init__(self, gametype=0, model1=None, model2=None, numHumanPlayers=None, socketio=None):
        self.players = []                   # The player objects apart of the game.
        self.cards = []                     # The cards in the game.
        self.cardsPlayed = []               # The cards played by the players
        self.cardsOnTable = []              # Cards on the table (can be 1,2,3,4)
        self.standings = []                 # The standings of the players at the end of the game.
        self.passedPlayers = []             # The players that passed a given round.
        self.autoAss = []                   # The players who got auto ass from playing a power card as their last play
        self.logArray = []                  # Array of all the past plays
        self.isTrainingDataGerneration = False  # Is used for training data.
        self.enableDropout = False              # Enable dropout in the model.
        self.isWebsiteGame = False              # Is a website game.
        self.encodedPlayedCards = np.zeros(54)  # The cards discarded, encoded in 1-hot vector
        self.assignPlayers(gametype, model1, model2, numHumanPlayers, socketio)
        self.dealCards()                        # Sets the Player.hand attribute

        # If the gametype is not a website game, run the game loop.
        if gametype != 6:
            self.gameLoop()

    # Deal the cards to all the generated player objects.
    def dealCards(self):
        # Initialize the Deck (4 of each card, 2 Jokers)
        tempCards = []
        for i in range(13):
            for j in range(4):
                tempCards.append(i + 1)
        for _ in range(2):
            tempCards.append(14)

        while(len(tempCards) != 0):
            self.cards.append(tempCards.pop(np.random.randint(len(tempCards))))

        cardsPerHand = np.ceil(len(self.cards) / len(self.players))     # Get the number of cards per hand

        # Deal the cards to each player.
        for i, player in enumerate(self.players):
            startIndex = (int)(i * cardsPerHand)
            endIndex = (int)((i + 1) * cardsPerHand)
            if endIndex > len(self.cards):
                endIndex = len(self.cards)

            cardsToAssign = self.cards[startIndex: endIndex]
            player.assignCards(self.cards[startIndex: endIndex])

    # Generate player objects depending on the game type.
    def assignPlayers(self, gameType=0, model1=None, model2=None, numHumanPlayers=None, socketio=None):

        # All players are command line players.
        if gameType == 0:
            for i in range(6): #self.players.append(PlayerModule.Player(0, i)) # Right now this is generating all CMD line players else:
                    self.players.append(PlayerModule.Player(1, i)) # Right now this is generating all CMD line players

        # All players are models (Used for training)
        elif gameType == 1: 
            self.isTrainingDataGerneration = False # Change this to true to use the special model play picking strategy
            self.enableDropout = False             # Chagne this to true to enable dropout when the model is selecting its play (Adds randomness when training)
            for i in range(6):
                self.players.append(PlayerModule.Player(2,i, model1, self))

        # All players are model players (Not used for training).
        elif gameType == 2:
            for i in range(6):
                self.players.append(PlayerModule.Player(2,i, model1, self))

        # Half of the players are the model, other half are random.
        elif gameType == 3: #Model with random players
            for i in range(3):
                self.players.append(PlayerModule.Player(2,i, model1, self))
            for i in range(3):
                self.players.append(PlayerModule.Player(1, i))

        # Generate 5 AI players and one command line player. (Used to play against model on command line)
        elif gameType == 4:
            self.players.append(PlayerModule.Player(0, 42)) # Right now this is generating all CMD line players
            for i in range(5): #self.players.append(PlayerModule.Player(0, i)) # Right now this is generating all CMD line players else:
                    self.players.append(PlayerModule.Player(2, i, model1, self)) # Right now this is generating all CMD line players
        
        # Generate 3 players with one model and the remaining with another model (Used for fitness).
        elif gameType == 5: #Evaluate Model
            for i in range(3):
                self.players.append(PlayerModule.Player(2,i, model1, self))
                self.players.append(PlayerModule.Player(2,i + 0.1, model2, self))
        
        # Generate Website game (dynamic number of AI and socket players).
        elif gameType == 6:
            # Load the model
            model1 = PresidentNet()
            model1.load_state_dict(torch.load("Models/websiteModel.pt", map_location=torch.device('cpu')))
            self.isWebsiteGame = True
            self.socketio = socketio

            # Generate human players.
            for i in range(numHumanPlayers):
                print(f"Generating human player ID: {i + 1}")
                self.players.append(PlayerModule.Player(3, i + 1, socketio=socketio)) 
            
            # Generate model players.
            for i in range(numHumanPlayers, 6):
                print(f"Generating AI player ID: {i + 1}")
                self.players.append(PlayerModule.Player(2,i + 1, model1, self))

    # Generate an array of players who got autoass, and the standings for a game.
    def getResults(self):
        resultsArr = []
        autoAssIds = []
        self.standings
        for player in self.standings:
            resultsArr.append(player)
        for player in self.autoAss:
            autoAssIds.append(player.id)
            resultsArr.remove(player)
            resultsArr.append(player)

        return resultsArr, autoAssIds

    # Reset whether or not a player has played in a hand.
    def resetPlayers(self):
        for player in self.players:
            player.playedHand = False


    # Add the play to self.logArray
    def logPlay(self, cardsPlayed, possiblePlays, playerID, playInHand, handBeforePlay):
        logObject = {}
        logObject["id"] = playerID
        logObject["cardsOnTable"] = self.cardsOnTable   # The play on the table
        logObject["cardsPlayed"] = cardsPlayed          # The cards Played by the player
        logObject["possiblePlays"] = possiblePlays      # The possible Plays of the plyaer.
        logObject["playedHand"] = playInHand            # Did the player play in the hand?
        logObject["cardsInHand"] = handBeforePlay       # The player hand before the play.

        encodedPlayers = np.zeros(6)
        for i, player in enumerate(self.players):
            encodedPlayers[i] = 1
        logObject["encodedPlayersIn"] = encodedPlayers 

        self.logArray.append(logObject)
    
    
    # Add a card to the cardsPlayed (Discarded cards)
    def encodeCardInPlayed(self, card, cardsPlayed):
        valueSet = False
        valueIndex = (card-1) * 4
        while(not valueSet):
            if cardsPlayed[valueIndex] == 1:
                valueIndex += 1
            else:
                cardsPlayed[valueIndex] = 1
                valueSet = True
        return cardsPlayed
 
    
    # Add a card to the list of cardsPlayed.
    def playCards(self, cardsPlayed):
        for card in cardsPlayed:
            self.encodedPlayedCards = self.encodeCardInPlayed(card, self.encodedPlayedCards)

    # Get the training date for the current game. (Usutally executed after the gameloop has finished)
    # This will assign the rewards to all the plays (1=autoass, 2=ass, 3=viceass, 4=secondNeutral, 5=neutral, 6=vicePresident, 7=president)
    def getTrainingData(self):
        outputArray = []
        finalStandings = []

        # generate the standings for the game.
        for player in self.standings:
            finalStandings.append(player)
        _, autoAsses = self.getResults()

        # Determine each players score.
        scoreInfo = {}
        for i, player in enumerate(finalStandings):
            scoreInfo[player.id] = {}
            if player.id in autoAsses:
                scoreInfo[player.id]["score"] = 1
            else:
                scoreInfo[player.id]["score"] = 7 - i
            scoreInfo[player.id]["cards"] = 9
        
        # Get the playerIds of only the target model.
        aiPlayerKeys = []
        for key in scoreInfo.keys():
            # Cast to int because the keys are either 1, or 1.1 (So if int key is the same as the key, there is no decimal)
            if int(key) == key:
                aiPlayerKeys.append(key)

        sortedPlayerIds = list(scoreInfo.keys())
        sortedPlayerIds.sort()

        allCardsPlayed = []
        allCardsEncoded = np.zeros(54)
        
        # For each play in the logArray.
        for logObject in self.logArray:

            # Ignore times when the model had no choise then to pass.
            if len(logObject["possiblePlays"]) == 0:
                continue
            
            playerScore = scoreInfo[logObject["id"]]["score"]

            # Determine the number of cards left the player has.
            if len(logObject["cardsPlayed"]) > 0:
                scoreInfo[logObject["id"]]["cards"] -= len(logObject["cardsPlayed"])

            currentPos = sortedPlayerIds.index(logObject["id"])
            playersSortedByCurrent = sortedPlayerIds[currentPos:] + sortedPlayerIds[:currentPos] # Get the ids where the first item is the current player

            # Cound the cards of all the oponents.
            oponentNumCards = np.empty(0)
            for i in playersSortedByCurrent:
                if i == logObject["id"]:
                    continue
                oponentCards = np.ones(scoreInfo[i]["cards"])
                oponentCards = np.hstack((oponentCards, np.zeros(9-scoreInfo[i]["cards"])))
                if oponentNumCards != np.empty(0):
                    oponentNumCards = np.hstack((oponentNumCards, oponentCards))
                else:
                    oponentNumCards = oponentCards 

            cardsOntable = encodePlays([logObject["cardsOnTable"]], value=1, oneHot=0)

            # Encode the players hand
            handEncoded = np.zeros(54)
            for card in logObject["cardsInHand"]:
                handEncoded = self.encodeCardInPlayed(card, handEncoded)
            
            # Encode if the player passed
            playerPass = [0]
            if len(logObject["cardsPlayed"]) == 0:
                playerPass = [playerScore]
             

            # Create an array of all the non-powercards in the players hand
            nonPowerCardsInHand = []
            for card in logObject["cardsInHand"]:
                if card != 2 and card != 3 and card != 14:
                    nonPowerCardsInHand.append(card)


            # If the list of non-powercardsInHand is 0, then there are only powercards
            onlyPowerCardsInHand = len(nonPowerCardsInHand) == 0
            numberOfNonPowerCardsInHandBefore = len(nonPowerCardsInHand)

            # Remove all the cards from the play from nonPowercards in hand.    
            for card in logObject["cardsPlayed"]:
                for nonPowerCard in nonPowerCardsInHand:
                    if card == nonPowerCard:
                        nonPowerCardsInHand.remove(nonPowerCard) # I suspect this is removing all instances of the card
                        break
                
            numberOfNonPowerCardsInHandAfter = len(nonPowerCardsInHand)

            # If after the play nonPowercards in hand 
            # The play must not result in an empty hand, or else they got auto ass this turn.
            autoAssThisTurn = False
            if numberOfNonPowerCardsInHandBefore != 0 and numberOfNonPowerCardsInHandAfter == 0 and len(logObject["cardsPlayed"]) != len(logObject["cardsInHand"]):
                autoAssThisTurn = True
                if playerPass[0] != 0:
                    playerPass = [1]
            
            # The play must not result in an empty hand
            # If there are powercards in your hand and there are no non-powercards, then you are autoass 
            validPlay = True
            if numberOfNonPowerCardsInHandBefore == 0:
                validPlay = False
                if playerPass[0] != 0:
                    playerPass = [1]
            
            cardsPlayedEncoded = encodePlays([logObject["cardsPlayed"]], playerScore, oneHot=0 )
            
            # Only add Row if:
            # - If there is a mix of AI and Random, only add AI ids.
            # - If the player got autoAss this turn add it. or it was a regular play
            # - If the player got autoass this turn, add their score as 1.
            # - If the player got autoass on a previous turn, do not add the score.
            if (playerScore == 1 and (not validPlay or autoAssThisTurn)) or (playerScore != 1 and validPlay):
                outputRow = np.hstack((logObject["id"], oponentNumCards, handEncoded, cardsOntable, allCardsEncoded, playerPass, cardsPlayedEncoded))
                if len(outputArray) == 0:
                    outputArray = outputRow
                else:
                    outputArray = np.vstack((outputArray,outputRow))


            # Add the cards to the cards played after the row has been added.
            for card in logObject["cardsPlayed"]:
                allCardsEncoded = self.encodeCardInPlayed(card, allCardsEncoded)
                allCardsPlayed.append(card)
            allCardsPlayed.sort()

        return outputArray


    # Output the training datat to a log file.
    def outputLogToFile(self, filename):
        data = self.getTrainingData()
        data.tofile(filename, sep=",")

    # Game loop. This is executed when the game object is created (Unless it is a website game)
    def gameLoop(self):
        turnIndex = 0                   # The index of the player whos turn it is.
        gameOver = False                # Is the game over.
        lastPlayedIsFinished = False    # Did the last player who played their hand finish.

        # One loop is one players turn
        while not gameOver:
            isBurn = False
            isFinished = False
            passed = False
            
            cardOnTablePrior = self.cardsOnTable
            handBeforePlay = copy.deepcopy(self.players[turnIndex].hand)
            possiblePlays = getPossiblePlays(self.players[turnIndex].hand, self.cardsOnTable)

            # Prompt the player for a play.
            cardsToPlay = self.players[turnIndex].promptCard(self.cardsOnTable)

            # Log the play
            self.logPlay(cardsToPlay, possiblePlays, self.players[turnIndex].id, self.players[turnIndex].playedHand, handBeforePlay)

            # Add all the cards to the played cards list.
            for card in cardsToPlay: 
                self.cardsPlayed.append(card)
            
            if len(cardsToPlay) == 0: # The player passed
                self.passedPlayers.append(self.players[turnIndex])
                passed = True

                # Check if all players passed on what is on the table.
                if (lastPlayedIsFinished and (len(self.passedPlayers) == len(self.players))) or (not lastPlayedIsFinished and  (len(self.passedPlayers) == len(self.players) - 1)):
                    lastPlayedIsFinished = False
                    self.cardsOnTable = []
                    self.resetPlayers()
                    self.passedPlayers = []
            else: 

                # Check if the play is a burn
                if len(self.cardsOnTable) != 0 and cardsToPlay[0] == self.cardsOnTable[0]:
                    lastPlayedIsFinished = False
                    self.passedPlayers = []
                    self.resetPlayers()
                    self.cardsOnTable = []
                    isBurn = True
                
                # If the play is not a burn, then new play has started.
                else:
                    lastPlayedIsFinished = False
                    self.passedPlayers = []
                    self.cardsOnTable = cardsToPlay
            
                # If the player is done their hand.
                if len(self.players[turnIndex].hand) == 0: 
                    # Check if the player gets autoass.
                    if 2 in cardsToPlay or 3 in cardsToPlay or 14 in cardsToPlay: # The player is autoAss for finishing on a powercard
                        self.autoAss.append(self.players[turnIndex])
                    
                    self.standings.append(self.players[turnIndex])
                    lastPlayedIsFinished = True
                    self.players.pop(turnIndex)

                # If there is only one player, the game is over.
                if len(self.players) == 1:
                    self.standings.append(self.players[0])
                    gameOver = True 
                    break

            #TODO: Make this function remove the cards from the players hand.
            #   * Right now this is done by the CardInterface, which is wrong.
            self.playCards(cardsToPlay)

            # Determine who has the next turn.
            if len(self.players) == 1:
                turnIndex = 0
            elif isBurn and not lastPlayedIsFinished:
                turnIndex = (turnIndex) % len(self.players)
            elif isBurn and lastPlayedIsFinished:
                turnIndex = ((turnIndex % len(self.players))) % len(self.players)
            elif not lastPlayedIsFinished or passed:
                turnIndex = (turnIndex + 1) % len(self.players)
            else: 
                turnIndex = turnIndex % len(self.players)


    # Initialize the game if it is a website game 
    def initSocketGame(self):
        self.turnIndex = 0
        self.gameOver = False
        self.lastPlayedIsFinished = False
        self.turnId = self.players[0].id
        initObject = {}

        # Create the initialization object for each socket player. (This will later be emitted to the clients)
        for player in self.players:
            tempHand = np.sort(player.hand)
            numTwos = np.count_nonzero(tempHand == 2)
            numThrees = np.count_nonzero(tempHand == 3)
            numJokers = np.count_nonzero(tempHand == 14)
            tempHand = tempHand[tempHand != 2]
            tempHand = tempHand[tempHand != 3]
            tempHand = tempHand[tempHand != 14]
            for i in range(numTwos):
                tempHand = np.append(tempHand, 2)
            for i in range(numThrees):
                tempHand = np.append(tempHand, 3)
            for i in range(numJokers):
                tempHand = np.append(tempHand, 14)
            initObject[player.id] = np.flip(tempHand).tolist()

        # Generate the first play (Will be emitted to all the clients so they know what to display)
        firstPlay = {}
        firstPlay["cardsOnTable"] = []
        firstPlay["playFromId"] = -1
        firstPlay["cardsPlayed"] = 0
        firstPlay["nextId"] = 1
        
        print(f"First Play: {firstPlay}")
        print(f"initbject: {initObject}")
        return initObject, firstPlay 
    

    # Advances the game by one player input (either AI or socket player)
    def socketGameStep(self, playObj, isSocket):
        # Returns stepObj:
        #   - "cardsOnTable": Cards on table after the play
        #   - "playFromID": ID of the player who played the play
        #   - "cardsPlayed": cards played by the player"
        #   - "NextID"
        #   - "isBurn"
        #   - "isFinished"
        #   - "passed"

        isBurn = False
        isFinished = False
        passed = False
        stepObj = {}
        stepObj["validPlay"] = True
            
        cardOnTablePrior = self.cardsOnTable

        # prompt the player at player index for a card.
        handBeforePlay = copy.deepcopy(self.players[self.turnIndex].hand)
        possiblePlays = getPossiblePlays(self.players[self.turnIndex].hand, self.cardsOnTable)

        # if the current player is not a socket player.
        if not isSocket:
            cardsToPlay = self.players[self.turnIndex].promptCard(self.cardsOnTable)
            stepObj["play"] = cardsToPlay
            stepObj["playFromId"] = self.turnId
            stepObj["cardsPlayed"] = cardsToPlay
            stepObj["playFromId"] = self.turnId
        
        # If the player is a socket player.
        else:
            play = playObj["play"].split(",")
            play = [eval(i) for i in play] # convert the play to int
            if play in possiblePlays or (len(play) == 1 and play[0] == 0):
                if play[0] == 0:
                    play = []
                cardsToPlay = play
                removeCardsFromHand(cardsToPlay, self.players[self.turnIndex])
                stepObj["play"] = cardsToPlay
                stepObj["playFromId"] = self.turnId
                stepObj["cardsPlayed"] = cardsToPlay
            else:
                stepObj["validPlay"] = False
                print("Invalid play selected")
                return stepObj

        self.logPlay(cardsToPlay, possiblePlays, self.players[self.turnIndex].id, self.players[self.turnIndex].playedHand, handBeforePlay)

        # Add all the cards to the played cards list.
        for card in cardsToPlay: 
            self.cardsPlayed.append(card)
            
        if len(cardsToPlay) == 0: # The player passed
            self.passedPlayers.append(self.players[self.turnIndex])
            passed = True

            # If the last person to play finished their hand.
            if (self.lastPlayedIsFinished and (len(self.passedPlayers) == len(self.players))) or (not self.lastPlayedIsFinished and  (len(self.passedPlayers) == len(self.players) - 1)):
                self.lastPlayedIsFinished = False
                self.cardsOnTable = []
                self.resetPlayers()
                self.passedPlayers = []
        else: 
            # If the play is burn.
            if len(self.cardsOnTable) != 0 and cardsToPlay[0] == self.cardsOnTable[0]:
                self.lastPlayedIsFinished = False
                self.passedPlayers = []
                self.resetPlayers()
                self.cardsOnTable = []
                isBurn = True
            else:
                self.lastPlayedIsFinished = False
                self.passedPlayers = []
                self.cardsOnTable = cardsToPlay
            
            if len(self.players[self.turnIndex].hand) == 0:
                if 2 in cardsToPlay or 3 in cardsToPlay or 14 in cardsToPlay: # The player is autoAss for finishing on a powercard
                    self.autoAss.append(self.players[self.turnIndex])
                self.standings.append(self.players[self.turnIndex])
                self.lastPlayedIsFinished = True
                self.players.pop(self.turnIndex)

            if len(self.players) == 1:
                self.standings.append(self.players[0])
                self.gameOver = True 
        
        self.playCards(cardsToPlay)
        stepObj["cardsOnTable"] = self.cardsOnTable

        if len(self.players) == 1:
            self.turnIndex = 0
        elif isBurn and not self.lastPlayedIsFinished:
            self.turnIndex = (self.turnIndex) % len(self.players)
        elif isBurn and self.lastPlayedIsFinished:
            self.turnIndex = ((self.turnIndex % len(self.players))) % len(self.players)
        elif not self.lastPlayedIsFinished or passed:
            self.turnIndex = (self.turnIndex + 1) % len(self.players)
        else: 
            self.turnIndex = self.turnIndex % len(self.players)

        self.turnId = self.players[self.turnIndex].id
        stepObj["nextId"] = self.turnId
        stepObj["isBurn"] = isBurn
        stepObj["isFinished"] = self.gameOver 
        stepObj["passed"] = passed
        return stepObj


    


    


