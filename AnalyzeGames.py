import torch
import numpy as np
from CardInterfaces import decodePlay
from GameClass import Game
from PresidentNeuralNet import PresidentNet
import json
import time
import threading

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


def calculateFitness(evalModel, competatorModel, numberOfGames = 500):
    # Calculates the fitness value of the evalModel compared to the competatorModel
    evalModelIds = [0, 1, 2]
    competatorModelIds = [0.1, 1.1, 2.1]
    fitness = 0
    competatorFitness = 0
    numAutoAsses = 0
    evalModelPlacements = {"President": 0,
                           "VP": 0,
                           "Neutral1": 0,
                           "Neutral2": 0,
                           "Vice Ass": 0,
                           "Ass": 0}
    for i in range(numberOfGames):
        if i != 0 and i % 500 == 0:
            print(f"Running Game {i}")
        if competatorModel == "random":
            game_obj = Game(3, evalModel)
        else:
            game_obj = Game(5, evalModel, competatorModel)
        resultsArr, autoAsses = game_obj.getResults()
        numAutoAsses += len(autoAsses)

            
        #print(f"ResultsArray[0].id: {resultsArr[0].id}")
        if resultsArr[0].id in evalModelIds:
            if resultsArr[0].id in autoAsses:
                fitness -= 1
            else:
                fitness += 1
            evalModelPlacements["President"] += 1
        else:
            if resultsArr[0].id in autoAsses:
                competatorFitness -= 1
            else:
                competatorFitness += 1

        if resultsArr[1].id in evalModelIds:
            if resultsArr[1].id in autoAsses:
                fitness -= 1
            else:
                fitness += 1
            evalModelPlacements["VP"] += 1
        else:
            if resultsArr[1].id in autoAsses:
                competatorFitness -= 1
            else:
                competatorFitness += 1
        
        if resultsArr[2].id in evalModelIds:
            if resultsArr[2].id in autoAsses:
                fitness -= 1
            else:
                fitness += 1
            evalModelPlacements["Neutral1"] += 1
        else:
            if resultsArr[2].id in autoAsses:
                competatorFitness -= 1
            else:
                competatorFitness += 1

        if resultsArr[3].id in evalModelIds:
            if resultsArr[3].id in autoAsses:
                fitness -= 1
            else:
                fitness -= 1
            evalModelPlacements["Neutral2"] += 1
        else:
            if resultsArr[3].id in autoAsses:
                competatorFitness -= 1
            else:
                competatorFitness -= 1

        if resultsArr[4].id in evalModelIds:
            if resultsArr[4].id in autoAsses:
                fitness -= 1
            else:
                fitness -= 1
            evalModelPlacements["Vice Ass"] += 1
        else:
            if resultsArr[4].id in autoAsses:
                competatorFitness -= 1
            else:
                competatorFitness -= 1

        if resultsArr[5].id in evalModelIds:
            if resultsArr[5].id in autoAsses:
                fitness -= 1
            else:
                fitness -= 1
            evalModelPlacements["Ass"] += 1
        else:
            if resultsArr[5].id in autoAsses:
                competatorFitness -= 1
            else:
                competatorFitness -= 1
        
    for position in evalModelPlacements.keys():
        print(f"{position}: {evalModelPlacements[position]}")
    print(f"Auto Asses: {numAutoAsses}")

    #finalFitness = fitness - competatorFitness
    return fitness, competatorFitness

def modelFitnessFromFiles(evalModelPath, competatorModelPath, numberOfGames=500):
    evalModel = PresidentNet()
    competatorModel = PresidentNet()
    evalModel.load_state_dict(torch.load(evalModelPath))

    if competatorModelPath != "random":
        competatorModel.load_state_dict(torch.load(competatorModelPath))
    else:
        competatorModel = "random"
    return calculateFitness(evalModel, competatorModel, numberOfGames)

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

def generateOneThousandGames(threadId, model):
    dataset = None
    notSet = True

    # Generate the initial random Games.
    for i in range(1000): 
        if i % 250 == 0:
            print(f"Thread: {threadId} playing Game {i}")
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

def generateGamesWithMultiThreading(model, numWorkers, outputPath, outputToFile):

    start_time = time.time()
    threads = []
    for i in range(numWorkers):
        threads.append(generationThread({i + 1}, f"Thread-{i+1}", model))
        threads[i].start()
    
    for t in threads:
        t.join()
    
    fullDataset = None
    notSet = True

    datasetArray = []
    for t in threads:
        datasetArray.append(t.dataset)
    
    #print(datasetArray)
    fullDataset = np.vstack(datasetArray)

    '''
    for t in threads:
        if notSet:
            fullDataset = t.dataset
            notSet = False
        else:
            fullDataset = np.vstack((fullDataset, t.dataset))
    '''
    

    #print(f"FullDataset shape: {fullDataset.shape}")
    if outputToFile != False:
        fullDataset.tofile(outputPath, sep = ",")


    #print(f"datasetShape: {fullDataset.shape}")

    print("All Threads finished")
    print(f"Total Time: {time.time() - start_time}")
    return fullDataset

