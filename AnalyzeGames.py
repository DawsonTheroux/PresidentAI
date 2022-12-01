import torch
import numpy as np
from CardInterfaces import decodePlay
from GameClass import Game
from PresidentNeuralNet import PresidentNet
def analyzePlay(play):
    #playersIn, possiblePlays, cardsInHand, cardsOnTable, cardsPlayed, playChosen = np.split(play, [6, 60, 114, 168, 222])
    playerID, playersIn, cardsInHand, cardsOnTable, cardsPlayed, playChosen = np.split(play, [1, 7, 61, 115, 169])
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
    if playChosen[playChosenIndex] == 0:
        playChosenIndex = np.argmin(playChosen)
    positions = ["Ass", "Vice Ass", "Neutral2", "Neutral1", "Vice President", "President"]
    position = -1
    if playChosen[playChosenIndex] == -10:
        position = "Auto Ass"
    elif playChosen[playChosenIndex] > 0:
        position = positions[int(playChosen[playChosenIndex] + 2)]
    else:
        position = positions[int(playChosen[playChosenIndex] + 3)]
    #position = positions[(int)(playChosen[playChosenIndex] - 1)]
    chosenPlay = decodePlay(playChosenIndex)
    outputString = ""
    outputString += f"----{playerID}:({playChosen[playChosenIndex]})-----:\n"
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
    gameMatrix = gameMatrix.reshape((-1, 224))
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


def calculateFitness(evalModel, competatorModel):
    # Calculates the fitness value of the evalModel compared to the competatorModel
    evalModelIds = [0.2, 1.2, 2.2]
    competatorModelIds = [0.1, 1.1, 2.1]
    fitness = 0
    for i in range(1000):
        if i != 0 and i % 250 == 0:
            print(f"Running Game {i}")
        if competatorModel == "random":
            game_obj = Game(3, evalModel)
        else:
            game_obj = Game(5, evalModel, competatorModel)
        resultsArr = game_obj.getResults()
        #print(f"ResultsArray[0].id: {resultsArr[0].id}")
        if resultsArr[0].id in evalModelIds:
            fitness += 1
    return fitness

def modelFitnessFromFiles(evalModelPath, competatorModelPath):
    evalModel = PresidentNet()
    competatorModel = PresidentNet()
    evalModel.load_state_dict(torch.load(evalModelPath))

    if competatorModelPath != "random":
        competatorModel.load_state_dict(torch.load(competatorModelPath))
    else:
        competatorModel = "random"
    return calculateFitness(evalModel, competatorModel)



if __name__ == "__main__":
    ''' Compare generations to random
    for i in range(15):
        print(f"Evaluating Gen {i}")
        evalModelPath = f"D:\\school\\COMP3106\\Project\\PresidentAI\\Models\\model2008\\model2008_gen{i}.pt"
        print(f"fitness {modelFitnessFromFiles(evalModelPath, 'random')}")
        print("-----")
    '''
    # Compare generations to previous
    for i in range(15):
        print(f"Evaluating Gen {i}")
        evalModelPath = f"D:\\school\\COMP3106\\Project\\PresidentAI\\Models\\model2008\\model2008_gen{i}.pt"
        competatorPath = f"D:\\school\\COMP3106\\Project\\PresidentAI\\Models\\model2008\\model2008_gen{i-1}.pt"
        if i == 0:
            print(f"fitness {modelFitnessFromFiles(evalModelPath, 'random')}")
        else:
            print(f"fitness {modelFitnessFromFiles(evalModelPath, competatorPath)}")
        print("-----")
    #analyzeOutput("testfile.csv")