from .NsgaII import NsgaII
import numpy as np
from random import random, randrange
from time import time

# Zhang, G.X., Rong, H.N., Real-observation quantum-inspired evolutionary algorithm
# for a class of numerical optimization problems. In: Lecture Notes
# in Computer Science, vol. 4490, pp. 989–996 (2007).
# Copyright (c) 2023 Miller Cy Chan


# Real observation QIEA (rQIEA)
class Rqiea(NsgaII):
    def __init__(self, configuration, numberOfCrossoverPoints=2, mutationSize=2, crossoverProbability=80,
                 mutationProbability=3, maxIterations=5000):
        self._max_iterations = maxIterations
        super().__init__(configuration, numberOfCrossoverPoints, mutationSize, crossoverProbability,
                        mutationProbability)
                        
        self._currentGeneration, self._max_iterations = 0, 5000
	
        # quantum population
        self._Q = []
    
        # observed classical population
        self._P = []

        self._bounds = [[]]
        self._chromlen, self._updated = 0, 0

        self._bestval = None
        self._best = []
        self._bestq = [[]]



    def initialize(self, population):
        prototype = self._prototype
        self._bestval = None
		
        bounds = []
        populationSize = len(population)
        for i in range(populationSize):	
            if i < 1:			
                # initialize new population with chromosomes randomly built using prototype
                population[i] = prototype.makeEmptyFromPrototype(bounds)
				
                self._chromlen = size = len(bounds)
                self._Q = np.zeros(populationSize * size * 2, dtype=float)
                self._P = np.zeros(populationSize * size, dtype=float)
                self._bounds = np.zeros((size, 2), dtype=float)
                self._best = np.zeros(size, dtype=float)
                self._bestq = np.zeros((size, 2), dtype=float)
            else:
                population[i] = prototype.makeEmptyFromPrototype()
			
            for j in range(self._chromlen):
                qij = i * 2 * self._chromlen + 2 * j
                alpha = 2 * random() - 1
                beta = np.sqrt(1 - alpha ** 2) * (-1 if (randrange(32768) % 2 != 0) else 1)
                self._Q[qij] = alpha
                self._Q[qij + 1] = beta

		
        for i in range(len(bounds)):
            self._bounds[i][1] = bounds[i]


    def observe(self):
        self._updated = 0;
        for i in range(self._populationSize):
            for j in range(self._chromlen):
                pij = i * self._chromlen + j
                qij = 2 * pij
				
                if random() <= .5:
                    self._P[pij] = self._Q[qij] ** 2
                else:
                    self._P[pij] = self._Q[qij + 1] ** 2
				
                self._P[pij] *= self._bounds[j][1] - self._bounds[j][0]
                self._P[pij] += self._bounds[j][0]
			
            start = i * self._chromlen
            positions = self._P[start: start + self._chromlen + 1]
            chromosome = self._prototype.makeEmptyFromPrototype()
            chromosome.updatePositions(positions)
            if (randrange(100) <= self._mutationProbability and i > self._mutationProbability) \
                    or chromosome.fitness > self._chromosomes[i].fitness:
                self._chromosomes[i] = chromosome
                self._updated += 1
            else:
                self._chromosomes[i].extractPositions(positions)
                self._P[start: start + self._chromlen + 1] = positions

	
    def storebest(self):
        i_best = 0
        for i in range(1, self._populationSize):
            if self._chromosomes[i].dominates(self._chromosomes[i_best]):
                i_best = i
		
        if self._bestval is None or self._chromosomes[i_best].dominates(self._bestval):
            self._bestval = self._chromosomes[i_best]
            self._best[: self._chromlen] = self._P[i_best * self._chromlen: i_best * self._chromlen + self._chromlen]
			
            j, start = 0, i_best * self._chromlen * 2
            for i in range(start, start + self._chromlen * 2, 2):
                self._bestq[j][0] = self._Q[i]
                self._bestq[j][1] = self._Q[i + 1]
                j += 1

	
    def evaluate(self):
        # not implemented			
        pass
	
    @staticmethod
    def sign(x):
        if x > 0:
            return 1
        if x < 0:
            return -1
        return 0
	
	
    def lut(self, alpha, beta, alphabest, betabest):
        M_PI_2, eps = np.pi / 2, 1e-5
        xi, xi_b = np.arctan(beta / alpha), np.arctan(betabest / alphabest)
        # (xi_b or xi = 0) || (xi_b or xi = pi/2) || (xi_b or xi = -pi/2)
        if np.abs(xi_b) < eps or np.abs(xi) < eps\
                or np.abs(xi_b - M_PI_2) < eps or np.abs(xi_b - M_PI_2) < eps\
                or np.abs(xi_b + M_PI_2) < eps or np.abs(xi_b + M_PI_2) < eps:
            return -1 if (randrange(32768) % 2 != 0) else 1

        if xi_b > 0 and xi > 0:
            return 1 if xi_b >= xi else -1

        if xi_b > 0 and xi < 0:
            return self.sign(alpha * alphabest)

        if xi_b < 0 and xi > 0:
            return -self.sign(alpha * alphabest)

        if xi_b < 0 and xi < 0:
            return 1 if xi_b >= xi else -1

        return self.sign(xi_b)

	
    def update(self):
        for i in range(self._populationSize):
            for j in range(self._chromlen):
                qij = 2 * (i * self._chromlen + j)
                qprim = np.zeros(2, dtype=float)

                k = np.pi / (100 + self._currentGeneration % 100)
                theta = k * self.lut(self._Q[qij], self._Q[qij + 1], self._bestq[j][0], self._bestq[j][1])

                qprim[0] = self._Q[qij] * np.cos(theta) + self._Q[qij + 1] * (-np.sin(theta))
                qprim[1] = self._Q[qij] * np.sin(theta) + self._Q[qij + 1] * np.cos(theta)

                self._Q[qij] = qprim[0]
                self._Q[qij + 1] = qprim[1]

	
    def recombine(self):
        i, j = randrange(self._populationSize), randrange(self._populationSize)
        while i == j:
            j = randrange(self._populationSize)

        h1 = randrange(self._chromlen)
        h2 = randrange(self._chromlen - h1) + h1

        q1, q2 = i * self._chromlen * 2, j * self._chromlen * 2

        buf = self._Q[q1: q1 + 2 * self._chromlen + 1]

        self._Q[q1 + h1 * 2: q1 + h1 * 2 + (h2 - h1) * 2 + 1] = self._Q[q2 + h1: q2 + h1 + (h2 - h1) * 2 + 1]
        self._Q[q1 + h1 * 2: q1 + h1 * 2 + (h2 - h1) * 2 + 1] = buf[h1: h1 + (h2 - h1) * 2 + 1]

        for k in range(h1, h2):
            self._Q[q1 + k * 2], self._Q[q2 + k * 2] = self._Q[q2 + k * 2], self._Q[q1 + k * 2]
	
    @property
    # Returns pointer to best chromosomes in population
    def result(self):
        return self._bestval
	
    # Starts and executes algorithm
    def run(self, maxRepeat=9999, minFitness=0.999):
        mutationSize = self._mutationSize
        mutationProbability = self._mutationProbability
        nonDominatedSorting = self.nonDominatedSorting
        selection = self.selection
        populationSize = self._populationSize
        population = populationSize * [None]

        self.initialize(population)
        self._chromosomes = population
        np.random.seed(int(time()))

        # Current generation
        currentGeneration = self._currentGeneration
        self.observe()
        self.evaluate()
        self.storebest()

        bestNotEnhance, lastBestFit = 0, 0.0

        while currentGeneration < self._max_iterations:
            if currentGeneration > 0:
                bestFitness = self.result.fitness
                print("Fitness:", "{:f}\t".format(bestFitness), "Generation:", currentGeneration, end="\r")

                # algorithm has reached criteria?
                if bestFitness > minFitness:
                    break

                difference = abs(bestFitness - lastBestFit)
                if difference <= 0.0000001:
                    bestNotEnhance += 1
                else:
                    bestNotEnhance = 0

                self._repeatRatio = bestNotEnhance * 100 / maxRepeat
                if bestNotEnhance > (maxRepeat / 100):
                    self.reform()

            # crossover
            offspring = self.replacement(population)

            # mutation
            for child in offspring:
                child.mutation(mutationSize, mutationProbability)

            totalChromosome = population + offspring

            # non-dominated sorting
            front = nonDominatedSorting(totalChromosome)
            if len(front) == 0:
                break

            # selection
            population = selection(front, totalChromosome)
            self._populationSize = populationSize = len(population)

            # comparison
            if currentGeneration == 0:
                self._chromosomes = population
            else:
                totalChromosome = population + self._chromosomes
                newBestFront = nonDominatedSorting(totalChromosome)
                if len(newBestFront) == 0:
                    break
                self._chromosomes = selection(newBestFront, totalChromosome)
                lastBestFit = bestFitness
				
                for i in range(populationSize):
                    positions = np.zeros(self._chromlen, dtype=float)
                    start = i * self._chromlen
                    self._chromosomes[i].extractPositions(positions)
                    self._P[start: start + self._chromlen] = positions
			
            self.observe()
            self.evaluate()
            self.storebest()
            self.update()
            self.recombine()

            currentGeneration += 1
            self._currentGeneration = currentGeneration

	
    def __str__(self):
        return "Real observation QIEA (rQIEA)"
