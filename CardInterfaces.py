import numpy as np


class CommandLineInterface:
    # Prompts the command line to enter a card.
    def promptCard(self, player, cardsOnTable):
        cardNotChosen = True
        tempHand = player.hand.copy()
        while cardNotChosen:
            print(f" The cards on Table {cardsOnTable}")
            userInput = input(f"Player({player.id}) Please choose a card: {np.sort(player.hand)}: ").split(',')

            cardsToPlay = []
            for card in userInput:
                cardInt = (int)(card)
                cardsToPlay.append(cardInt)
            if cardsToPlay[0] == 0: cardsToPlay = []

            print(f"checkCardsInHand(cardToPlay,player.hand: {checkCardsInHand(cardsToPlay, player.hand)}")
            print(f"isValidCard(cardsToPlay, player.hand: {isValidCard(cardsToPlay, cardsOnTable)}")
            if checkCardsInHand(cardsToPlay, player.hand) and  isValidCard(cardsToPlay, cardsOnTable):
                # Remove the cards from the players hand and return
                print(f"The players hand before removing the cards: {player.hand}")
                removeCardsFromHand(cardsToPlay, player)
                print(f"The players hand after removing the cards: {player.hand}")
                print(f"The cards to play {cardsToPlay}")
                cardNoChosen = False
                return cardsToPlay



class RandomCardInterface:
    # Randomly selects a card to be played (Play must be legal)
    # Used for inital Model Input data 
    def promptCard(self, hand, cardOnTable):
        print("Prompting random player for a card")


class AIModelInterfaceInterface:
    # Generates what card to play using the trained model
    # (If the max prob is low enough then pass turn??)
    def promptCard(self, hand, cardOnTable):
        print("Prompting AI player for a card")

def isValidCard(cardsToPlay, cardsOnTable):
    # Check if the cardToPlay is valid against the cardsOnTable 
    # Cards to play should be an array 
    # Empty array is pass
    print(f" Cards on table {cardsOnTable}")
    if len(cardsToPlay) == 0 or len(cardsOnTable) == 0:
        return True


    # Check if all the cardsToPlay are the same
    cardType = cardsToPlay[0]
    for card in cardsToPlay:
        if cardType != card:
            return False

    # Check if the cards played was a powercard
    if 2 in cardsToPlay:
        # Check if the 2 is trying to be played on a powercard or bomb
        if 2 not in cardsOnTable and 3 not in cardsOnTable and 14 not in cardsOnTable and len(cardsOnTable) < 4:
            # Make sure the 2 was not played on tripples
            if len(cardsToPlay) >= len(cardsOnTable) - 1:
                return True
    
    if 3 in cardsToPlay:
        # Check if the 3 is trying to be played on a powercard or bomb
        if 3 not in cardsOnTable and 14 not in cardsOnTable and len(cardsOnTable) < 4:
            return True

    if 14 in cardsToPlay:
        # Check if the 2 is trying to be played on a powercard
        if 14 not in cardsOnTable and len(cardsOnTable) < 4:
            return True
        
    # The cardsToPlay cannot be a powercard, so just don't set to true if the card on the table is a 2 or 3
    if len(cardsToPlay) == len(cardsOnTable):
        # Check if the cards is of greater value
        if cardsToPlay[0] > cardsOnTable[0] and cardsOnTable[0] != 2 and cardsOnTable[0] != 3:
            return True
        if cardsToPlay[0] == cardsOnTable[0] and cardsToPlay[0] != 2 and cardsToPlay[0] != 3 and cardsToPlay[0] != 14:
            return True
        
        # If a lower card was played check for 2, 3
        if cardsToPlay[0] < cardsOnTable[0]:
            if cardsToPlay[0] == 2 and cardsOnTable[0] != 3:
                return True
            elif cardsToPlay[0] == 3:
                return True
    
    if len(cardsToPlay) == 4:
        if len(cardsOnTable) == 4:
            # Check if the cards is of greater value
            if cardsToPlay[0] > cardsOnTable[0]:
                return True
            if cardsToPlay[0] == cardsOnTable[0] and cardsToPlay[0] != 2 and cardsToPlay[0] != 3 and cardsToPlay[0] != 14:
                return True
        
            # If a lower card was played check for 2, 3
            if cardsToPlay[0] < cardsOnTable[0]:
                if cardsToPlay[0] == 2 and cardsOnTable[0] != 3:
                    return True
                elif cardsToPlay[0] == 3:
                    return True 

        else:
            return True

    # The card is not value at this point
    return False 

def checkCardsInHand(cardsToPlay, cardsInHand):
    # Check if all the cards in the hand by removing them from the cards in hand.
    #  If the number of cards removed is equal to the number of cards they want to play, then it is successfull.
    if len(cardsToPlay) == 0:
        return True
        
    cardsInHandCopy = cardsInHand.copy()
    for j, cardInHand in enumerate(cardsInHandCopy):
        for i, card in enumerate(cardsToPlay):
            if card == cardInHand:
                cardsInHandCopy.pop(j)
                break

    return len(cardsToPlay) == len(cardsInHand) - len(cardsInHandCopy)

def removeCardsFromHand(cardsToPlay, player):
    if len(cardsToPlay) == 0:
        return

    for i, card in enumerate(player.hand):
        for j, cardToPlay in enumerate(cardsToPlay):
            if card == cardToPlay:
                player.hand.pop(i)
                continue
        
