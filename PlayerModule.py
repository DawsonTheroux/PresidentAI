import numpy as np
import CardInterfaces

class Player:
    def __init__(self, interfaceType, id):
        self.hand = []
        self.cardInterface = None
        self.id = id
        self.playedHand = False
        if interfaceType == 0:
            self.cardInterface = CardInterfaces.CommandLineInterface()
        elif interfaceType == 1:
            self.cardInterface = CardInterfaces.RandomCardInterface()
        elif interfaceType == 2:
            self.cardInterface = CardInterfaces.AIModelInterface()
        else:
            print("That is not a card interface")

    def assignCards(self, cardList):
        self.hand = cardList
        
    def promptCard(self, cardOnTable):
        # Calls the interface to play a card.
        #TODO: Is there a polymorphic way to call this??
        # 0 will be pass. Returns an array.
        cardsToPlay = self.cardInterface.promptCard(self, cardOnTable)
        if len(cardsToPlay) > 0:
            self.playedHand = True

        return cardsToPlay