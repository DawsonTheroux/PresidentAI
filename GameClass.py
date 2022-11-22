import PlayerModule
import numpy as np
import pandas as pd
import os
import copy
from CardInterfaces import getPossiblePlays
from CardInterfaces import encodePlays


# TODO: Fix aces (Maybe just rework the ordering of the cards in general)
#   - This is kinda unecessary
# TODO: Create Log

class Game:

    def __init__(self, gametype=0, model=None):
        self.players = []
        self.cards = []
        self.cardsPlayed = []
        self.cardsOnTable = []   # Array of cards on the table (can be 1,2,3,4)
        self.standings = []
        self.passedPlayers = []
        self.autoAss = []
        self.logArray = []
        self.encodedPlayedCards = np.zeros(54)
        self.assignPlayers(gametype, model)    # This will set self.players array to Player Objects.
        self.dealCards()        # Sets the Player.hand attribute
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

    def assignPlayers(self, gameType=0, model=None):

        if gameType != 0:
            for i in range(6):
                self.players.append(PlayerModule.Player(2,i, model, self))
            #for i in range(2):
                #self.players.append(PlayerModule.Player(1, i)) # Right now this is generating all CMD line players
        else:
            for i in range(6): #self.players.append(PlayerModule.Player(0, i)) # Right now this is generating all CMD line players else:
                    self.players.append(PlayerModule.Player(1, i)) # Right now this is generating all CMD line players
        

    def printResults(self):
        resultsArr = []
        for player in self.standings:
            resultsArr.append(player)
        for player in self.autoAss:
            resultsArr.append(player)
        
        for i, player in enumerate(resultsArr):
            print(f"{i}. Player({player.id})")

        return resultsArr

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
        for player in self.autoAss:
            finalStandings.append(player)
        
        allCardsPlayed = []
        allCardsEncoded = np.zeros(54)
        for i, logObject in enumerate(self.logArray):
            # Encode possible Plays
            possiblePlaysEncoded = encodePlays(logObject["possiblePlays"], 1)
            cardsOntable = encodePlays([logObject["cardsOnTable"]], 1)

            handEncoded = np.zeros(54)
            for card in logObject["cardsInHand"]:
                handEncoded = self.encodeCardInPlayed(card, handEncoded)
            

            # Encode the play that the player played
            playerScore = -1
            for i, player in enumerate(finalStandings):
                if player.id == logObject["id"]:
                    playerScore = 6 - i
                    break

            # Encode is the player passed
            playerPass = [0]
            if len(logObject["cardsPlayed"]) == 0:
                playerPass = [playerScore]

            cardsPlayedEncoded = encodePlays([logObject["cardsPlayed"]], playerScore)
            # label is playerPass + cardsPlayedEncoded
            #outputRow = np.hstack((logObject["encodedPlayersIn"], possiblePlaysEncoded, handEncoded, cardsOntable, allCardsEncoded, playerPass, cardsPlayedEncoded))
            outputRow = np.hstack((logObject["encodedPlayersIn"], handEncoded, cardsOntable, allCardsEncoded, playerPass, cardsPlayedEncoded))
            if len(outputArray) == 0:
                outputArray = outputRow
            else:
                outputArray = np.vstack((outputArray, outputRow))

            # Encode the all the cards in the cards played.
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
                    else:
                        self.standings.append(self.players[turnIndex])
                    lastPlayedIsFinished = True
                    self.players.pop(turnIndex)

                if len(self.players) == 1:
                    self.standings.append(self.players[0])
                    gameOver = True 
                    break
                
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
    game_obj = Game()
    filename = f"testfile.csv"
    game_obj.outputLogToFile(filename)

