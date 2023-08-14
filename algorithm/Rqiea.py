from .NsgaIII import NsgaIII
import math
import numpy as np
import random
from time import time


# Zhang, G.X., Rong, H.N., Real-observation quantum-inspired evolutionary algorithm
# for a class of numerical optimization problems. In: Lecture Notes
# in Computer Science, vol. 4490, pp. 989–996 (2007).
# Copyright (c) 2023 Miller Cy Chan


# Real observation QIEA (rQIEA)
class Rqiea(NsgaIII):
    def __init__(self, configuration, numberOfCrossoverPoints=2, mutationSize=2, crossoverProbability=80,
                 mutationProbability=3, maxIterations=5000):
        self._max_iterations = maxIterations
        self._maxRepeat = min(15, self._max_iterations // 2)
        super().__init__(configuration, numberOfCrossoverPoints, mutationSize, crossoverProbability,
                        mutationProbability)

        self._currentGeneration = 0

        # quantum population
        self._Q = []
    
        # observed classical population
        self._P = []

        self._bounds = [[]]
        self._chromlen, self._catastrophe, self._bestNotEnhance = 0, mutationProbability, 0

        self._bestval = []
        self._bestq = [[]]



    def initialize(self, population):
        prototype = self._prototype

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
                self._bestval = np.zeros(size, dtype=float)
                self._bestq = np.zeros((size, 2), dtype=float)
            else:
                population[i] = prototype.makeEmptyFromPrototype()

            for j in range(self._chromlen):
                qij = i * 2 * self._chromlen + 2 * j
                alpha = 2 * random.random() - 1
                beta = math.sqrt(1 - alpha ** 2) * (-1 if (random.randrange(32768) % 2 != 0) else 1)
                self._Q[qij] = alpha
                self._Q[qij + 1] = beta


        for i in range(len(bounds)):
            self._bounds[i][1] = bounds[i]


    def observe(self, population):
        for i in range(self._populationSize):
            for j in range(self._chromlen):
                pij = i * self._chromlen + j
                qij = 2 * pij

                if random.random() <= .5:
                    self._P[pij] = self._Q[qij] ** 2
                else:
                    self._P[pij] = self._Q[qij + 1] ** 2

                self._P[pij] *= self._bounds[j][1] - self._bounds[j][0]
                self._P[pij] += self._bounds[j][0]

            start = i * self._chromlen
            positions = self._P[start: start + self._chromlen + 1]
            if population[i].fitness <= 0 or random.randrange(100) <= self._catastrophe:
                chromosome = self._prototype.makeEmptyFromPrototype()
                chromosome.updatePositions(positions)
                population[i] = chromosome
            else:
                population[i].extractPositions(positions)
                self._P[start: start + self._chromlen + 1] = positions


    def storebest(self, population):
        i_best = 0
        for i in range(1, self._populationSize):
            if population[i].dominates(population[i_best]):
                i_best = i

        if self._best is None or i_best > 0:
            self._best = population[i_best]
            self._bestval[: self._chromlen] = self._P[i_best * self._chromlen: i_best * self._chromlen + self._chromlen]

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

    @staticmethod
    def lut(alpha, beta, alphabest, betabest):
        M_PI_2, eps = math.pi / 2, 1e-5
        xi, xi_b = math.atan(beta / (alpha + eps)), math.atan(betabest / (alphabest + eps))
        # (xi_b or xi = 0) || (xi_b or xi = pi/2) || (xi_b or xi = -pi/2)
        if abs(xi_b) < eps or abs(xi) < eps\
                or abs(xi_b - M_PI_2) < eps or abs(xi_b - M_PI_2) < eps\
                or abs(xi_b + M_PI_2) < eps or abs(xi_b + M_PI_2) < eps:
            return -1 if (random.randrange(32768) % 2 != 0) else 1

        if xi_b > 0 and xi > 0:
            return 1 if xi_b >= xi else -1

        if xi_b > 0 and xi < 0:
            return Rqiea.sign(alpha * alphabest)

        if xi_b < 0 and xi > 0:
            return -Rqiea.sign(alpha * alphabest)

        if xi_b < 0 and xi < 0:
            return 1 if xi_b >= xi else -1

        return Rqiea.sign(xi_b)


    def update(self):
        for i in range(self._populationSize):
            for j in range(self._chromlen):
                qij = 2 * (i * self._chromlen + j)
                qprim = np.zeros(2, dtype=float)

                k = math.pi / (100 + self._currentGeneration % 100)
                theta = k * Rqiea.lut(self._Q[qij], self._Q[qij + 1], self._bestq[j][0], self._bestq[j][1])

                qprim[0] = self._Q[qij] * math.cos(theta) + self._Q[qij + 1] * (-math.sin(theta))
                qprim[1] = self._Q[qij] * math.sin(theta) + self._Q[qij + 1] * math.cos(theta)

                self._Q[qij] = qprim[0]
                self._Q[qij + 1] = qprim[1]


    def recombine(self):
        i, j = random.randrange(self._populationSize), random.randrange(self._populationSize)
        while i == j:
            j = random.randrange(self._populationSize)

        h1 = random.randrange(self._chromlen)
        h2 = random.randrange(self._chromlen - h1) + h1

        q1, q2 = i * self._chromlen * 2, j * self._chromlen * 2

        buf = self._Q[q1: q1 + 2 * self._chromlen + 1]

        self._Q[q1 + h1 * 2: q1 + h1 * 2 + (h2 - h1) * 2 + 1] = self._Q[q2 + h1: q2 + h1 + (h2 - h1) * 2 + 1]
        self._Q[q2 + h1 * 2: q2 + h1 * 2 + (h2 - h1) * 2 + 1] = buf[h1: h1 + (h2 - h1) * 2 + 1]

        for k in range(h1, h2):
            self._Q[q1 + k * 2], self._Q[q2 + k * 2] = self._Q[q2 + k * 2], self._Q[q1 + k * 2]


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
        currentGeneration = self._currentGeneration
        self.observe(pop[0])
        self.evaluate()
        self.storebest(pop[0])

        self._bestNotEnhance, lastBestFit = 0, 0.0

        cur, next = 0, 1
        while currentGeneration < self._max_iterations:
            if currentGeneration > 0:
                best = self.result
                if self._bestNotEnhance < self._maxRepeat:
                    print("Fitness:", "{:f}\t".format(best.fitness), "Generation:", currentGeneration, end="    \r")
                else:
                    print("Fitness:", "{:f}\t".format(best.fitness), "Generation:", currentGeneration, end=" ...\r")

                # algorithm has reached criteria?
                if best.fitness > minFitness:
                    break

                difference = abs(best.fitness - lastBestFit)
                if difference <= 0.0000001:
                    self._bestNotEnhance += 1
                else:
                    lastBestFit = best.fitness
                    self._bestNotEnhance = 0

                if self._bestNotEnhance > (maxRepeat / 50):
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

            cur, next = next, cur

            if self._bestNotEnhance >= self._maxRepeat and currentGeneration % 4 == 0:
                for i in range(populationSize):
                    positions = np.zeros(self._chromlen, dtype=float)
                    start = i * self._chromlen
                    pop[cur][i].extractPositions(positions)
                    self._P[start: start + self._chromlen] = positions

                    self.observe(pop[cur])
                    self.evaluate()
                    self.storebest(pop[cur])
                    self.update()
                    self.recombine()

            currentGeneration += 1
            self._currentGeneration = currentGeneration

    def __str__(self):
        return "Real observation QIEA (rQIEA)"
