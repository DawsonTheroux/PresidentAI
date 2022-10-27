import PlayerModule
import numpy as np
import pandas as pd


# TODO: Fix aces (Maybe just rework the ordering of the cards in general)
#   - This is kinda unecessary
# TODO: Create Log

class Game:

    def __init__(self):
        self.players = []
        self.cards = []
        self.cardsPlayed = []
        self.cardsOnTable = []   # Array of cards on the table (can be 1,2,3,4)
        self.standings = []
        self.passedPlayers = []
        self.autoAss = []
        self.assignPlayers()    # This will set self.players array to Player Objects.
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

        for player in self.players:
            print(f"player({player.id}): {player.hand}")

    def assignPlayers(self):
        for i in range(6):
            #self.players.append(PlayerModule.Player(0, i)) # Right now this is generating all CMD line players
            self.players.append(PlayerModule.Player(1, i)) # Right now this is generating all CMD line players
        

    def isValidCard(self, cardsToPlay):
        # Check if the cardToPlay is valid against the cardsOnTable 
        # Cards to play should be an array 
        # Empty array is pass
        if len(cardsToPlay) == 0:
            return True

        # Check if all the cardsToPlay are the same
        cardType = cardsToPlay[0]
        for card in cardsToPlay:
            if cardType != card:
                return False

        # Check if the cards played was a powercard
        if 2 in cardsToPlay:
            # Check if the 2 is trying to be played on a powercard or bomb
            if 2 not in self.cardsOnTable and 3 not in self.cardsOnTable and 14 not in self.cardsOnTable and len(self.cardsOnTable) < 4:
                # Make sure the 2 was not played on tripples
                if len(cardsToPlay) >= len(self.cardsOnTable) - 1:
                    return True
        
        if 3 in cardsToPlay:
            # Check if the 3 is trying to be played on a powercard or bomb
            if 3 not in self.cardsOnTable and 14 not in self.cardsOnTable and len(self.cardsOnTable) < 4:
                return True

        if 14 in cardsToPlay:
            # Check if the 2 is trying to be played on a powercard
            if 14 not in self.cardsOnTable and len(self.cardsOnTable) < 4:
                return True
            
        if len(cardsToPlay) == len(self.cardsOnTable):

            # Check if the cards is of greater value
            if cardsToPlay[0] > self.cardsOnTable[0]:
                return True
            if cardsToPlay[0] == self.cardsOnTable[0] and cardsToPlay[0] != 2 and cardsToPlay[0] != 3 and cardsToPlay[0] != 14:
                return True
            
            # If a lower card was played check for 2, 3
            if cardsToPlay[0] < self.cardsOnTable[0]:
                if cardsToPlay[0] == 2 and self.cardsOnTable[0] != 3:
                    return True
                elif cardsToPlay[0] == 3:
                    return True
        
        if len(cardsToPlay) == 4:
            if len(self.cardsOnTable) == 4:
                # Check if the cards is of greater value
                if cardsToPlay[0] > self.cardsOnTable[0]:
                    return True
                if cardsToPlay[0] == self.cardsOnTable[0] and cardsToPlay[0] != 2 and cardsToPlay[0] != 3 and cardsToPlay[0] != 14:
                    return True
            
                # If a lower card was played check for 2, 3
                if cardsToPlay[0] < self.cardsOnTable[0]:
                    if cardsToPlay[0] == 2 and self.cardsOnTable[0] != 3:
                        return True
                    elif cardsToPlay[0] == 3:
                        return True 

            else:
                return True

        # The card is not value at this point
        return False 
    

    def printResults(self):
        resultsArr = []
        for player in self.standings:
            resultsArr.append(player)
        for player in self.autoAss:
            resultsArr.append(player)
        
        for i, player in enumerate(resultsArr):
            print(f"{i}. Player({player.id})")

        return resultsArr

    def createGameFile(self, fileString, results):
        fileString += "\n\nResults:\n"
        positions = ["President", "Vice President", "Neutral1", "Neutral2", "Vice Ass", "Ass"]
        for i, player in enumerate(results):
            fileString += f"{positions[i]}; Player({player.id})\n"

        fileName = "GameFile.csv"

        outputFile = open(f"GameLogs/{fileName}", "w")
        outputFile.write(fileString)
        outputFile.close()
        
    def gameLoop(self):
        # Prompt the players for cards
        # Choose a random player with a 4 to start.
        turnIndex = 0
        fileString = "Turn; Cards on table; Hand; Card Played; IsDone?\n"
        gameOver = False
        lastPlayedIsFinished = False
        # One loop is one players turn
        while not gameOver:
            # Problem: If everyone passes on the last card played, the turn is assigned ot the wrong player.
            print("\n")
            isBurn = False
            isFinished = False
            passed = False
            
            # prompt the player at player index for a card.
            #print(f"Num players: {len(self.players)} - Prompting Player: {turnIndex}")
            fileString += f"Player({self.players[turnIndex].id});{self.cardsOnTable};{self.players[turnIndex].hand};"
            cardsToPlay = self.players[turnIndex].promptCard(self.cardsOnTable)

            # Add all the cards to the played cards list.
            for card in cardsToPlay: 
                self.cardsPlayed.append(card)
            
            if len(cardsToPlay) == 0: # The player passed
                print("The player has passed")
                fileString += "passed"
                self.passedPlayers.append(self.players[turnIndex])
                passed = True

                if (lastPlayedIsFinished and (len(self.passedPlayers) == len(self.players))) or (not lastPlayedIsFinished and  (len(self.passedPlayers) == len(self.players) - 1)):
                    lastPlayedIsFinished = False
                    print("All players have passed")
                    fileString += "(All Players)"
                    self.cardsOnTable = []
                    self.passedPlayers = []
                fileString += ";"
            else: 
                if len(self.cardsOnTable) != 0 and cardsToPlay[0] == self.cardsOnTable[0]:
                    lastPlayedIsFinished = False
                    fileString += f"{cardsToPlay} (BURN);"
                    self.passedPlayers = []
                    print("***BURN****")
                    self.cardsOnTable = []
                    isBurn = True
                else:
                    fileString += f"{cardsToPlay};"
                    lastPlayedIsFinished = False
                    self.passedPlayers = []
                    self.cardsOnTable = cardsToPlay
            
                #TODO: Check to see if all players have passed

                if len(self.players[turnIndex].hand) == 0:
                    if 2 in cardsToPlay or 3 in cardsToPlay or 14 in cardsToPlay: # The player is autoAss for finishing on a powercard
                        fileString += f"DONE (autoAss);"
                        self.autoAss.append(self.players[turnIndex])
                    else:
                        fileString += f"DONE;"
                        self.standings.append(self.players[turnIndex])
                    lastPlayedIsFinished = True
                    print(f"Player({self.players[turnIndex].id}) has been added to the standings")
                    print("Standings:")
                    for player in self.standings:
                        print(f"Player({player.id})")
                    print("AutoAss:")
                    for player in self.autoAss:
                        print(f"Player({player.id})")
                    self.players.pop(turnIndex)
                    print("Players In Game:")
                    for player in self.players:
                        print(f"Player({player.id})")

                if len(self.players) == 1:
                    self.standings.append(self.players[0])
                    fileString += "\nGAME OVER"
                    gameOver = True 
                    break

            fileString += "\n"
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

        results = self.printResults() 
        self.createGameFile(fileString, results)

        

if __name__ == "__main__":
    game_obj = Game()

