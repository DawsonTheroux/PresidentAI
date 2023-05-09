import numpy as np
import torch
import copy
import sys


# Use the command line interface as the Card Interface a player.
class CommandLineInterface:
    def promptCard(self, player, cardsOnTable):
        cardNotChosen = True
        tempHand = player.hand.copy()
        while cardNotChosen:

            # Prompt the Command line for a card.
            print(f" The cards on Table {cardsOnTable}")
            userInput = input(f"Player({player.id}) Please choose a card: {np.sort(player.hand)}: ").split(',')

            # Validate that the card is in the users posession.
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

            # Remove the card from the players hand.
            if checkCardsInHand(cardsToPlay, player.hand) and  isValidCard(cardsToPlay, cardsOnTable):
                removeCardsFromHand(cardsToPlay, player)
                cardNoChosen = False
                return cardsToPlay


# Encodes the play into the one-hot value
def encodePlays(plays, value, oneHot=-1):
    # If oneHot is -1, then values are 1 or -1. If it is 0, then it is 1 or 0.

    # How cards are encoded: {Singles(14) go from 0-14}  {Doubles(14) go from 15-28} {Tripples(13) go from 28-40} {Bombs(13) go from 41-53}
    if oneHot == -1:
        encodedArr = -np.ones(54)
    elif oneHot == 0:
        encodedArr = np.zeros(54)
    else:
        assert False, "encodePlays(plays,value,oneHot=-1): must send oneHot value of 0 or -1"

    #Encode Plays by smallest to largest values (singles, doubles, tripples, bombs)
    for play in plays:
        
        # Convert the card number to its index (A,4,5,6,7,8,9,10,J,Q,K,2,3,Joker).
        if len(play) == 0:
            return encodedArr
        playNumber = play[0]
        if play[0] == 2:
            playNumber = 12
        elif play[0] == 3:
            playNumber = 13
        elif play[0] > 3 and play[0] < 14:
            playNumber = play[0] - 2

        # Convert the index to represent single, double, tripple, or bomb.
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


# Returns the bombs present in the hand.
def getBombs(hand):
    # Returns an array of all the bomb types (i.e. 4,6 means there are bombs of 4s and 6sii)
    bombsArray = []
    for card in hand:
        if hand.count(card) == 4:
            bombsArray.append(card)
    return bombsArray


# Returns an array of all the possible plays in the hand.
def getPossiblePlays(hand, cardsOnTable):
    possiblePlays = []
    bombList = getBombs(hand)

    # If the table is a bomb, only add bombs of higher value.
    if len(cardsOnTable) == 4:
        for card in cardsOnTable:
            for bomb in bombList:
                if bomb >= card:
                    possiblePlays.append([bomb, bomb, bomb, bomb])

    # If the table is not a bomb, add all possible bombs
    else:
        for bomb in bombList:
            possiblePlays.append([bomb,bomb,bomb,bomb])


    # If a 3 is on the table, add all the Jokers(14).
    if 3 in cardsOnTable:
        if 14 in hand:
            possiblePlays.append([14])
        
    # If a 2 is on the table, add all the 3s and Jokers(14).
    elif 2 in cardsOnTable:
        if 14 in hand:
            possiblePlays.append([14])
        if 3 in hand:
            possiblePlays.append([3])

    # If the top card is not a power card or a bomb, add all Jokers(14), 3s, 2s.
    # NOTE: If the table is tripples, don't add 2s unless the user has two 2s.
    elif len(cardsOnTable) > 0 and 14 not in cardsOnTable and 3 not in cardsOnTable and 2 not in cardsOnTable and len(cardsOnTable) < 4:   # If the top is not a powercard or bomb
        if 14 in hand:
            possiblePlays.append([14])
        if 3 in hand:
            possiblePlays.append([3])
        if 2 in hand and len(cardsOnTable) < 3:
            possiblePlays.append([2])
        if 2 in hand and len(cardsOnTable) == 3 and hand.count(2) > 1:
            possiblePlays.append([2,2])

        # Add all the non-powercards that are equal or higher to what is on the table.
        for card in np.unique(np.array(hand)):
            if card >= cardsOnTable[0] and hand.count(card) >= len(cardsOnTable) and card != 2 and card != 3 and card != 14:
                tempArr = []
                for _ in range(len(cardsOnTable)):
                    tempArr.append(card)
                possiblePlays.append(tempArr)
                continue
    
    # If there is nothing on the table, add all possible combinations of every card in the hand.
    elif len(cardsOnTable) == 0:
        for card in np.unique(np.array(hand)):
            possiblePlays.append([card])
            if hand.count(card) >= 2:
                possiblePlays.append([card, card]) 
            if hand.count(card) >= 3:
                possiblePlays.append([card,card,card])

    return possiblePlays


