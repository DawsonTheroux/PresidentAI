import torch
import numpy as np
from CardInterfaces import decodePlay

def analyzePlay(play):
    #playersIn, possiblePlays, cardsInHand, cardsOnTable, cardsPlayed, playChosen = np.split(play, [6, 60, 114, 168, 222])
    playersIn, cardsInHand, cardsOnTable, cardsPlayed, playChosen = np.split(play, [6, 60, 114, 168])
    #print(f"Players in ({playersIn.shape}): {playersIn}")
    #print(f"possiblePlays({possiblePlays.shape}): {possiblePlays}")
    #print(f"cardsOnTable({cardsOnTable.shape}): {cardsOnTable}")
    #print(f"cardsPlayed({cardsPlayed.shape}): {cardsPlayed}")
    #print(f"PlayChosen({playChosen.shape}): {playChosen}")


    allCardsPlayed = []
    cardsInHandDecoded = []
    cardAtIndex = 0
    for i in range(len(cardsPlayed)):
        if i % 4 == 0:
            cardAtIndex += 1
        if cardsPlayed[i] == 1:
            allCardsPlayed.append(cardAtIndex)
        if cardsInHand[i] == 1:
            cardsInHandDecoded.append(cardAtIndex)


    playerCount = 0
    for i in range(len(playersIn)):
        if playersIn[i] == 1:
            playerCount += 1
    
    '''
    possiblePlaysDecoded = []
    for i in range(len(possiblePlays)):
        if possiblePlays[i] == 1:
            play = decodePlay(i + 1)
            possiblePlaysDecoded.append(play)
    '''
    
    cardsOnTableDecoded = []
    for i in range(len(cardsOnTable)):
        if cardsOnTable[i] == 1:
            cardsOnTableDecoded = decodePlay(i + 1)
            break
        

    playChosenIndex = np.argmax(playChosen)
    positions = ["Ass", "Vice Ass", "Neutral2", "Neutral1", "Vice President", "President"]
    position = positions[(int)(playChosen[playChosenIndex] - 1)]
    chosenPlay = decodePlay(playChosenIndex)
    outputString = ""
    outputString += f"----{position}-----:\n"
    outputString += f"Discarded Cards: {allCardsPlayed}\n"
    outputString += f"Player Count: {playerCount}\n"
    outputString += f"Cards On Table: {cardsOnTableDecoded}\n"
    outputString += f"Cards in hand: {cardsInHandDecoded}\n"
    #outputString += f"PossiblePlays {possiblePlaysDecoded}\n"
    outputString += f"Play Chosen: {chosenPlay}\n"
    return outputString


def analyzeOutput(filename, outputFilename = None):
    gameMatrix = np.loadtxt(filename, delimiter = ",")
    shapeTouple = gameMatrix.shape
    #print(f"shapeTupple: {shapeTouple[0]}")
    #n = shapeTouple[0] / (55 + 168)
    #gameMatrix = gameMatrix.reshape((-1, 277))
    gameMatrix = gameMatrix.reshape((-1, 223))
    #print(gameMatrix.shape)
    #print(gameMatrix)
    outputString = ""
    for i in range(len(gameMatrix)):
        playString = analyzePlay(gameMatrix[i])
        if outputFilename == None:
            print(playString)
        else:
            outputString += playString
    if outputFilename != None:
        f = open(outputFilename, "w")
        f.write(outputString)
        f.close()
        #input()
    #print(f"gameMatrix.shape: {gameMatrix.shape}")

if __name__ == "__main__":
    analyzeOutput("testfile.csv")