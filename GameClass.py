import PlayerModule
import numpy as np
import pandas as pd
import os
import copy
from CardInterfaces import getPossiblePlays, removeCardsFromHand
from CardInterfaces import encodePlays
from PresidentNeuralNet import PresidentNet
#from flask_socketio import SocketIO, send, emit
import torch
import sys


# NEXT:
#   - Try and run the updated parameters without creating new training data in model.train() mode
#       - Right now it is running in model.train() mode when generating new data to act as a pseudo random informed player

class Game:

    def __init__(self, gametype=0, model1=None, model2=None, numHumanPlayers=None, socketio=None):
        self.players = []
        self.cards = []
        self.cardsPlayed = []
        self.cardsOnTable = []   # Array of cards on the table (can be 1,2,3,4)
        self.standings = []
        self.passedPlayers = []
        self.autoAss = []
        self.logArray = []
        self.isTrainingDataGerneration = False
        self.enableDropout = False
        self.isWebsiteGame = False
        self.encodedPlayedCards = np.zeros(54)
        self.assignPlayers(gametype, model1, model2, numHumanPlayers, socketio)    # This will set self.players array to Player Objects.
        self.dealCards()        # Sets the Player.hand attribute
        if gametype != 6:
            self.gameLoop()


    def dealCards(self):
        # Initialize the Deck (4 of each card, 2 Jokers)
        tempCards = []
        for i in range(13):
            for j in range(4):
                tempCards.append(i + 1)
        for _ in range(2):
            tempCards.append(14)

        #TODO: DO this better with numpy.
        while(len(tempCards) != 0):
        #while(len(tempCards) > (54 - 6)):
            self.cards.append(tempCards.pop(np.random.randint(len(tempCards))))
        # Split the array into len(self.players) parts.
        cardsPerHand = np.ceil(len(self.cards) / len(self.players))     # Get the number of cards per hand
        #cardsPerHand = 1
        for i, player in enumerate(self.players):
            startIndex = (int)(i * cardsPerHand)
            endIndex = (int)((i + 1) * cardsPerHand)
            if endIndex > len(self.cards):
                endIndex = len(self.cards)

            cardsToAssign = self.cards[startIndex: endIndex]
            player.assignCards(self.cards[startIndex: endIndex])

        #for player in self.players:
            #print(f"player({player.id}): {player.hand}")

    def assignPlayers(self, gameType=0, model1=None, model2=None, numHumanPlayers=None, socketio=None):

        if gameType == 1: # All players a President model
            #self.isTrainingDataGerneration = True
            self.isTrainingDataGerneration = False
            self.enableDropout = False 
            for i in range(6):
                self.players.append(PlayerModule.Player(2,i, model1, self))
                #self.players.append(PlayerModule.Player(2,i + 0.1, model2, self)) 
        elif gameType == 2: # All players are model.
            for i in range(6):
                self.players.append(PlayerModule.Player(2,i, model1, self))
        if gameType == 3: #Model with random players
            for i in range(3):
                self.players.append(PlayerModule.Player(2,i, model1, self))
            for i in range(3):
                self.players.append(PlayerModule.Player(1, i))

        elif gameType == 0:
            for i in range(6): #self.players.append(PlayerModule.Player(0, i)) # Right now this is generating all CMD line players else:
                    self.players.append(PlayerModule.Player(1, i)) # Right now this is generating all CMD line players
        elif gameType == 4:
            self.players.append(PlayerModule.Player(0, 42)) # Right now this is generating all CMD line players
            for i in range(5): #self.players.append(PlayerModule.Player(0, i)) # Right now this is generating all CMD line players else:
                    self.players.append(PlayerModule.Player(2, i, model1, self)) # Right now this is generating all CMD line players
        elif gameType == 5: #Evaluate Model
            for i in range(3):
                self.players.append(PlayerModule.Player(2,i, model1, self))
                self.players.append(PlayerModule.Player(2,i + 0.1, model2, self))
        elif gameType == 6:
            model1 = PresidentNet()
            model1.load_state_dict(torch.load("Models/websiteModel.pt", map_location=torch.device('cpu')))
            self.isWebsiteGame = True
            self.socketio = socketio
            for i in range(numHumanPlayers):
                print(f"Generating human player ID: {i + 1}")
                self.players.append(PlayerModule.Player(3, i + 1, socketio=socketio)) 
            for i in range(numHumanPlayers, 6):
                print(f"Generating AI player ID: {i + 1}")
                self.players.append(PlayerModule.Player(2,i + 1, model1, self))

            
        

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
        
        #for i, player in enumerate(resultsArr):
            #print(f"{i}. Player({player.id})")

        return resultsArr, autoAssIds

    def resetPlayers(self):
        for player in self.players:
            player.playedHand = False


    def logPlay(self, cardsPlayed, possiblePlays, playerID, playInHand, handBeforePlay):
        logObject = {}
        logObject["id"] = playerID
        logObject["cardsOnTable"] = self.cardsOnTable   # The play on the table
        logObject["cardsPlayed"] = cardsPlayed          # The cards Played by the player
        logObject["possiblePlays"] = possiblePlays      # The possible Plays of the plyaer.
        logObject["playedHand"] = playInHand            # Did the player play in the hand?
        logObject["cardsInHand"] = handBeforePlay       # The player hand before the play.
        
        #print(f"player({playerID})")
        #print(f"cardsOntable({self.cardsOnTable})")
        #print(f"cardsPlayed({cardsPlayed})")
        #print(f"possiblePlays({possiblePlays})")
        #print(f"Hand Before Play({handBeforePlay})")
        #print("--")

        encodedPlayers = np.zeros(6)
        for i, player in enumerate(self.players):
            encodedPlayers[i] = 1
        logObject["encodedPlayersIn"] = encodedPlayers 

        self.logArray.append(logObject)
    
    
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
 
    
    def playCards(self, cardsPlayed):
        for card in cardsPlayed:
            self.encodedPlayedCards = self.encodeCardInPlayed(card, self.encodedPlayedCards)

    def getTrainingData(self):
        outputArray = []
        finalStandings = []
        for player in self.standings:
            finalStandings.append(player)
        #for player in self.autoAss:
            #finalStandings.append(player)
        _, autoAsses = self.getResults()

        scoreInfo = {}
        for i, player in enumerate(finalStandings):
            scoreInfo[player.id] = {}
            if player.id in autoAsses:
                scoreInfo[player.id]["score"] = 1
            else:
                scoreInfo[player.id]["score"] = 7 - i
            #scoreInfo[player.id]["numPlays"] = 1
            scoreInfo[player.id]["cards"] = 9
            #TESTING
            #print(f"player:{player.id}: score: {6-i}")
        #for key in scoreInfo.keys():
            #print(f"PlayerId: {key} - Score: {scoreInfo[key]['score']}")

        aiPlayerKeys = []
        for key in scoreInfo.keys():
            if int(key) == key:
                aiPlayerKeys.append(key)

        sortedPlayerIds = list(scoreInfo.keys())
        sortedPlayerIds.sort()

        #for logObject in self.logArray:
            #if len(logObject["cardsPlayed"]) > 0:
                #scoreInfo[logObject["id"]]["numPlays"] += 1

        allCardsPlayed = []
        #allCardsEncoded = -np.ones(54)
        allCardsEncoded = np.zeros(54)
        
        for logObject in self.logArray:
            # Encode possible Plays 
            #playerScore = scoreInfo[logObject["id"]]["score"] / scoreInfo[logObject["id"]]["numPlays"]
            if len(logObject["possiblePlays"]) == 0:
                continue
            
            playerScore = scoreInfo[logObject["id"]]["score"]
            #print(f"({logObject['id']}) Num Plays Left: {scoreInfo[logObject['id']]['numPlays']}")
            if len(logObject["cardsPlayed"]) > 0:
                scoreInfo[logObject["id"]]["cards"] -= len(logObject["cardsPlayed"])

            currentPos = sortedPlayerIds.index(logObject["id"])
            playersSortedByCurrent = sortedPlayerIds[currentPos:] + sortedPlayerIds[:currentPos] # Get the ids where the first item is the current player
            #print("==")
            #print(f"PlayerId: {logObject['id']}")
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
                #print(f"Player: {i}") 
                #print(f"Shape of oponentCards:{oponentCards.shape}")
                #print(f"OponentCards: {oponentCards}")
                #print(f"numCards: {scoreInfo[i]['cards']}")


            autoAssThisTurn = False
            #possiblePlaysEncoded = encodePlays(logObject["possiblePlays"], 1)
            # ENCODED AS -1
            #cardsOntable = encodePlays([logObject["cardsOnTable"]], 1)
            # ENCODED AS 0
            cardsOntable = encodePlays([logObject["cardsOnTable"]], value=1, oneHot=0)

            # ENCODED AS -1
            #handEncoded = -np.ones(54)
            # ENCODED AS 0
            handEncoded = np.zeros(54)
            for card in logObject["cardsInHand"]:
                handEncoded = self.encodeCardInPlayed(card, handEncoded)
            

            # Encode the play that the player played
            #playerScore = scoreInfo[logObject["id"]]["score"]
            #playerScore = -1
            #for i, player in enumerate(finalStandings):
            #    if player.id == logObject["id"]:
            #        #playerScore = 6 - i
            #        if i <= 2:
            #            playerScore = 3 - i
            #        else:
            #            playerScore = 2 - i
            #        break

            # Encode is the player passed
            playerPass = [0]
            if len(logObject["cardsPlayed"]) == 0:
                playerPass = [playerScore]
            
            
            # If the hand has only power cards after the play, then set the score to -10.

            validPlay = True

            # Create an array of all the non-powercards in the players hand
            nonPowerCardsInHand = []
            for card in logObject["cardsInHand"]:
                if card != 2 and card != 3 and card != 14:
                    nonPowerCardsInHand.append(card)


            # If the list of non-powercardsInHand is 0, then there are only powercards
            onlyPowerCardsInHand = len(nonPowerCardsInHand) == 0 # If there are only power cards in the users hand

            numberOfNonPowerCardsInHandBefore = len(nonPowerCardsInHand)

            # Remove all the cards from the play from nonPowercards in hand.    
            for card in logObject["cardsPlayed"]:
                for nonPowerCard in nonPowerCardsInHand:
                    if card == nonPowerCard:
                        nonPowerCardsInHand.remove(nonPowerCard) # I suspect this is removing all instances of the card
                        break
                
            #print(f"---Player id({logObject['id']}----")
            numberOfNonPowerCardsInHandAfter = len(nonPowerCardsInHand)
            # If after the play nonPowercards in hand 
            # THe play must not result in an empty hand
            if numberOfNonPowerCardsInHandBefore != 0 and numberOfNonPowerCardsInHandAfter == 0 and len(logObject["cardsPlayed"]) != len(logObject["cardsInHand"]):
                #scoreInfo[logObject["id"]]["score"] = -10
                autoAssThisTurn = True
                if playerPass[0] != 0:
                    playerPass = [1]
            
            # THe play must not result in an empty hand
            if numberOfNonPowerCardsInHandBefore == 0:
                validPlay = False
                if playerPass[0] != 0:
                    playerPass = [1]
            #print(f"auto ass this turn: {autoAssThisTurn}")
            #print(f"Valid Play: {validPlay}")
            
            # If there are powercards in your hand and there are no non-powercards, then you are autoass
            

            #print(f"Play: {logObject['cardsPlayed']}")
            #print(f"validPlay: {validPlay}") 
            #print(f"autoAssThisTurn: {autoAssThisTurn}") 
            #print(f"Adding to data: {validPlay or autoAssThisTurn}")
            #print("----")
            cardsPlayedEncoded = encodePlays([logObject["cardsPlayed"]], playerScore, oneHot=0 )
            
            # Only add Row if:
            # - If there is a mix of AI and Random, only add AI ids.
            # - If the player got autoAss this turn add it. or it was a regular play

            # TESTING
            #print(f"Players in encoded: {logObject['encodedPlayersIn']}")
            #print(f"PlayerHand: {np.sort(logObject['cardsInHand'])}")
            #print(f"Encoded PlayerHand: {handEncoded}")
            #print(f"Cards In OnTable: {logObject['cardsOnTable']}")
            #print(f"Encoded Cards In OnTable: {cardsOntable}")
            #print(f"discardedCards: {allCardsPlayed}")
            #print(f"Encoded discardedCards: {allCardsEncoded}")
            #print(f"PlayerPass:{playerPass}")
            #print(f"Cards Player:{logObject['cardsPlayed']}")
            #print(f"Encoded Cards Player:{cardsPlayedEncoded}")
            #if not (len(aiPlayerKeys) > 0 and logObject["id"] not in aiPlayerKeys) and (validPlay or autoAssThisTurn):
            if (playerScore == 1 and (not validPlay or autoAssThisTurn)) or (playerScore != 1 and validPlay):
                outputRow = np.hstack((logObject["id"], oponentNumCards, handEncoded, cardsOntable, allCardsEncoded, playerPass, cardsPlayedEncoded))
                if len(outputArray) == 0:
                    outputArray = outputRow
                else:
                    #outputArray = np.vstack((outputArray, outputRow))
                    #outputArray = np.vstack((outputRow, outputArray))
                    outputArray = np.vstack((outputArray,outputRow))

            #input()
            #print('======================================')
            #input()

            # Encode the all the cards in the cards played.

            # Add the cards to the cards played after the row has been added.
            for card in logObject["cardsPlayed"]:
                allCardsEncoded = self.encodeCardInPlayed(card, allCardsEncoded)
                allCardsPlayed.append(card)
            allCardsPlayed.sort()
        return outputArray


    def outputLogToFile(self, filename):
        data = self.getTrainingData()
        data.tofile(filename, sep=",")

    def gameLoop(self):
        # Prompt the players for cards
        # Choose a random player with a 4 to start.
        turnIndex = 0
        gameOver = False
        lastPlayedIsFinished = False
        handObject = {}
        for player in self.players:
            handObject[player.id] = np.sort(player.hand).tolist()
        

        # Removed because it is now in the server side.
        #emit("gameStarted", handObject)

        # One loop is one players turn
        while not gameOver:
            isBurn = False
            isFinished = False
            passed = False
            
            cardOnTablePrior = self.cardsOnTable
            # prompt the player at player index for a card.
            handBeforePlay = copy.deepcopy(self.players[turnIndex].hand)
            possiblePlays = getPossiblePlays(self.players[turnIndex].hand, self.cardsOnTable)
            cardsToPlay = self.players[turnIndex].promptCard(self.cardsOnTable)
            self.logPlay(cardsToPlay, possiblePlays, self.players[turnIndex].id, self.players[turnIndex].playedHand, handBeforePlay)
            # newPlay Object:
            #   - PlayerID of person who played
            #   - Playername of the person who played
            #   - Cards played
            #   - Cards on table after

            # This is removed because socketIO is moved to new functions.
            #newPlay = {}
            #newPlay["playerID"] = self.players[turnIndex].id
            #newPlay["playerName"] = self.socketio.players[self.players[turnIndex].id]["name"]
            #newPlay["cardsPlayed"] = cardsToPlay

            # Add all the cards to the played cards list.
            for card in cardsToPlay: 
                self.cardsPlayed.append(card)
            
            if len(cardsToPlay) == 0: # The player passed
                #print("The player has passed")
                self.passedPlayers.append(self.players[turnIndex])
                passed = True

                if (lastPlayedIsFinished and (len(self.passedPlayers) == len(self.players))) or (not lastPlayedIsFinished and  (len(self.passedPlayers) == len(self.players) - 1)):
                    lastPlayedIsFinished = False
                    #print("All players have passed")
                    self.cardsOnTable = []
                    self.resetPlayers()
                    self.passedPlayers = []
            else: 
                if len(self.cardsOnTable) != 0 and cardsToPlay[0] == self.cardsOnTable[0]:
                    lastPlayedIsFinished = False
                    self.passedPlayers = []
                    self.resetPlayers()
                    self.cardsOnTable = []
                    isBurn = True
                else:
                    lastPlayedIsFinished = False
                    self.passedPlayers = []
                    self.cardsOnTable = cardsToPlay
            
                if len(self.players[turnIndex].hand) == 0:
                    if 2 in cardsToPlay or 3 in cardsToPlay or 14 in cardsToPlay: # The player is autoAss for finishing on a powercard
                        self.autoAss.append(self.players[turnIndex])
                    self.standings.append(self.players[turnIndex])
                    lastPlayedIsFinished = True
                    self.players.pop(turnIndex)

                if len(self.players) == 1:
                    self.standings.append(self.players[0])
                    gameOver = True 
                    break
                
            #newPlay["cardsOnTable"] = self.cardsOnTable
            #emit("newPlay", newPlay)
            self.playCards(cardsToPlay)

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

        #results = self.printResults() 

    def initSocketGame(self):
        self.turnIndex = 0
        self.gameOver = False
        self.lastPlayedIsFinished = False
        self.turnId = self.players[0].id
        initObject = {}
        for player in self.players:
            #initObject[player.id] = np.sort(player.hand).tolist()
            tempHand = np.sort(player.hand)
            numTwos = np.count_nonzero(tempHand == 2)
            numThrees= np.count_nonzero(tempHand == 3)
            numJokers= np.count_nonzero(tempHand == 14)
            tempHand = tempHand[tempHand != 2]
            tempHand = tempHand[tempHand != 3]
            tempHand = tempHand[tempHand != 14]
            for i in range(numTwos):
                print(f"Appending 2 for player {player.id}")
                tempHand = np.append(tempHand, 2)
            for i in range(numThrees):
                #tempHand.append(3)
                print(f"Appending 3 {player.id}")
                tempHand = np.append(tempHand, 3)
            for i in range(numJokers):
                #tempHand.append(14)
                print(f"Appending 14 {player.id}")
                tempHand = np.append(tempHand, 14)
            initObject[player.id] = np.flip(tempHand).tolist()

            
            
            
            
    
        firstPlay = {}
        firstPlay["cardsOnTable"] = []
        firstPlay["playFromId"] = -1
        firstPlay["cardsPlayed"] = 0
        firstPlay["nextId"] = 1
        
        print(f"First Play: {firstPlay}")
        print(f"initbject: {initObject}")
        return initObject, firstPlay 
    

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

        # TODO: Change this so that prompt play can take in 
        #          play selected and determine if it valid.
        #           This will also allow the prompt play to deal with removing the cards.
        if not isSocket:
            cardsToPlay = self.players[self.turnIndex].promptCard(self.cardsOnTable)
            stepObj["play"] = cardsToPlay
            stepObj["playFromId"] = self.turnId
            stepObj["cardsPlayed"] = cardsToPlay
            stepObj["playFromId"] = self.turnId
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
        # newPlay Object:
        #   - PlayerID of person who played
        #   - Playername of the person who played
        #   - Cards played
        #   - Cards on table after

        # This is removed because socketIO is moved to new functions.
        #newPlay = {}
        #newPlay["playerID"] = self.players[turnIndex].id
        #newPlay["playerName"] = self.socketio.players[self.players[turnIndex].id]["name"]
        #newPlay["cardsPlayed"] = cardsToPlay

        # Add all the cards to the played cards list.
        for card in cardsToPlay: 
            self.cardsPlayed.append(card)
            
        if len(cardsToPlay) == 0: # The player passed
            #print("The player has passed")
            self.passedPlayers.append(self.players[self.turnIndex])
            passed = True

            if (self.lastPlayedIsFinished and (len(self.passedPlayers) == len(self.players))) or (not self.lastPlayedIsFinished and  (len(self.passedPlayers) == len(self.players) - 1)):
                self.lastPlayedIsFinished = False
                #print("All players have passed")
                self.cardsOnTable = []
                self.resetPlayers()
                self.passedPlayers = []
        else: 
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
        
        #newPlay["cardsOnTable"] = self.cardsOnTable
        #emit("newPlay", newPlay)
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