# Player that plays random legal plays. (Used for generating inital training data for the Neural Network.)
class RandomCardInterface:
    def promptCard(self, player, cardOnTable):
        possiblePlays = getPossiblePlays(player.hand, cardOnTable)
        play = []

        # If the random player has a legal play, select a random play.
        if len(possiblePlays) > 0:
            possiblePlaysInHand = getPossiblePlays(player.hand, [])

            # If it is not the Random players turn to lead, choose between passing and playing with equal probability.
            if len(cardOnTable) > 0:
                randomPlay = np.random.randint(len(possiblePlays) + (len(possiblePlaysInHand)))
            else:
                randomPlay = np.random.randint(len(possiblePlays))

            # If the random play is outside of the possible plays, it means pass.
            if randomPlay >= len(possiblePlays):
                play = []
            else:
                play = possiblePlays[randomPlay]
                removeCardsFromHand(play, player)       # Remove the cards from the hand.

        return play


# Uses a Neural Network to determine the random play.
class AIModelInterface:
    def __init__(self, game, model):
        self.model = model
        self.game = game

    # Encode the players hand (Needed for input to the NN)
    def encodeCardsInHand(self, hand):
        encodedHand = np.zeros(54)
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
        # Select the device to use. (CPU for website, CUDA for training)
        #device = "cuda"
        device = "cpu"

        # Get the possible plays to ensure the model picks a valid play.
        possiblePlays = getPossiblePlays(player.hand, cardsOnTable)
        possiblePlaysEncoded = encodePlays(possiblePlays,1, oneHot=0)

        # Pass if the model has no possible plays.
        if len(possiblePlays) == 0:
            return []


        cardsOnTableEncoded = encodePlays([cardsOnTable], 1, oneHot=0)
        encodedHand = self.encodeCardsInHand(player.hand)

        # Encode the number of players still in the game.
        encodedPlayers = np.zeros(6)
        for i in range(len(self.game.players)):
            encodedPlayers[i] = 1


        allPlayerIds = []
        oponentNumCardsObj = {}
        for p in self.game.players:
            allPlayerIds.append(p.id)
            oponentNumCardsObj[p.id] = np.hstack((np.ones(len(p.hand)), np.zeros(9-len(p.hand))))
        
        for p in self.game.standings:
            allPlayerIds.append(p.id)
            oponentNumCardsObj[p.id] = np.hstack((np.ones(len(p.hand)), np.zeros(9-len(p.hand))))
        
        # Get the seat of the current player to sort the cards in hands of the other players by the seat in respect to the current player.
        currentPos = allPlayerIds.index(player.id)
        playersSortedByCurrent = allPlayerIds[currentPos:] + allPlayerIds[:currentPos] # Get the ids where the first item is the current player
  
        # Get the number of cards
        otherPlayersNumCards = np.empty(0)
        for opId in playersSortedByCurrent:
            # Do not add the number of cards of the player this interface is attacked to.
            if opId == player.id:
                continue
            
            # Append the 1-hot representation of the number of cards in the players hand to the total list of oponent number of cards.
            if otherPlayersNumCards == np.empty(0):
                otherPlayersNumCards = oponentNumCardsObj[opId]
            else:
                otherPlayersNumCards = np.hstack((otherPlayersNumCards, oponentNumCardsObj[opId]))

        # Enable training mode (For an experiment with model performance).
        if self.game.enableDropout:
            self.model.train()
        else:
            self.model.eval()
        
        topPredsArr = [] # The best to worst plays.

        # Stack the input data for the model:
        #   - otherPlayerNumCards: The number of cards in the oponents hands starting from the player directly after the player of the interface.
        #   - encodedHand: The cards in the Interface players hand.
        #   - cardsOnTableEncoded: The cards on the table.
        #   - encodedPlayedCards: The cards that have already been played in the hand.
        data = np.hstack((otherPlayersNumCards, encodedHand, cardsOnTableEncoded, self.game.encodedPlayedCards))

        with torch.no_grad():
            if device == "cpu":
                data = torch.from_numpy(data).float().cpu()
            else:
                data = torch.from_numpy(data).float().cuda()
            output = self.model(data)
            topPredsArr = torch.topk(output, 55).indices.tolist()

        play = [] # The play selected by the model.

        # Special training mode that picks the top play 70% of the time, second best 15%, and third best 15%
        if self.game.isTrainingDataGerneration:
            randNum = np.random.rand()
            playNumber = 0

            # Pick the second best play.
            if randNum >= 0.70 and randNum <= 0.84:
                playNumber = 1

            # Pick the third best play
            elif randNum >= 0.85:
                playNumber = 2
            
            numTries = 0
            numTries -= playNumber
            for i, predInd in enumerate(topPredsArr):
                numTries += 1
                candidate = decodePlay(predInd)

                # If the play is pass and there ARE cards on the table, then pass is the selected play.
                if candidate == [] and len(cardsOnTable) != 0:#  and i == 0:
                    # If this is the playNumber we are selecting.
                    if playNumber == 0:
                        break
                    else:
                        playNumber -= 1
                
                # If this play is in the possible plays.
                elif possiblePlaysEncoded[predInd-1] != 0:
                    # If this is the playNumber we are selecting.
                    if playNumber == 0:
                        play = candidate
                        break
                    else:
                        playNumber -= 1

            # If there is nothing on the table and it tries to pass, pick the best option.
            if len(cardsOnTable) == 0 and play == []:
                for i, predInd in enumerate(topPredsArr):
                    candidate = decodePlay(predInd)
                    if candidate == [] and len(cardsOnTable) != 0:
                        break
                    elif possiblePlaysEncoded[predInd-1] != 0:
                        play = candidate
                        break
                    
            if play != []: 
                removeCardsFromHand(play,player)
        
        # Regular card selection logic.
        else:   
            for i, predInd in enumerate(topPredsArr):
                candidate = decodePlay(predInd)
                if candidate == [] and len(cardsOnTable) != 0:
                    break
                elif possiblePlaysEncoded[predInd-1] != 0:
                    play = candidate
                    removeCardsFromHand(play,player)
                    break

        return play


