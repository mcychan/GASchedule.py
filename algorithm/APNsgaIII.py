from .NsgaIII import NsgaIII
import numpy as np
import random
from time import time


# Wu, M.; Yang, D.; Zhou, B.; Yang, Z.; Liu, T.; Li, L.; Wang, Z.; Hu,
# K. Adaptive Population NSGA-III with Dual Control Strategy for Flexible Job
# Shop Scheduling Problem with the Consideration of Energy Consumption and Weight. Machines 2021, 9, 344.
# https://doi.org/10.3390/machines9120344
# Copyright (c) 2023 Miller Cy Chan


# Adaptive Population NSGA-III with Dual Control Strategy (APNsgaIII)
class APNsgaIII(NsgaIII):
    def __init__(self, configuration, numberOfCrossoverPoints=2, mutationSize=2, crossoverProbability=80,
                 mutationProbability=3, maxIterations=5000):
        self._max_iterations = maxIterations
        self._worst = None
        super().__init__(configuration, numberOfCrossoverPoints, mutationSize, crossoverProbability,
                        mutationProbability)


    def ex(self, chromosome):
        numerator, denominator = 0.0, 0.0
        for f, obj in enumerate(chromosome.objectives):
            numerator += obj - self._best.objectives[f]
            denominator += self._worst.objectives[f] - self._best.objectives[f]

        return (numerator + 1) / (denominator + 1)


    def popDec(self, population):
        N = len(population)
        if N <= self._populationSize:
            return

        rank = int(0.3 * self._populationSize)

        i = 0
        while i < N:
            exValue = self.ex(population[i])

            if exValue > 0.5 and i > rank:
                del population[i]
                N -= 1
                if N <= self._populationSize:
                    break
            i += 1


    def dualCtrlStrategy(self, population, bestNotEnhance, nMax):
        N = len(population)
        nTmp = N
        for i in range(nTmp):
            chromosome = population[i]
            tumor = chromosome.clone()
            tumor.mutation(self._mutationSize, self._mutationProbability)

            self._worst = population[-1]
            if tumor.dominates(chromosome):
                population[i] = tumor
                if tumor.dominates(self._best):
                    self._best = tumor
            else:
                if bestNotEnhance >= 15 and N < nMax:
                    N += 1
                    if self._worst.dominates(tumor):
                        population.append(tumor)
                        self._worst = tumor
                    else:
                        population.insert(-1, tumor)

        self.popDec(population)


    def replacement(self, population):
        result = super().replacement(population)
        result.sort(key = lambda chromosome: chromosome.fitness, reverse=True)
        return result


    # Starts and executes algorithm
    def run(self, maxRepeat=9999, minFitness=0.999):
        mutationSize, mutationProbability = self._mutationSize, self._mutationProbability
        populationSize = self._populationSize
        nMax = int(1.5 * populationSize)

        population = self.initialize()
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
                if bestNotEnhance < 15:
                    print("Fitness:", "{:f}\t".format(best.fitness), "Generation:", currentGeneration, end="    \r")
                else:
                    print("Fitness:", "{:f}\t".format(best.fitness), "Generation:", currentGeneration, end=" ...\r")

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
            for child in offspring:
                child.mutation(mutationSize, mutationProbability)

            pop[cur].extend(offspring)

            # replacement
            pop[next] = self.replacement(pop[cur])
            self._best = pop[next][0] if pop[next][0].dominates(pop[cur][0]) else pop[cur][0]

            self.dualCtrlStrategy(pop[next], bestNotEnhance, nMax)

            cur, next = next, cur
            currentGeneration += 1

    def __str__(self):
        return "Adaptive Population NSGA-III with Dual Control Strategy (APNsgaIII)"