#def encodePlays(plays, value):
#    # Singles(14) go from 0-14
#    # Doubles(14) go from 15-28
#    # Tripples(13) go from 28-40
#    # Bombs(13) go from 41-53
#    encodedArr = np.zeros(54)
#    doublesPadding = 14
#    tripplesPadding = 28
#    bombsPadding = 41
#
#    for play in plays:
#        if len(play) == 1:
#            encodedArr[play[0]-1] = value
#        elif len(play) == 2:
#            encodedArr[doublesPadding + (play[0]-1)] = value
#        elif len(play) == 3:
#            encodedArr[tripplesPadding + (play[0]-1)] = value
#        elif len(play) == 4:
#            encodedArr[bombsPadding + (play[0]-1)] = value
#        elif len(play) > 4:
#            raise Exception("A play was tried to be encoded that was larger than 4")
#    return encodedArr


if __name__ == "__main__":
    '''
    for i in range(1000):
        if i % 100 == 0:
            print(f"Game: {i}")
        game_obj = Game()
        filename = f"GameLogs/gameFile{i}.csv"
        game_obj.outputLogToFile(filename)
        dataTable = game_obj.getTrainingData()
    '''
    #a = [1,1,2,3,4,5]
    #a.remove(1)
    #print(f"{a}")
    #game_obj = Game()

    #filename = f"testfile.csv"
    #game_obj.outputLogToFile(filename)
    #gameMatrix = np.loadtxt(filename, delimiter = ",")
    #gameMatrix = gameMatrix.reshape((-1, 263))
    #for i in range(len(gameMatrix)):
    #    play = gameMatrix[i]
    #    playerID, oponentNumberOfcards, cardsInHand, cardsOnTable, cardsPlayed, playChosen = np.split(play, [1, 46, 100, 154, 208])
    #    print("Encoded Values:")
    #    print(f"PlayerID: {playerID}")
    #    print(f"oponentNumberOfCards: {oponentNumberOfcards}")
    #    print(f"cardsInHand: {cardsInHand}")
    #    print(f"cardsOnTable: {cardsOnTable}")
    #    print(f"cardsDiscarded: {cardsPlayed}")
    #    print(f"playChosen: {playChosen}")
    #    print("===========================================")
    '''
    print("Decoded Values:")
    print(f"PlayerID: {playerID}")
    print(f"playersIn: {playersIn}")
    print(f"cardsInHand: {cardsInHand}")
    print(f"cardsOnTable: {cardsOnTable}")
    print(f"cardsPlayed: {cardsPlayed}")
    print(f"playChosen: {playChosen}")
    '''
    


    