# Take a the index of a play from the 1 hot encoding, and return the array of cards it represents.
def decodePlay(codeIndex):
    # Plays go in order 0=A; 1=A,A; 44=2; 45=2,2

    # The index represents a pass.
    if(codeIndex == 0):
        return []

    codeIndex = codeIndex - 1

    # Find the ace index closest to the codeIndex (Find how many cards are in the play).
    for i in range(14):
        candidateIndex = i * 4
        if codeIndex >= candidateIndex and codeIndex <= candidateIndex + 3:
            break    
    numberOfCards = (codeIndex - candidateIndex) + 1

    # Find the card value of the index.
    card = (candidateIndex / 4) + 1
    if card == 12:
        card = 2
    elif card == 13:
        card = 3
    elif card > 1 and card < 12:
        card = card + 2

    # Generate the play.
    play = []
    card = int(card)
    for i in range(numberOfCards):
        play.append(card)

    return play
    

# Check if the cardToPlay is valid given the cardsOnTable by process of elemination.
def isValidCard(cardsToPlay, cardsOnTable):

    # If the player is leading or passing, the play is valid.
    if len(cardsToPlay) == 0 or len(cardsOnTable) == 0:
        return True

    # Check if all the cardsToPlay are the same
    cardType = cardsToPlay[0]
    for card in cardsToPlay:
        if cardType != card:
            return False

    # Block 2s from being played illegally
    if 2 in cardsToPlay:
        if 2 not in cardsOnTable and 3 not in cardsOnTable and 14 not in cardsOnTable and len(cardsOnTable) < 4:
            # Make sure that one 2 is not played on tripples.
            if len(cardsToPlay) >= len(cardsOnTable) - 1:
                return True
    
    # Block 3s from being played illegally
    if 3 in cardsToPlay:
        if (3 not in cardsOnTable) and (14 not in cardsOnTable) and (len(cardsOnTable) < 4):
            return True

    # Block Jokers from being played illegally
    if 14 in cardsToPlay:
        if 14 not in cardsOnTable and len(cardsOnTable) < 4:
            return True
        
    # Check non-power cards
    if len(cardsToPlay) == len(cardsOnTable):
        # Check if the card is of higher value than the one on the table.
        if cardsToPlay[0] > cardsOnTable[0] and cardsOnTable[0] != 2 and cardsOnTable[0] != 3:
            return True
        # Check for burn legallity
        if cardsToPlay[0] == cardsOnTable[0] and cardsToPlay[0] != 2 and cardsToPlay[0] != 3 and cardsToPlay[0] != 14:
            return True
        
        # If a lower card was played check for 2, 3
        if cardsToPlay[0] < cardsOnTable[0]:
            if cardsToPlay[0] == 2 and cardsOnTable[0] != 3 and 14 not in cardsOnTable:
                return True
            elif cardsToPlay[0] == 3 and 14 not in cardsOnTable:
                return True
    
    # Check for bombs.
    if len(cardsToPlay) == 4:
        # If the cardsOnTable is a bomb, then check if the cardsToPlay is a bigger bomb.
        if len(cardsOnTable) == 4:
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


# Check to make sure that the player actually has the cards necessary in their hand.
def checkCardsInHand(cardsToPlay, cardsInHand):
    if len(cardsToPlay) == 0:
        return True
        
    cardsInHandCopy = cardsInHand.copy()
    for i, card in enumerate(cardsToPlay):
        for j, cardInHand in enumerate(cardsInHandCopy):
            if card == cardInHand:
                cardsInHandCopy.pop(j)
                break

    return len(cardsToPlay) == (len(cardsInHand) - len(cardsInHandCopy))


# Remove the cardsToPlay from the players hand.
def removeCardsFromHand(cardsToPlay, player):
    if len(cardsToPlay) == 0:
        return

    for j, cardToPlay in enumerate(cardsToPlay):
        for i, card in enumerate(player.hand):
            if card == cardToPlay:
                player.hand.pop(i)
                break 
        
