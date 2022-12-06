import PlayerModule
import numpy as np
import pandas as pd
import os
import copy
from CardInterfaces import getPossiblePlays
from CardInterfaces import encodePlays


# Disabled Auto Ass
# Things to try: Randomize game playing to learn new strategies during game(1,model)
# Implement a reinforcement learning with goal based reward.
# Discard the last play since it is almost guarenteed.

class Game:

    def __init__(self, gametype=0, model1=None, model2=None):
        self.players = []
        self.cards = []
        self.cardsPlayed = []
        self.cardsOnTable = []   # Array of cards on the table (can be 1,2,3,4)
        self.standings = []
        self.passedPlayers = []
        self.autoAss = []
        self.logArray = []
        self.encodedPlayedCards = -np.ones(54)
        self.assignPlayers(gametype, model1, model2)    # This will set self.players array to Player Objects.
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

    def assignPlayers(self, gameType=0, model1=None, model2=None):

        if gameType == 1: # All players a President model
            for i in range(6):
                self.players.append(PlayerModule.Player(2,i, model1, self))
            #for i in range(3):
                #self.players.append(PlayerModule.Player(1, i)) 
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
            self.players.append(PlayerModule.Player(0, 42.1)) # Right now this is generating all CMD line players
            for i in range(5): #self.players.append(PlayerModule.Player(0, i)) # Right now this is generating all CMD line players else:
                    self.players.append(PlayerModule.Player(1, i)) # Right now this is generating all CMD line players
        elif gameType == 5: #Evaluate Model
            for i in range(3):
                self.players.append(PlayerModule.Player(2,i, model1, self))
                self.players.append(PlayerModule.Player(2,i + 0.1, model2, self))
        

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

        encodedPlayers = -np.ones(6)
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

        scoreInfo = {}
        for i, player in enumerate(finalStandings):
            scoreInfo[player.id] = {}
            if i <= 2:
                scoreInfo[player.id]["score"] = 3 - i
            else:
                scoreInfo[player.id]["score"] = 2 - i
            scoreInfo[player.id]["numPlays"] = 0

        aiPlayerKeys = []
        for key in scoreInfo.keys():
            if int(key) == key:
                aiPlayerKeys.append(key)

        for logObject in self.logArray:
            scoreInfo[logObject["id"]]["numPlays"] += 1

        allCardsPlayed = []
        allCardsEncoded = -np.ones(54)
        
        for logObject in self.logArray:
            # Encode possible Plays 
            #playerScore = scoreInfo[logObject["id"]]["score"] / scoreInfo[logObject["id"]]["numPlays"]
            scoreInfo[logObject["id"]]["numPlays"] -= 1
            if len(logObject["possiblePlays"]) == 0:
                continue
            

            playerScore = scoreInfo[logObject["id"]]["numPlays"]
            #print(f'PlayerScore: {playerScore}')
            #print(f"({logObject['id']}) Num Plays Left: {scoreInfo[logObject['id']]['numPlays']}")
            #if len(logObject["cardsPlayed"]) > 0:
                #scoreInfo[logObject["id"]]["numPlays"] -= 1

            '''
            print(f"Cards In OnTable: {logObject['cardsOnTable']}")
            print(f"Cards Player:{logObject['cardsPlayed']}")
            print(f"PlayerHand: {logObject['cardsInHand']}")
            print(f"discardedCards: {allCardsPlayed}")
            print('------')
            '''

            autoAssThisTurn = False
            #possiblePlaysEncoded = encodePlays(logObject["possiblePlays"], 1)
            cardsOntable = encodePlays([logObject["cardsOnTable"]], 1)

            handEncoded = -np.ones(54)
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
            nonPowerCardsInHand = []
            for card in logObject["cardsInHand"]:
                if card != 2 and card != 3 and card != 14:
                    nonPowerCardsInHand.append(card)
            onlyPowerCardsInHand = len(nonPowerCardsInHand) == 0 # If there are only power cards in the users hand
            for card in logObject["cardsPlayed"]:
                for nonPowerCard in nonPowerCardsInHand:
                    if card == nonPowerCard:
                        nonPowerCardsInHand.remove(nonPowerCard)
                        break
            if len(nonPowerCardsInHand) == 0 and len(logObject["cardsInHand"]) > len(logObject["cardsPlayed"]):
                #scoreInfo[logObject["id"]]["score"] = -10
                playerScore = 20
                autoAssThisTurn = True

                
            cardsPlayedEncoded = encodePlays([logObject["cardsPlayed"]], playerScore, 0)
            
            # Only add Row if:
            # - If there is a mix of AI and Random, only add AI ids.
            # - If the player got autoAss this turn add it.
            if not (len(aiPlayerKeys) > 0 and logObject["id"] not in aiPlayerKeys) and not autoAssThisTurn and not onlyPowerCardsInHand: 
                outputRow = np.hstack((logObject["id"], logObject["encodedPlayersIn"], handEncoded, cardsOntable, allCardsEncoded, playerPass, cardsPlayedEncoded))
                if len(outputArray) == 0:
                    outputArray = outputRow
                else:
                    #outputArray = np.vstack((outputArray, outputRow))
                    #outputArray = np.vstack((outputRow, outputArray))
                    outputArray = np.vstack((outputArray,outputRow))

            # Add the cards to the cards played after the row has been added.
            for card in logObject["cardsPlayed"]:
                allCardsEncoded = self.encodeCardInPlayed(card, allCardsEncoded)
                allCardsPlayed.append(card)
            allCardsPlayed.sort()

            # Encode the all the cards in the cards played.

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
    '''
    gameMatrix = np.loadtxt(filename, delimiter = ",")
    gameMatrix = gameMatrix.reshape((-1, 224))
    for i in range(len(gameMatrix)):
        play = gameMatrix[i]
        playerID, playersIn, cardsInHand, cardsOnTable, cardsPlayed, playChosen = np.split(play, [1, 7, 61, 115, 169])
        print("Encoded Values:")
        print(f"PlayerID: {playerID}")
        print(f"playersIn: {playersIn}")
        print(f"cardsInHand: {cardsInHand}")
        print(f"cardsOnTable: {cardsOnTable}")
        print(f"cardsDiscarded: {cardsPlayed}")
        print(f"playChosen: {playChosen}")
        print("===========================================")
    '''
    '''
    print("Decoded Values:")
    print(f"PlayerID: {playerID}")
    print(f"playersIn: {playersIn}")
    print(f"cardsInHand: {cardsInHand}")
    print(f"cardsOnTable: {cardsOnTable}")
    print(f"cardsPlayed: {cardsPlayed}")
    print(f"playChosen: {playChosen}")
    '''
    


    


