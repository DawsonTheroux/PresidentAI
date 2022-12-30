import numpy as np
import CardInterfaces

class Player:
    def __init__(self, interfaceType, id, model = None, game = None, socketio=None ):
        self.hand = []
        self.cardInterface = None
        self.playedHand = False
        self.socketio = socketio
        if interfaceType == 0:
            self.id = id
            self.cardInterface = CardInterfaces.CommandLineInterface()
        elif interfaceType == 1:
            self.id = id + 0.1
            #self.id = id
            self.cardInterface = CardInterfaces.RandomCardInterface()
        elif interfaceType == 2:
            self.id = id
            self.cardInterface = CardInterfaces.AIModelInterface(game, model)
        elif interfaceType == 3: # Website socket player
            self.id = id
            self.cardInterface = CardInterfaces.SocketInterface()
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