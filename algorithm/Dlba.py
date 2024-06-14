from .LévyFlights import LévyFlights
from .NsgaIII import NsgaIII
import math
import numpy as np
import random
from time import time


# Xie, Jian & Chen, Huan. (2013).
# A Novel Bat Algorithm Based on Differential Operator and Lévy Flights Trajectory.
# Computational intelligence and neuroscience. 2013. 453812. 10.1155/2013/453812. 
# Copyright (c) 2024 Miller Cy Chan


# Bat algorithm with differential operator and Levy flights trajectory (DLBA)
class Dlba(NsgaIII):
    def __init__(self, configuration, numberOfCrossoverPoints=2, mutationSize=2, crossoverProbability=80,
                 mutationProbability=3, maxIterations=5000):
        self._currentGeneration, self._max_iterations = 0, maxIterations
        super().__init__(configuration, numberOfCrossoverPoints, mutationSize, crossoverProbability,
                        mutationProbability)

        self._chromlen, self._minValue, self._alpha, self._pa = 0, 0, .9, .25
        self._frequency, self._loudness, self._rate = None, None, None

        self._gBest = None
        self._position, self._velocity = [[]], [[]]
        self._maxValues, self._lf = None, None


    def initialize(self, population):
        prototype = self._prototype

        self._maxValues = []
        prototype.makeEmptyFromPrototype(self._maxValues)

        populationSize = self._populationSize
        for i in range(populationSize):
            positions = []
            # add new chromosome to population
            population[i] = prototype.makeNewFromPrototype(positions)
            if i < 1:
                self._chromlen = len(positions)
                self._frequency = np.zeros(self._chromlen, dtype=float)
                self._rate = np.zeros(populationSize, dtype=float)
                self._loudness = np.zeros(populationSize, dtype=float)
                self._position = np.zeros((populationSize, self._chromlen), dtype=float)
                self._velocity = np.zeros((populationSize, self._chromlen), dtype=float)
                self._lf = LévyFlights(self._chromlen)

            self._rate[i] = random.random()
            self._loudness[i] = random.random() + 1


    def updateVelocities(self, population):
        mean = np.mean(self._loudness)
        currentGeneration, prototype = self._currentGeneration, self._prototype
        frequency, gBest = self._frequency, self._gBest
        maxValues, minValue = self._maxValues, self._minValue
        position, rate = self._position, self._rate
        loudness, velocity = self._loudness, self._velocity

        globalBest = prototype.makeEmptyFromPrototype()
        globalBest.updatePositions(self._gBest)
        localBest = prototype.makeNewFromPrototype()

        populationSize = self._populationSize
        for i in range(populationSize):
            beta, rand = np.random.uniform(size=2)
            n = np.random.uniform(low=-1, high=1)

            for j in range(self._chromlen):
                frequency[j] = ((maxValues[j] - minValue) * currentGeneration / n + minValue) * beta
                velocity[i, j] += (position[i, j] - gBest[j]) * frequency[j]

                if rand > rate[i]:
                    position[i, j] += velocity[i, j]
                    if position[i, j] > maxValues[j]:
                        position[i, j], velocity[i, j] = maxValues[j], minValue
                    elif position[i, j] < minValue:
                        position[i, j] = velocity[i, j] = minValue

                localTemp = prototype.makeEmptyFromPrototype()
                localTemp.updatePositions(position[i])
                if localTemp.dominates(localBest):
                    localBest = localTemp

        for i in range(populationSize):
            positionTemp = np.copy(position)
            if random.random() < loudness[i]:
                n = np.random.uniform(low=-1, high=1)
                for j in range(self._chromlen):
                    positionTemp[i, j] = gBest[j] + n * mean
                    if positionTemp[i, j] > maxValues[j]:
                        positionTemp[i, j], velocity[i, j] = maxValues[j], minValue
                    elif positionTemp[i, j] < minValue:
                        positionTemp[i, j] = velocity[i, j] = minValue

                if globalBest.dominates(localBest):
                    position[i] = positionTemp[i]
                    rate[i] *= (_currentGeneration / n) ** 3
                    loudness[i] *= alpha

            position[i] = self._lf.optimum(position[i], population[i])


    def reform(self):
        random.seed(round(time() * 1000))
        np.random.seed(int(time()))
        if self._crossoverProbability < 95:
            self._crossoverProbability += 1.0
        elif self._pa < .5:
            self._pa += .01


    def replacement(self, population):
        populationSize = self._populationSize
        self._gBest = self._lf.updateVelocities(population, populationSize, self._position, self._gBest)
        self.updateVelocities(population)

        for i in range(populationSize):
            chromosome = self._prototype.makeEmptyFromPrototype()
            chromosome.updatePositions(self._position[i])
            population[i] = chromosome

        return super().replacement(population)


    # Starts and executes algorithm
    def run(self, maxRepeat=9999, minFitness=0.999):
        mutationSize, mutationProbability = self._mutationSize, self._mutationProbability
        populationSize = self._populationSize
        population = populationSize * [None]

        self.initialize(population)
        random.seed(round(time() * 1000))
        np.random.seed(int(time()))
        pop = [population, None]

        # Current generation
        currentGeneration = 0
        bestNotEnhance, lastBestFit = 0, 0.0

        cur, next = 0, 1
        while currentGeneration < self._max_iterations:
            if currentGeneration > 0:
                best = self.result
                print("Fitness:", "{:f}\t".format(best.fitness), "Generation:", currentGeneration, end="\r")

                # algorithm has reached criteria?
                if best.fitness > minFitness:
                    break

                difference = abs(best.fitness - lastBestFit)
                if difference <= 0.0000001:
                    bestNotEnhance += 1
                else:
                    lastBestFit = best.fitness
                    bestNotEnhance = 0

                if bestNotEnhance > (maxRepeat / 50):
                    self.reform()

            # crossover
            offspring = self.crossing(pop[cur])

            # mutation
            [i for i in map(self.mutation, offspring)]

            pop[cur].extend(offspring)

            # replacement
            pop[next] = self.replacement(pop[cur])
            self._best = pop[next][0] if pop[next][0].dominates(pop[cur][0]) else pop[cur][0]

            cur, next = next, cur
            currentGeneration += 1
            self._currentGeneration = currentGeneration

    def __str__(self):
        return "Bat algorithm with differential operator and Levy flights trajectory (DLBA)"

