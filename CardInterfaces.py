import numpy as np
import torch
import copy
#from GameClass import encodePlays


class CommandLineInterface:
    # Prompts the command line to enter a card.
    def promptCard(self, player, cardsOnTable):
        cardNotChosen = True
        tempHand = player.hand.copy()
        print(getPossiblePlays(player.hand, cardsOnTable))
        while cardNotChosen:
            print(f" The cards on Table {cardsOnTable}")
            userInput = input(f"Player({player.id}) Please choose a card: {np.sort(player.hand)}: ").split(',')

            cardsToPlay = []
            for card in userInput:
                try:
                    cardInt = (int)(card)
                except:
                    break
                cardsToPlay.append(cardInt)
            
            try:
                if cardsToPlay[0] == 0: cardsToPlay = []
            except:
                continue

            #print(f"checkCardsInHand(cardToPlay,player.hand: {checkCardsInHand(cardsToPlay, player.hand)}")
            #print(f"isValidCard(cardsToPlay, player.hand: {isValidCard(cardsToPlay, cardsOnTable)}")
            if checkCardsInHand(cardsToPlay, player.hand) and  isValidCard(cardsToPlay, cardsOnTable):
                # Remove the cards from the players hand and return
                removeCardsFromHand(cardsToPlay, player)
                cardNoChosen = False
                return cardsToPlay

def encodePlays(plays, value, oneHot=-1):
    # Singles(14) go from 0-14
    # Doubles(14) go from 15-28
    # Tripples(13) go from 28-40
    # Bombs(13) go from 41-53
    if oneHot == -1:
        encodedArr = -np.ones(54)
    elif oneHot == 0:
        encodedArr = np.zeros(54)
    else:
        assert False, "encodePlays(plays,value,oneHot=-1): must send oneHot value of 0 or -1"

    #doublesPadding = 14
    #tripplesPadding = 28
    #bombsPadding = 41

    #for play in plays:
    #    if len(play) == 1:
    #        encodedArr[play[0]-1] = value
    #    elif len(play) == 2:
    #        encodedArr[doublesPadding + (play[0]-1)] = value
    #    elif len(play) == 3:
    #        encodedArr[tripplesPadding + (play[0]-1)] = value
    #    elif len(play) == 4:
    #        encodedArr[bombsPadding + (play[0]-1)] = value
    #    elif len(play) > 4:
    #        raise Exception(f"A play was tried to be encoded that was larger than 4: {play}")
    #return encodedArr

    #----Encode Plays by smallest to largest values---.
    for play in plays:
        if len(play) == 0:
            return encodedArr
        playNumber = play[0]
        if play[0] == 2:
            playNumber = 12
        elif play[0] == 3:
            playNumber = 13
        elif play[0] > 3 and play[0] < 14:
            playNumber = play[0] - 2

        if len(play) == 1:            
            encodedArr[((playNumber-1) * 4)] = value
        elif len(play) == 2:
            encodedArr[((playNumber-1) * 4) + 1] = value
        elif len(play) == 3:
            encodedArr[((playNumber-1) * 4) + 2] = value
        elif len(play) == 4:
            encodedArr[((playNumber-1) * 4) + 3] = value
        else:
            raise Exception(f"Tried to encode a play larger than 4")
    return encodedArr


def getBombs(hand):
    # Returns an array of all the bomb types (i.e. 4,6 means there are bombs of 4s and 6sii)
    bombsArray = []
    for card in hand:
        if hand.count(card) == 4:
            bombsArray.append(card)
    return bombsArray


