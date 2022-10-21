import PlayerModule
import numpy as np
import pandas as pd


# TODO: Fix the logic for playing a card:
    # - hasCardInHand is returning false when you try and slit doubles
# TODO: Fix passing logic, if everyone passes the table isnt cleared.
# TODO: Fix aces (Maybe just rework the ordering of the cards in general)

class Game:

    def __init__(self):
        self.players = []
        self.cards = []
        self.cardsPlayed = []
        self.cardsOnTable = []   # Array of cards on the table (can be 1,2,3,4)
        self.standings = []
        self.passedPlayers = []
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
            self.cards.append(tempCards.pop(np.random.randint(len(tempCards))))

        # Split the array into len(self.players) parts.
        cardsPerHand = np.ceil(len(self.cards) / len(self.players))     # Get the number of cards per hand
        for i, player in enumerate(self.players):
            startIndex = (int)(i * cardsPerHand)
            endIndex = (int)((i + 1) * cardsPerHand)
            if endIndex > len(self.cards):
                endIndex = len(self.cards)

            cardsToAssign = self.cards[startIndex: endIndex]
            player.assignCards(self.cards[startIndex: endIndex])


    def assignPlayers(self):
        for i in range(6):
            self.players.append(PlayerModule.Player(0, i)) # Right now this is generating all CMD line players
        

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
    

    def gameLoop(self):
        # Prompt the players for cards
        print("gameLoop")
        # Choose a random player with a 4 to start.
        turnIndex = 0

        gameOver = False
        # One loop is one players turn
        while not gameOver:

            # prompt the player at player index for a card.
            cardsToPlay = self.players[turnIndex].promptCard(self.cardsOnTable)


            # Add all the cards to the played cards list.
            for card in cardsToPlay: 
                self.cardsPlayed.append(card)
            
            if len(cardsToPlay) == 0: # The player passed
                self.passedPlayers.append(self.players[turnIndex])
                if len(self.passedPlayers) == len(self.players):
                    self.passedPlayers = []
            else: 
                if len(self.cardsOnTable) != 0 and cardsToPlay[0] == self.cardsOnTable[0]:
                    self.passedPlayers = []
                    print("***BURN****")
                    self.cardsOnTable = []
                else:
                    self.passedPlayers = []
                    self.cardsOnTable = cardsToPlay
            
                #TODO: Check to see if all players have passed

                if len(self.players[turnIndex].hand) == 0:
                    standings.append(player[turnIndex])
                    self.players.pop(turnIndex)

                if len(self.players) == 0:
                    gameOver = True 
                    break

            turnIndex = (turnIndex + 1) % len(self.players)
                



            


        

if __name__ == "__main__":
    game_obj = Game()

