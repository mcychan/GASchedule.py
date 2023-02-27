from model.Schedule import Schedule
import functools
import random
from collections import deque
from random import randrange
from time import time


# S. Tiwari, G. Fadel, and K. Deb, 
# “AMGA2: Improving the performance of the archive-based micro-genetic algorithm for multi-objective optimization,” 
# Eng. Optim., vol. 43, no. 4, pp. 371–401, 2011.
# Copyright (c) 2020 - 2022 Miller Cy Chan


# Archive-based Micro Genetic Algorithm (AMGA2)
class Amga2:
    def initAlgorithm(self, prototype, numberOfChromosomes=100):
        # Prototype of chromosomes in population
        self._prototype = prototype

        # there should be at least 2 chromosomes in population
        if numberOfChromosomes < 2:
            numberOfChromosomes = 2

        # Population of chromosomes
        self._archivePopulation = []
        self._parentPopulation = []
        self._offspringPopulation = []
        self._combinedPopulation = []
        self._populationSize = self._archiveSize = numberOfChromosomes

        # Initializes genetic algorithm

    def __init__(self, configuration, etaCross=0.35, mutationSize=2, crossoverProbability=80,
                 mutationProbability=3):
        self.initAlgorithm(Schedule(configuration))
        self._mutationSize, self._etaCross = mutationSize, etaCross
        self._crossoverProbability, self._mutationProbability = crossoverProbability, mutationProbability

    @functools.total_ordering
    class DistanceMatrix:
        def __init__(self):
            self.index1 = -1
            self.index2 = -1
            self.distance = 0.0

        def __lt__(self, other):
            if self is None:
                return 0

            if self.distance < other.distance:
                return -1
            if self.distance > other.distance:
                return 1
            if self.index1 < other.index1:
                return -1
            if self.index1 > other.index1:
                return 1
            if self.index2 < other.index2:
                return -1
            if self.index2 > other.index2:
                return 1
            return 0

        def __eq__(self, other):
            return self.index1 == other.index1 and self.index2 == other.index2 and self.distance == other.distance

        def __ne__(self, other):
            return not self.__eq__(other)

    @property
    # Returns pointer to best chromosomes in population
    def result(self):
        return self._combinedPopulation[0]

    # initialize new population with chromosomes randomly built using prototype
    def initialize(self):
        prototype = self._prototype
        archiveSize, populationSize = self._archiveSize, self._populationSize
        archivePopulation = self._archivePopulation = []
        parentPopulation = self._parentPopulation = []
        offspringPopulation = self._offspringPopulation = []
        combinedPopulation = self._combinedPopulation = []

        for i in range(archiveSize):
            archivePopulation.append(prototype.makeNewFromPrototype())
            combinedPopulation.append(prototype.makeNewFromPrototype())

        for i in range(populationSize):
            parentPopulation.append(prototype.makeNewFromPrototype())
            offspringPopulation.append(prototype.makeNewFromPrototype())
            combinedPopulation.append(prototype.makeNewFromPrototype())

    def assignInfiniteDiversity(self, population, elite):
        for index in elite:
            population[index].diversity = float("inf")

    def assignDiversityMetric(self, population, elite):
        if len(elite) <= 2:
            self.assignInfiniteDiversity(population, elite)
            return

        distinct = self.extractDistinctIndividuals(population, elite)
        if len(distinct) <= 2:
            self.assignInfiniteDiversity(population, elite)
            return

        size = len(distinct)
        for e in distinct:
            population[e].diversity = 0.0

        val = population[distinct[size - 1]].getDifference(population[distinct[0]])
        if val == 0:
            return

        for j in range(size):
            if j == 0:
                diff = population[distinct[j + 1]].getDifference(population[distinct[j]])
                hashArray = (0.0, population[distinct[j]].fitness, population[distinct[j + 1]].fitness)
                r = diff / val
                population[distinct[j]].diversity += (r * r)
            elif j == size - 1:
                diff = population[distinct[j]].getDifference(population[distinct[j - 1]])
                l = diff / val
                population[distinct[j]].diversity += (l * l)
            else:
                diff = population[distinct[j]].getDifference(population[distinct[j - 1]])
                l = diff / val
                diff = population[distinct[j + 1]].getDifference(population[distinct[j]])
                r = diff / val
                population[distinct[j]].diversity += (l * r)

    def createOffspringPopulation(self):
        currentArchiveSize, populationSize = self._currentArchiveSize, self._populationSize
        archivePopulation, parentPopulation, offspringPopulation = self._archivePopulation, self._parentPopulation,self._offspringPopulation
        etaCross, crossoverProbability = self._etaCross, self._crossoverProbability

        for i in range(populationSize):
            r1 = -1
            while r1 < 0 or archivePopulation[r1] == archivePopulation[i]:
                r1 = randrange(currentArchiveSize)
            r2 = -1
            while r2 < 0 or archivePopulation[r2] == archivePopulation[i] or r2 == r1:
                r2 = randrange(currentArchiveSize)
            r3 = -1
            while r3 < 0 or archivePopulation[r3] == archivePopulation[i] or r3 == r1 or r3 == r2:
                r3 = randrange(currentArchiveSize)
            offspringPopulation[i] = offspringPopulation[i].crossovers(parentPopulation[i], archivePopulation[r1],
                                                                       archivePopulation[r2], archivePopulation[r3],
                                                                       etaCross, crossoverProbability)
            offspringPopulation[i].rank = parentPopulation[i].rank  # for rank based mutation

    @functools.total_ordering
    def checkDomination(self, a, b):
        if a.fitness < b.fitness:
            return -1
        if a.fitness > b.fitness:
            return 1
        return 0

    def extractDistinctIndividuals(self, population, elite):
        return sorted(set(elite), key=lambda e: population[e].fitness)

    def extractENNSPopulation(self, mixedPopulation, pool, desiredEliteSize):
        poolSize, mixedSize = len(pool), len(mixedPopulation)
        filtered = [index for index in pool if mixedPopulation[index].diversity == float("inf")]
        numInf = len(filtered)
        if desiredEliteSize <= numInf:
            return filtered[:desiredEliteSize]

        elite = deque(dict.fromkeys(pool))
        pool.clear()
        if desiredEliteSize <= numInf:
            return elite

        distance = [[0 for x in range(poolSize)] for y in range(poolSize)]
        indexArray = poolSize * [0]
        originalArray = mixedSize * [-1]

        for counter, index in enumerate(elite):
            indexArray[counter] = index
            originalArray[index] = counter

        distArray = []
        for i in range(poolSize):
            for j in range(i + 1, poolSize):
                distMatrix = Amga2.DistanceMatrix()
                distMatrix.index1 = indexArray[i]
                distMatrix.index2 = indexArray[j]
                distMatrix.distance = mixedPopulation[distMatrix.index1].getDifference(mixedPopulation[distMatrix.index2])
                distance[j][i] = distance[i][j] = distMatrix.distance
                distArray.append(distMatrix)

        distArray.sort()
        distArray_len = len(distArray)
        idx = 0
        while len(elite) > desiredEliteSize and idx < distArray_len:
            temp = distArray[idx]
            idx += 1
            index1, index2 = temp.index1, temp.index2

            while (originalArray[index1] == -1 or originalArray[index2] == -1) and idx < distArray_len:
                temp = distArray[idx]
                idx += 1
                index1, index2 = temp.index1, temp.index2

            if idx >= distArray_len:
                break

            if mixedPopulation[index1].diversity == float("inf") and mixedPopulation[index2].diversity == float("inf"):
                continue

            if mixedPopulation[index1].diversity == float("inf"):
                elite.remove(index2)
                pool.append(index2)
                originalArray[index2] = -1
            elif mixedPopulation[index2].diversity == float("inf"):
                elite.remove(index1)
                pool.append(index1)
                originalArray[index1] = -1
            else:
                dist1 = float("inf")
                for index in elite:
                    if index != index1 and index != index2:
                        if dist1 > distance[originalArray[index1]][originalArray[index]]:
                            dist1 = distance[originalArray[index1]][originalArray[index]]

                dist2 = float("inf")
                for index in elite:
                    if index != index1 and index != index2:
                        if dist2 > distance[originalArray[index2]][originalArray[index]]:
                            dist2 = distance[originalArray[index2]][originalArray[index]]

                if dist1 < dist2:
                    elite.remove(index1)
                    pool.append(index1)
                    originalArray[index1] = -1
                else:
                    elite.remove(index2)
                    pool.append(index2)
                    originalArray[index2] = -1

        while len(elite) > desiredEliteSize:
            pool.append(elite.popleft())

        return elite

    def extractBestRank(self, population, pool, elite):
        if not pool:
            return False

        checkDomination = self.checkDomination
        remains = deque()
        elite.append(pool.popleft())

        while pool:
            index1 = pool.popleft()
            flag, index2 = -1, 0
            while index2 < len(elite):
                flag = checkDomination(population[index1], population[index2])
                if flag == 1:
                    remains.append(index2)
                    del elite[index2]
                elif flag == -1:
                    break
                else:
                    index2 += 1

            if flag > -1:
                elite.append(index1)
            else:
                remains.append(index1)

        pool.clear()
        pool.extend(remains)
        return True

    def fillBestPopulation(self, mixedPopulation, mixedLength, population, populationLength):
        pool = deque(range(mixedLength))
        elite, filled = deque(), []
        rank = 1

        assignInfiniteDiversity = self.assignInfiniteDiversity
        extractBestRank, extractENNSPopulation = self.extractBestRank, self.extractENNSPopulation

        for index in pool:
            mixedPopulation[index].diversity = 0

        hasBetter = True
        while hasBetter and len(filled) < populationLength:
            hasBetter = extractBestRank(mixedPopulation, pool, elite)
            for index in elite:
                mixedPopulation[index].rank = rank

            if rank == 1:
                assignInfiniteDiversity(mixedPopulation, elite)

            rank += 1

            if len(elite) + len(filled) < populationLength:
                filled.extend(elite)
                elite.clear()
            else:
                temp = extractENNSPopulation(mixedPopulation, elite, populationLength - len(filled))
                filled.extend(temp)

        for j, index in enumerate(filled):
            population[j] = mixedPopulation[index]

    def fillDiversePopulation(self, mixedPopulation, pool, population, startLocation, desiredSize):
        self.assignDiversityMetric(mixedPopulation, pool)
        poolSize = len(pool)
        indexArray = sorted(pool, key=lambda e: mixedPopulation[e].diversity)
        for i in range(desiredSize):
            population[startLocation + i] = mixedPopulation[indexArray[poolSize - 1 - i]]

    def createParentPopulation(self):
        pool = deque(range(self._currentArchiveSize))
        elite, selectionPool = [], deque()

        rank, populationSize = 1, self._populationSize
        archivePopulation, parentPopulation = self._archivePopulation, self._parentPopulation
        extractBestRank = self.extractBestRank
        while len(selectionPool) < populationSize:
            extractBestRank(archivePopulation, pool, elite)
            for i in elite:
                archivePopulation[i].rank = rank
                selectionPool.append(i)
            rank += 1
            elite.clear()

        j = 0
        for i in selectionPool:
            parentPopulation[j] = archivePopulation[i]
            j += 1
        self.fillDiversePopulation(archivePopulation, selectionPool, parentPopulation, j, populationSize - j)

    def mutateOffspringPopulation(self):
        currentArchiveSize, populationSize = self._currentArchiveSize, self._populationSize
        mutationProbability, mutationSize = self._mutationProbability, self._mutationSize
        offspringPopulation = self._offspringPopulation
        for i in range(populationSize):
            pMut = mutationProbability + (1.0 - mutationProbability) * (
                        float(offspringPopulation[i].rank - 1) / (currentArchiveSize - 1))  # rank-based variation
            offspringPopulation[i].mutation(mutationSize, pMut)

    def updateArchivePopulation(self):
        currentArchiveSize, populationSize = self._currentArchiveSize, self._populationSize
        archivePopulation, combinedPopulation, offspringPopulation = self._archivePopulation, self._combinedPopulation, self._offspringPopulation
        if (currentArchiveSize + populationSize) <= self._archiveSize:
            for j, i in enumerate(range(populationSize), start=currentArchiveSize):
                archivePopulation[j] = offspringPopulation[i]
            self._currentArchiveSize += populationSize
        else:
            for i in range(currentArchiveSize):
                combinedPopulation[i] = archivePopulation[i]

            for i in range(populationSize):
                combinedPopulation[currentArchiveSize + i] = offspringPopulation[i]

            self.fillBestPopulation(combinedPopulation, currentArchiveSize + populationSize, archivePopulation,
                                    self._archiveSize)
            self._currentArchiveSize = self._archiveSize

        for e in archivePopulation:
            e.diversity = 0

    def finalizePopulation(self):
        currentArchiveSize, populationSize = self._currentArchiveSize, self._populationSize
        archivePopulation, combinedPopulation = self._archivePopulation, self._combinedPopulation

        elite = []
        pool = deque([i for i in range(currentArchiveSize) if archivePopulation[i].fitness >= 0])

        if pool:
            self.extractBestRank(archivePopulation, pool, elite)
            pool.clear()
            if len(elite) > populationSize:
                for index in elite:
                    archivePopulation[index].diversity = 0

                self.assignInfiniteDiversity(archivePopulation, elite)
                self.extractENNSPopulation(archivePopulation, pool, populationSize)
                elite = list(pool)
            self._currentArchiveSize = len(elite)

            for i, index in enumerate(elite):
                combinedPopulation[i] = archivePopulation[index]
        else:
            self._currentArchiveSize = 0

    def reform(self):
        random.seed(round(time() * 1000))
        if self._crossoverProbability < 95:
            self._crossoverProbability += 1.0;
        elif self._mutationProbability < 30:
            self._mutationProbability += 1.0;

    # Starts and executes algorithm
    def run(self, maxRepeat=9999, minFitness=0.999):
        self.initialize()
        self._currentArchiveSize = self._populationSize
        createParentPopulation, createOffspringPopulation = self.createParentPopulation, self.createOffspringPopulation
        mutateOffspringPopulation, updateArchivePopulation = self.mutateOffspringPopulation, self.updateArchivePopulation
        random.seed(round(time() * 1000))

        # Current generation
        currentGeneration = 0

        repeat, lastBestFit = 0, 0.0

        while 1:
            if currentGeneration > 0:
                bestFitness = self.result.fitness
                print("Fitness:", "{:f}\t".format(bestFitness), "Generation:", currentGeneration, end="\r")

                # algorithm has reached criteria?
                if bestFitness > minFitness:
                    self.finalizePopulation()
                    break

                difference = abs(bestFitness - lastBestFit)
                if difference <= 0.0000001:
                    repeat += 1
                else:
                    repeat = 0

                if repeat > (maxRepeat / 100):
                    self.reform()
                lastBestFit = bestFitness

            createParentPopulation()
            createOffspringPopulation()
            mutateOffspringPopulation()
            updateArchivePopulation()
            currentGeneration += 1

    def __str__(self):
        return "Archive-based Micro Genetic Algorithm (AMGA2)"
