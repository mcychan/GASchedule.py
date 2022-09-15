from model.Schedule import Schedule
import random
from random import randrange
from time import time


# Lakshmi, R. et al. “A New Biological Operator in Genetic Algorithm for Class Scheduling Problem.” 
# International Journal of Computer Applications 60 (2012): 6-11.
# Copyright (c) 2020 - 2022 Miller Cy Chan


# Genetic algorithm
class GeneticAlgorithm:
    def initAlgorithm(self, prototype, numberOfChromosomes=100, replaceByGeneration=8, trackBest=5):
        # Number of best chromosomes currently saved in best chromosome group
        self._currentBestSize = 0
        # Prototype of chromosomes in population
        self._prototype = prototype

        # there should be at least 2 chromosomes in population
        if numberOfChromosomes < 2:
            numberOfChromosomes = 2

        # and algorithm should track at least on of best chromosomes
        if trackBest < 1:
            trackBest = 1

        # Population of chromosomes
        self._chromosomes = numberOfChromosomes * [None]
        # Inidicates whether chromosome belongs to best chromosome group
        self._bestFlags = numberOfChromosomes * [False]

        # Indices of best chromosomes
        self._bestChromosomes = trackBest * [0]
        # Number of chromosomes which are replaced in each generation by offspring
        self.set_replace_by_generation(replaceByGeneration)

    # Initializes genetic algorithm
    def __init__(self, configuration, numberOfCrossoverPoints=2, mutationSize=2, crossoverProbability=80,
                 mutationProbability=3):
        self.initAlgorithm(Schedule(configuration))
        self._mutationSize = mutationSize
        self._numberOfCrossoverPoints = numberOfCrossoverPoints
        self._crossoverProbability = crossoverProbability
        self._mutationProbability = mutationProbability

    @property
    # Returns pointer to best chromosomes in population
    def result(self):
        return self._chromosomes[self._bestChromosomes[0]]

    def set_replace_by_generation(self, value):
        numberOfChromosomes = len(self._chromosomes)
        trackBest = len(self._bestChromosomes)
        if (value > numberOfChromosomes - trackBest):
            value = numberOfChromosomes - trackBest
        self._replaceByGeneration = value

    # Tries to add chromosomes in best chromosome group
    def addToBest(self, chromosomeIndex):
        bestChromosomes = self._bestChromosomes
        length_best = len(bestChromosomes)
        bestFlags = self._bestFlags
        chromosomes = self._chromosomes

        # don't add if new chromosome hasn't fitness big enough for best chromosome group
        # or it is already in the group?
        if (self._currentBestSize == length_best and chromosomes[bestChromosomes[self._currentBestSize - 1]].fitness >=
            chromosomes[chromosomeIndex].fitness) or bestFlags[chromosomeIndex]:
            return

        # find place for new chromosome
        j = self._currentBestSize
        for i in range(j, -1, -1):
            j = i
            pos = bestChromosomes[i - 1]
            # group is not full?
            if i < length_best:
                # position of new chromosomes is found?
                if chromosomes[pos].fitness > chromosomes[chromosomeIndex].fitness:
                    break

                # move chromosomes to make room for new
                bestChromosomes[i] = pos
            else:
                # group is full remove worst chromosomes in the group
                bestFlags[pos] = False

        # store chromosome in best chromosome group
        bestChromosomes[j] = chromosomeIndex
        bestFlags[chromosomeIndex] = True

        # increase current size if it has not reached the limit yet
        if self._currentBestSize < length_best:
            self._currentBestSize += 1

    # Returns TRUE if chromosome belongs to best chromosome group
    def isInBest(self, chromosomeIndex) -> bool:
        return self._bestFlags[chromosomeIndex]

    # Clears best chromosome group
    def clearBest(self):
        self._bestFlags = len(self._bestFlags) * [False]
        self._currentBestSize = 0

    # initialize new population with chromosomes randomly built using prototype
    def initialize(self, population):
        # addToBest = self.addToBest
        prototype = self._prototype
        length_chromosomes = len(population)

        for i in range(0, length_chromosomes):
            # add new chromosome to population
            population[i] = prototype.makeNewFromPrototype()
            # addToBest(i)

    def selection(self, population):
        length_chromosomes = len(population)
        return (population[randrange(32768) % length_chromosomes],  population[randrange(32768) % length_chromosomes])

    def replacement(self, population, replaceByGeneration) -> []:
        mutationSize = self._mutationSize
        numberOfCrossoverPoints = self._numberOfCrossoverPoints
        crossoverProbability = self._crossoverProbability
        mutationProbability = self._mutationProbability
        selection = self.selection
        isInBest = self.isInBest
        length_chromosomes = len(population)
        # produce offspring
        offspring = replaceByGeneration * [None]
        for j in range(replaceByGeneration):
            # selects parent randomly
            parent = selection(population)

            offspring[j] = parent[0].crossover(parent[1], numberOfCrossoverPoints, crossoverProbability)
            offspring[j].mutation(mutationSize, mutationProbability)

            # replace chromosomes of current operation with offspring
            # select chromosome for replacement randomly
            ci = randrange(32768) % length_chromosomes
            while isInBest(ci):
                ci = randrange(32768) % length_chromosomes

            # replace chromosomes
            population[ci] = offspring[j]

            # try to add new chromosomes in best chromosome group
            self.addToBest(ci)
        return offspring

    # Starts and executes algorithm
    def run(self, maxRepeat=9999, minFitness=0.999):
        # clear best chromosome group from previous execution
        self.clearBest()
        length_chromosomes = len(self._chromosomes)

        self.initialize(self._chromosomes)
        random.seed(round(time() * 1000))

        # Current generation
        currentGeneration = 0

        repeat = 0
        lastBestFit = 0.0

        while 1:
            best = self.result
            print("Fitness:", "{:f}\t".format(best.fitness), "Generation:", currentGeneration, end="\r")

            # algorithm has reached criteria?
            if best.fitness > minFitness:
                break

            difference = abs(best.fitness - lastBestFit)
            if difference <= 0.0000001:
                repeat += 1
            else:
                repeat = 0

            if repeat > (maxRepeat / 100):
                random.seed(round(time() * 1000))
                self.set_replace_by_generation(self._replaceByGeneration * 3)
                self._crossoverProbability += 1

            self.replacement(self._chromosomes, self._replaceByGeneration)

            lastBestFit = best.fitness
            currentGeneration += 1

    def __str__(self):
        return "Genetic Algorithm"