def getPossiblePlays(hand, cardsOnTable):
    # Retruns an array of all the possible options.
    possiblePlays = [] # Array of arrays
    bombList = getBombs(hand)

    if len(cardsOnTable) == 4:
        # Add the bombs that are bigger than the bomb on the table.
        for card in cardsOnTable:
            for bomb in bombList:
                if bomb >= card:
                    possiblePlays.append([bomb, bomb, bomb, bomb])
    else:
        for bomb in bombList:
            possiblePlays.append([bomb,bomb,bomb,bomb])

    # Don't need to handle 14 because all bombs are already added.

    if 3 in cardsOnTable:
        if 14 in hand:
            possiblePlays.append([14])

    elif 2 in cardsOnTable:
        if 14 in hand:
            possiblePlays.append([14])
        if 3 in hand:
            possiblePlays.append([3])

    elif len(cardsOnTable) > 0 and 14 not in cardsOnTable and 3 not in cardsOnTable and 2 not in cardsOnTable and len(cardsOnTable) < 4:   # If the top is not a powercard or bomb
        if 14 in hand:
            possiblePlays.append([14])
        if 3 in hand:
            possiblePlays.append([3])
        if 2 in hand and len(cardsOnTable) < 3:
            possiblePlays.append([2])
        if 2 in hand and len(cardsOnTable) == 3 and hand.count(2) > 1:
            possiblePlays.append([2,2])

        for card in np.unique(np.array(hand)):
            if card >= cardsOnTable[0] and hand.count(card) >= len(cardsOnTable) and card != 2 and card != 3 and card != 14:
                tempArr = []
                for _ in range(len(cardsOnTable)):
                    tempArr.append(card)
                possiblePlays.append(tempArr)
                continue
    
    elif len(cardsOnTable) == 0:
        # Add all the singles, doubles, tripples
        for card in np.unique(np.array(hand)):
            #print(f"Appending {card}")
            possiblePlays.append([card])
            if hand.count(card) >= 2:
                possiblePlays.append([card, card]) 
            if hand.count(card) >= 3:
                possiblePlays.append([card,card,card])
    return possiblePlays


class RandomCardInterface:
    def promptCard(self, player, cardOnTable):
        possiblePlays = getPossiblePlays(player.hand, cardOnTable)
        play = []
        #print(f" The cards on Table {cardOnTable}")
        #print(f"Player({player.id}) Please choose a card: {np.sort(player.hand)}")
        if len(possiblePlays) > 0:
            if len(cardOnTable) > 0:
                randomPlay = np.random.randint(len(possiblePlays) +1)
            else:
                randomPlay = np.random.randint(len(possiblePlays))
            #print(f"Random Play chosen: {randomPlay} - len(possiblePlays): {len(possiblePlays)}")
            if randomPlay >= len(possiblePlays):
                play = []
            else:
                play = possiblePlays[randomPlay]
                removeCardsFromHand(play, player)

            # Pick 1 of the possible plays

        # Get all available options
        # If the list of availble options is nothing,k
        # Pick a random option 
        #print(f"--Player({player.id})--")
        #print(f"CardsOnTable: {cardOnTable}")
        #print(f"PlayerHand: {player.hand}")
        #print(f"Play: {play}")
        #print("----------------")
        return play


class AIModelInterface:
    # Generates what card to play using the trained model
    # (If the max prob is low enough then pass turn??)
    def __init__(self, game, model):
        self.model = model
        self.game = game

    def encodeCardsInHand(self, hand):
        encodedHand = -np.ones(54)
        for i, card in enumerate(hand):
            valueSet = False
            valueIndex = (card-1) * 4
            while(not valueSet):
                if encodedHand[valueIndex] == 1:
                    valueIndex += 1
                else:
                    encodedHand[valueIndex] = 1
                    valueSet = True
        return encodedHand 


    def promptCard(self, player, cardsOnTable):
        #print(f"Prompting AI player({player.id}) for a card")
        device = "cuda"
        #print(f"({player.id}): Cards On Table: {cardsOnTable}")
        possiblePlays = getPossiblePlays(player.hand, cardsOnTable)
        #print(f"({player.id}): possiblePlays: {possiblePlays}")
        #print(f"({player.id}): hand: {player.hand}")
        #print(f"Cards On Table: {cardsOnTable}")
        #print(f"PossiblePlays: {possiblePlays}")
        possiblePlaysEncoded = encodePlays(possiblePlays,1)
        #print(f"Possible plays encoded {possiblePlaysEncoded}")
        if len(possiblePlays) == 0:
            return []
        #print(f"size of possiblePlays {possiblePlaysEncoded.shape}")
        cardsOnTableEncoded = encodePlays([cardsOnTable], 1)
        encodedHand = self.encodeCardsInHand(player.hand)
        #print(f"size of cardsOnTable {cardsOnTableEncoded.shape}")
        #print(f"size of encoded played cards: {self.game.encodedPlayedCards}")
        encodedPlayers = -np.ones(6)
        for i in range(len(self.game.players)):
            encodedPlayers[i] = 1
            
        self.model.eval()
        
        # Data structuure: possiblePlayesEncoded(54), cardsOnTable, All cards enccoded(54)
        topPredsArr = []
        #data = np.hstack((encodedPlayers, possiblePlaysEncoded, encodedHand, cardsOnTableEncoded, self.game.encodedPlayedCards))
        '''
        print(f"EncodedPlayersIn: {encodedPlayers}")
        print(f"Hand: {player.hand}")
        print(f"encodedHand: {encodedHand}")
        print(f"cardsOnTable: {cardsOnTable}")
        print(f"encodedCardsOnTable: {cardsOnTableEncoded}")
        print(f"discardedCards: {self.game.encodedPlayedCards}")
        '''
        data = np.hstack((encodedPlayers, encodedHand, cardsOnTableEncoded, self.game.encodedPlayedCards))
        with torch.no_grad():
            #print(f"data.shape {data.shape}")
            if device == "cpu":
                data = torch.from_numpy(data).float().cpu()
            else:
                data = torch.from_numpy(data).float().cuda()
            output = self.model(data)
            #topPreds = torch.topk(output, 3)
            #if len(cardsOnTable) == 0:
            if True:
                topPredsArr = torch.topk(output, 55).indices.tolist()
            #else:
                #topPredsArr = torch.topk(output, 3).indices.tolist()



        play = []
        for i, predInd in enumerate(topPredsArr):
            candidate = decodePlay(predInd)
            if candidate == [] and len(cardsOnTable) != 0:#  and i == 0:
                break
            elif possiblePlaysEncoded[predInd-1] != -1:
                play = candidate
                removeCardsFromHand(play,player)
                break
        
        #print(f"({player.id})Candidate: {candidate} - {predInd}")
        #print(f"({player.id})possiblePlaysEncoded: {possiblePlaysEncoded} - {predInd}")
        #print(f'({player.id})Playing: {play}') 
        #print("--------------------------------")
        return play

