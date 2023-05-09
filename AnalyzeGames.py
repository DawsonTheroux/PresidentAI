import torch
import numpy as np
from CardInterfaces import decodePlay
from GameClass import Game
from PresidentNeuralNet import PresidentNet
import json
import time
import threading

def analyzePlay(play):

    # split a 1-hot encoding into all its individual pieces.
    playerID, oponentNumberOfcards, cardsInHand, cardsOnTable, cardsPlayed, playChosen = np.split(play, [1, 46, 100, 154, 208])

    # Decode the cards played so far, the cardsInHand at this play
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
 
    # Decode the cards on table.
    cardsOnTableDecoded = []
    for i in range(len(cardsOnTable)):
        if cardsOnTable[i] == 1:
            cardsOnTableDecoded = decodePlay(i + 1)
            break
        
    # Decode the play selected by the player.
    playChosenIndex = np.argmax(playChosen)
    if playChosen[playChosenIndex] == 0:
        playChosenIndex = np.argmin(playChosen)

    positions = ["Ass", "Vice Ass", "Neutral2", "Neutral1", "Vice President", "President"]

    chosenPlay = decodePlay(playChosenIndex)

    # Generate an output string for the play.
    outputString = ""
    outputString += f"----{playerID}:({playChosen[playChosenIndex]})-----:\n"
    outputString += f"Discarded Cards: {allCardsPlayed}\n"
    outputString += f"Other Player Cards: {oponentNumberOfcards}\n"
    outputString += f"Cards On Table: {cardsOnTableDecoded}\n"
    outputString += f"Cards in hand: {cardsInHandDecoded}\n"
    outputString += f"Play Chosen: {chosenPlay}\n"
    return outputString


# Takes in a game file (1-hot matrix of all plays), and outputs a plaintext version of the game file.
def analyzeOutput(filename, outputFilename = None):
    # Load the gameMatrix from the file.
    gameMatrix = np.loadtxt(filename, delimiter = ",")
    shapeTouple = gameMatrix.shape
    gameMatrix = gameMatrix.reshape((-1, 263))

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


# Calculate the fitness of a model by running a certain number of games.
# Autoass = - 2,
# Possition in upper half: + 1
# Possition in lower half: - 1
def calculateFitness(evalModel, competatorModel, numberOfGames = 500):
    evalModelIds = [0, 1, 2]               # Ids of the model to evaluate
    competatorModelIds = [0.1, 1.1, 2.1]   # IDs of the competator model

    fitness = 0
    competatorFitness = 0
    numAutoAsses = 0
    evalModelPlacements = {"President": 0,
                           "VP": 0,
                           "Neutral1": 0,
                           "Neutral2": 0,
                           "Vice Ass": 0,
                           "Ass": 0}

    # Run numberOfGames games to calculate fitness.
    for i in range(numberOfGames):
        if i != 0 and i % 500 == 0:
            print(f"Running Game {i}")
        if competatorModel == "random":
            game_obj = Game(3, evalModel)
        else:
            game_obj = Game(5, evalModel, competatorModel)
        resultsArr, autoAsses = game_obj.getResults()
        numAutoAsses += len(autoAsses)
    
        if resultsArr[0].id in evalModelIds:
            if resultsArr[0].id in autoAsses:
                fitness -= 2
            else:
                fitness += 1
            evalModelPlacements["President"] += 1
        else:
            if resultsArr[0].id in autoAsses:
                competatorFitness -= 2
            else:
                competatorFitness += 1

        if resultsArr[1].id in evalModelIds:
            if resultsArr[1].id in autoAsses:
                fitness -= 2
            else:
                fitness += 1
            evalModelPlacements["VP"] += 1
        else:
            if resultsArr[1].id in autoAsses:
                competatorFitness -= 2
            else:
                competatorFitness += 1
        
        if resultsArr[2].id in evalModelIds:
            if resultsArr[2].id in autoAsses:
                fitness -= 2
            else:
                fitness += 1
            evalModelPlacements["Neutral1"] += 1
        else:
            if resultsArr[2].id in autoAsses:
                competatorFitness -= 2
            else:
                competatorFitness += 1

        if resultsArr[3].id in evalModelIds:
            if resultsArr[3].id in autoAsses:
                fitness -= 2
            else:
                fitness -= 1
            evalModelPlacements["Neutral2"] += 1
        else:
            if resultsArr[3].id in autoAsses:
                competatorFitness -= 2
            else:
                competatorFitness -= 1

        if resultsArr[4].id in evalModelIds:
            if resultsArr[4].id in autoAsses:
                fitness -= 2
            else:
                fitness -= 1
            evalModelPlacements["Vice Ass"] += 1
        else:
            if resultsArr[4].id in autoAsses:
                competatorFitness -= 2
            else:
                competatorFitness -= 1

        if resultsArr[5].id in evalModelIds:
            if resultsArr[5].id in autoAsses:
                fitness -= 2
            else:
                fitness -= 1
            evalModelPlacements["Ass"] += 1
        else:
            if resultsArr[5].id in autoAsses:
                competatorFitness -= 2
            else:
                competatorFitness -= 1
        
    # Print the result of the evaluation process. (Useful when training)
    for position in evalModelPlacements.keys():
        print(f"{position}: {evalModelPlacements[position]}")
    print(f"Auto Asses: {numAutoAsses}")

    return fitness, competatorFitness

