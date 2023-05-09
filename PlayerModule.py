import numpy as np
import CardInterfaces

# Class that holds the card interface. This class is responsible for keeping track of the cards in a players hand.
class Player:
    def __init__(self, interfaceType, id, model = None, game = None, socketio=None ):
        self.hand = []
        self.cardInterface = None
        self.playedHand = False
        self.socketio = socketio # Only used for online play, set to None otherwise.

        # Use the CommandLineInterface
        if interfaceType == 0:
            self.id = id
            self.cardInterface = CardInterfaces.CommandLineInterface()

        # Use the RandomCardInterface.
        elif interfaceType == 1:
            self.id = id + 0.1
            #self.id = id
            self.cardInterface = CardInterfaces.RandomCardInterface()
        
        # Use the AIModelInterface.
        elif interfaceType == 2:
            self.id = id
            self.cardInterface = CardInterfaces.AIModelInterface(game, model)
        
        # Use the SocketInterface (for website)
        elif interfaceType == 3:
            self.id = id
            self.cardInterface = CardInterfaces.SocketInterface()

        else:
            print("That is not a card interface")

    def assignCards(self, cardList):
        self.hand = cardList
        
    # TODO: There is probably an OOP way to call this.
    # TODO: Also, this class should handle getting rid of cards, not the interface.
    def promptCard(self, cardOnTable):
        cardsToPlay = self.cardInterface.promptCard(self, cardOnTable)
        if len(cardsToPlay) > 0:
            self.playedHand = True

        return cardsToPlay