def decodePlay(codeIndex):
    # Decode plays by index.
    # Plays go in order 0 =1; 1=1,1; 44=2; 45=2,2
    if(codeIndex == 0):
        return []
    codeIndex = codeIndex - 1
    for i in range(14):
        candidateIndex = i * 4
        if codeIndex >= candidateIndex and codeIndex <= candidateIndex + 3:
            break
    
    numberOfCards = (codeIndex - candidateIndex) + 1
    card = (candidateIndex / 4) + 1
    if card == 12:
        card = 2
    elif card == 13:
        card = 3
    elif card > 1 and card < 12:
        card = card + 2

    play = []
    card = int(card)
    for i in range(numberOfCards):
        play.append(card)

    return play
    
#for i in range(14):
    #play = []
    #for j in range(4):
        #play.append(i + 1)
        #encoded = encodePlays([copy.deepcopy(play)], 1)
        #print(f"Encoded {play} - {np.argmax(encoded)} - {encoded}")
        #print(f"Decoded - {decodePlay(np.argmax(encoded) + 1)}")
        #print('-----')
#exit(0)
        


def isValidCard(cardsToPlay, cardsOnTable):
    # Check if the cardToPlay is valid against the cardsOnTable 
    # Cards to play should be an array 
    # Empty array is pass
    #print(f" Cards on table {cardsOnTable}")
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
        if (3 not in cardsOnTable) and (14 not in cardsOnTable) and (len(cardsOnTable) < 4):
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
            if cardsToPlay[0] == 2 and cardsOnTable[0] != 3 and 14 not in cardsOnTable:
                return True
            elif cardsToPlay[0] == 3 and 14 not in cardsOnTable:
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
    for i, card in enumerate(cardsToPlay):
        for j, cardInHand in enumerate(cardsInHandCopy):
            if card == cardInHand:
                cardsInHandCopy.pop(j)
                break

    #print(f"len(cardstoPlay): {len(cardsToPlay)} - len(cardsInHand): {len(cardsInHand)} - len(cardsInHandCopy): {len(cardsInHandCopy)}")
    return len(cardsToPlay) == (len(cardsInHand) - len(cardsInHandCopy))

def removeCardsFromHand(cardsToPlay, player):
    if len(cardsToPlay) == 0:
        return

    for j, cardToPlay in enumerate(cardsToPlay):
        for i, card in enumerate(player.hand):
            if card == cardToPlay:
                player.hand.pop(i)
                break 
        