# Read in two models from weight files and then generate their fitness values (Useful after training to determine better model).
def modelFitnessFromFiles(evalModelPath, competatorModelPath, numberOfGames=500 ):
    evalModel = PresidentNet()
    competatorModel = PresidentNet()
    evalModel.load_state_dict(torch.load(evalModelPath, map_location=torch.device('cpu')))
    if competatorModelPath != "random":
        competatorModel.load_state_dict(torch.load(competatorModelPath, map_location=torch.device('cpu')))
    else:
        competatorModel = "random"
    return calculateFitness(evalModel, competatorModel, numberOfGames)


# Generate a thread that runs one thousand games. (Used for training data.)
class generationThread (threading.Thread):
    def __init__(self, threadID, name, model):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.model = model
        self.dataset = None
    def run(self):
        print(f"Starting  {self.name}")
        self.dataset = generateOneThousandGames(self.threadID, self.model)
        print(f"Exiting {self.name}")


# Run one thousand games. (Used for training Data).
def generateOneThousandGames(threadId, model):
    dataset = None
    notSet = True

    for i in range(1000): 
        if i % 250 == 0:
            print(f"Thread: {threadId} playing Game {i}")

        # Generate using the RandomCardInterface.
        if model == "random":
            game_obj = Game()
        else:
            game_obj = Game(1, model)
        if notSet:
            notSet = False
            dataset = game_obj.getTrainingData()
        else:
            dataset = np.vstack((dataset, game_obj.getTrainingData()))
    return dataset


# Creates numWorkers number of threads to generate training data faster.
def generateGamesWithMultiThreading(model, numWorkers, outputPath, outputToFile):
    start_time = time.time()
    threads = []

    # Generate the threads.
    for i in range(numWorkers):
        threads.append(generationThread({i + 1}, f"Thread-{i+1}", model))
        threads[i].start() 
    
    # Wait for threads to finish
    for t in threads:
        t.join()
    
    fullDataset = None
    notSet = True

    datasetArray = []
    for t in threads:
        datasetArray.append(t.dataset)
    
    fullDataset = np.vstack(datasetArray)

    if outputToFile != False:
        fullDataset.tofile(outputPath, sep = ",")

    print("All Threads finished")
    print(f"Total Time: {time.time() - start_time}")
    return fullDataset


# Plays games until there is an autoass.
# This is to analyze model behaviour
def generateAutoassGame():
    while(True):
        game_obj = Game(0)
        results, autoAss = game_obj.getResults()
        if len(autoAss) > 0:
            break

    game_obj.getTrainingData()
    print(f"Standings:")
    for i, player in enumerate(results):
        print(player.id)

    print("AutoAsses:")
    for i, player in enumerate(autoAss):
        print(player)

if __name__ == "__main__":
    generateAutoassGame()
    
    