if __name__ == "__main__":

    outputPath = "testfile.csv"
    model = PresidentNet()
    model.load_state_dict(torch.load("Models\\autoassmodel.pt", map_location=torch.device('cpu')))
    game = Game(1, model)
    outputData1 = game.getTrainingData()
    
    game = Game(1, model)
    outputData2 = game.getTrainingData()
    outputData = np.vstack((outputData1, outputData2))
    outputData.tofile(outputPath, sep=",")
    analyzeOutput(outputPath)
    

    '''
    generateGamesWithMultiThreading("random", 10, "non", False)
    '''

    ''' Compare generations to random
    for i in range(15):
        print(f"Evaluating Gen {i}")
        evalModelPath = f"D:\\school\\COMP3106\\Project\\PresidentAI\\Models\\model2008\\model2008_gen{i}.pt"
        print(f"fitness {modelFitnessFromFiles(evalModelPath, 'random')}")
        print("-----")
    '''
    '''
    evalModelPath = f"D:\\school\\COMP3106\\Project\\PresidentAI\\Models\\model2008\\model2008_gen7.pt"
    competatorPath = f"D:\\school\\COMP3106\\Project\\PresidentAI\\Models\\model2010\\model2010_gen8.pt"
    numberOfGamesVsModel = 2500
    for i in range(10):
        fitness, competatorFitness = modelFitnessFromFiles(evalModelPath, competatorPath, numberOfGamesVsModel)
        print(f"Fitness {i}: {fitness} -- Competator Fitness: {competatorFitness}")
    '''
    '''
    numberOfGenerations = 9
    firstGenerationNumber = 8
    numberOfGamesVsRandom = 100
    numberOfGamesVsModel = 500
    modelPerformances = []
    for i in range(numberOfGenerations):
        generationPerformances = []
        modelName = i + firstGenerationNumber
        maxGeneration = 15
        if modelName > 11:
            maxGeneration = 25
        for j in range(maxGeneration):
            evalModelPath = f"D:\\school\\COMP3106\\Project\\PresidentAI\\Models\\model20{modelName}\\model20{modelName}_gen{j}.pt"
            competatorPath = f"D:\\school\\COMP3106\\Project\\PresidentAI\\Models\\model20{modelName}\\model20{modelName}_gen{j-1}.pt"
            if modelName < 10:
                evalModelPath = f"D:\\school\\COMP3106\\Project\\PresidentAI\\Models\\model200{modelName}\\model200{modelName}_gen{j}.pt"
                competatorPath = f"D:\\school\\COMP3106\\Project\\PresidentAI\\Models\\model200{modelName}\\model200{modelName}_gen{j-1}.pt"
            ####PLAY AGAINST RANDOM######
            #############################
            competatorPath = "random"
            #############################
            generationFitness, competatorFitness = modelFitnessFromFiles(evalModelPath, competatorPath, numberOfGamesVsRandom)
            generationPerformances.append(generationFitness)
            print(f"Model {modelName}, Generation: {j} - Fitness: {generationFitness} - Random Fitness: {competatorFitness}")
        print("-----")
        modelPerformances.append(generationPerformances)
    
    print(f"Model performances: {modelPerformances}")
    
    bestPerformingGenerations = []
    for i in range(len(modelPerformances)): 
        highestScore = None
        highestIndex = None
        for j in range(len(modelPerformances[i])):
            currentScore = modelPerformances[i][j]
            if highestScore == None:
                highestScore = currentScore
                highestIndex = j
            elif highestScore < currentScore:
                highestScore = currentScore
                highestIndex = j
        bestPerformingGenerations.append(highestIndex)

    
    matchUpSpread = {}
    for i in range(numberOfGenerations):
        modelName = i + firstGenerationNumber
        bestGeneration = bestPerformingGenerations[i]
        evalModelPath = f"D:\\school\\COMP3106\\Project\\PresidentAI\\Models\\model20{modelName}\\model20{modelName}_gen{bestGeneration}.pt"
        if modelName < 10:
            evalModelPath = f"D:\\school\\COMP3106\\Project\\PresidentAI\\Models\\model200{modelName}\\model200{modelName}_gen{bestGeneration}.pt"
        matchUpSpread[modelName] = {}

        for j in range(numberOfGenerations):
            if i == j:
                continue
            competatorModelName = j + firstGenerationNumber
            bestCompetatorGeneration = bestPerformingGenerations[j]
            competatorPath = f"D:\\school\\COMP3106\\Project\\PresidentAI\\Models\\model20{competatorModelName}\\model20{competatorModelName}_gen{bestCompetatorGeneration}.pt"
            if competatorModelName < 10:
                competatorPath = f"D:\\school\\COMP3106\\Project\\PresidentAI\\Models\\model200{competatorModelName}\\model200{competatorModelName}_gen{bestCompetatorGeneration}.pt"
            print(f"Running Match: Model={modelName}|Gen={bestGeneration} vs. Competator={competatorModelName}|Gen={bestCompetatorGeneration}")
            fitness, competatorFitness = modelFitnessFromFiles(evalModelPath, competatorPath, numberOfGamesVsModel)
            matchUpSpread[modelName][competatorModelName] = {}
            matchUpSpread[modelName][competatorModelName]["fitnessValue"] = fitness
            matchUpSpread[modelName][competatorModelName]["Winning?"] = fitness > competatorFitness
    
    print(f" Match up spread: {matchUpSpread}")
    with open('MatchUpSpread.txt', 'w') as convert_file:
        convert_file.write(json.dumps(matchUpSpread))
    '''


    '''
            
    evalModelPath = f"D:\\school\\COMP3106\\Project\\PresidentAI\\Models\\model2008\\model2008_gen8.pt"
    evalModelPath = f"D:\\school\\COMP3106\\Project\\PresidentAI\\Models\\model2008\\model2008_gen8.pt"
    evalModelPath =  "D:\\school\\COMP3106\\Project\\PresidentAI\\model2017_gen6.pt"
    model = PresidentNet()
    model.load_state_dict(torch.load(evalModelPath, map_location=torch.device('cpu')))
    game_obj = Game(1, model)
    filename = "testfile.csv"
    game_obj.outputLogToFile(filename)
    analyzeOutput(filename)
    '''