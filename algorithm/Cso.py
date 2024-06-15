from .LévyFlights import LévyFlights
from .NsgaIII import NsgaIII
import math
import numpy as np
import random
from time import time


# X. -S. Yang and Suash Deb, "Cuckoo Search via Lévy flights,"
# 2009 World Congress on Nature & Biologically Inspired Computing (NaBIC), Coimbatore, India,
# 2009, pp. 210-214, doi: 10.1109/NABIC.2009.5393690.
# Copyright (c) 2023 - 2024 Miller Cy Chan


# Cuckoo Search Optimization (CSO)
class Cso(NsgaIII):
    def __init__(self, configuration, numberOfCrossoverPoints=2, mutationSize=2, crossoverProbability=80,
                 mutationProbability=3, maxIterations=5000):
        self._max_iterations = maxIterations
        super().__init__(configuration, numberOfCrossoverPoints, mutationSize, crossoverProbability,
                        mutationProbability)

        # there should be at least 5 chromosomes in population
        if self._populationSize < 5:
            self._populationSize = 5

        self._chromlen, self._pa = 0, .25

        self._lf, self._gBest = None, None
        self._current_position = [[]]


    def initialize(self, population):
        prototype = self._prototype

        populationSize = self._populationSize
        for i in range(populationSize):
            positions = []
            # add new chromosome to population
            population[i] = prototype.makeNewFromPrototype(positions)
            if i < 1:
                self._chromlen = len(positions)
                self._current_position = np.zeros((populationSize, self._chromlen), dtype=float)
                self._lf = LévyFlights(self._chromlen)


    def updateVelocities(self, population):
        current_position = np.copy(self._current_position)
        populationSize = self._populationSize
        for i in range(populationSize):
            d1, d2 = np.random.randint(0, 5, 2)
            while d1 == d2:
                d2 = np.random.randint(0, 5)
            changed = False
            for j in range(self._chromlen):
                r = np.random.rand()
                if r < self._pa:
                    changed = True
                    self._current_position[i, j] += random.random() * (current_position[d1, j] - current_position[d2, j])

            if changed:
                self._current_position[i] = self._lf.optimum(self._current_position[i], population[i])


    def reform(self):
        random.seed(round(time() * 1000))
        np.random.seed(int(time()))
        if self._crossoverProbability < 95:
            self._crossoverProbability += 1.0
        elif self._pa < .5:
            self._pa += .01


    def replacement(self, population):
        populationSize = self._populationSize
        self._gBest = self._lf.updatePositions(population, populationSize, self._current_position, self._gBest)
        self.updateVelocities(population)

        for i in range(populationSize):
            chromosome = self._prototype.makeEmptyFromPrototype()
            chromosome.updatePositions(self._current_position[i])
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

    def __str__(self):
        return "Cuckoo Search Optimization (CSO)"
