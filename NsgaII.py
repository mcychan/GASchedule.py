import Schedule
import random
import sys
import time


# NSGA II
class NsgaII:
    def initAlgorithm(self, prototype, numberOfChromosomes=100, replaceByGeneration=8):
        # Prototype of chromosomes in population
        self._prototype = prototype

        # there should be at least 2 chromosomes in population
        if numberOfChromosomes < 2:
            numberOfChromosomes = 2

        # Population of chromosomes
        self._chromosomes = []
        self._populationSize = numberOfChromosomes    

    # Initializes genetic algorithm
    def __init__(self, configuration, numberOfCrossoverPoints=2, mutationSize=2, crossoverProbability=80,
                 mutationProbability=3):
        self.initAlgorithm(Schedule.Schedule(configuration))
        self._mutationSize = mutationSize
        self._numberOfCrossoverPoints = numberOfCrossoverPoints
        self._crossoverProbability = crossoverProbability
        self._mutationProbability = mutationProbability

    @property
    # Returns pointer to best chromosomes in population
    def result(self):
        return self._chromosomes[0]

    # non-dominated sorting function
    def nonDominatedSorting(self, totalChromosome):
        doublePopulationSize = self._populationSize * 2
        s = doublePopulationSize * [ set() ]
        n = doublePopulationSize * [0]
        rank = doublePopulationSize * [0]
        front = [ set() ]
        range1 = range(doublePopulationSize)

        for p in range1:
            for q in range1:
                if totalChromosome[p].fitness > totalChromosome[q].fitness:
                    s[p].add(q)
                elif totalChromosome[p].fitness < totalChromosome[q].fitness:
                    n[p] += 1

            if n[p] == 0:
                rank[p] = 0
                front[0].add(p)
    
        i = 0
        while front[i]:
            Q = set()
            for p in front[i]:
                for q in s[p]:
                    n[q] -= 1
                    if n[q] == 0:
                        rank[q] = i + 1
                        Q.add(q)
            i += 1
            front.append(Q)
        
        return front[0: len(front) - 1]

    # calculate crowding distance function
    def calculateCrowdingDistance(self, front, totalChromosome):
        distance = {m: 0.0 for m in front}
        obj = {m: totalChromosome[m].fitness for m in front}
        sorted_keys = sorted(obj, key=obj.get)
        distance[sorted_keys[0]] = distance[sorted_keys[len(front) - 1]] = sys.float_info.max
        values_length = len(set(obj.values()))
        if values_length > 1:
            for i in range(1, len(front) - 1):
                distance[sorted_keys[i]] += (obj[sorted_keys[i + 1]] - obj[sorted_keys[i - 1]]) / (obj[sorted_keys[len(front) - 1]] - obj[sorted_keys[0]])

        return distance

    def selection(self, front, totalChromosome):
        populationSize = self._populationSize
        calculateCrowdingDistance = self.calculateCrowdingDistance
        N = 0
        newPop = []
        while N < populationSize:
            for row in front:
                N += len(row)
                if N > populationSize:
                    distance = calculateCrowdingDistance(row, totalChromosome)
                    sortedCdf = reversed(sorted(distance, key=distance.get))
                    for j in sortedCdf:
                        if len(newPop) >= populationSize:
                            break
                        newPop.append(j)
                    break
                newPop.extend(row)
    
        return [totalChromosome[n] for n in newPop]

    def replacement(self, population):
        populationSize = self._populationSize
        numberOfCrossoverPoints = self._numberOfCrossoverPoints
        crossoverProbability = self._crossoverProbability
        offspring = []
        # generate a random sequence to select the parent chromosome to crossover
        S = list(range(populationSize))
        random.shuffle(S)

        halfPopulationSize = populationSize // 2
        for m in range(halfPopulationSize):
            parent0 = population[S[2 * m]]
            parent1 = population[S[2 * m + 1]]
            child0 = parent0.crossover(parent1, numberOfCrossoverPoints, crossoverProbability)
            child1 = parent1.crossover(parent0, numberOfCrossoverPoints, crossoverProbability)

            # append child chromosome to offspring list
            offspring.extend((child0, child1))
            
        return offspring
                
    # initialize new population with chromosomes randomly built using prototype
    def initialize(self, population):
        prototype = self._prototype

        for i in range(len(population)):
            # add new chromosome to population
            population[i] = prototype.makeNewFromPrototype()

    # Starts and executes algorithm
    def run(self, maxRepeat=9999, minFitness=0.999):
        mutationSize = self._mutationSize        
        mutationProbability = self._mutationProbability
        nonDominatedSorting = self.nonDominatedSorting
        selection = self.selection
        populationSize = self._populationSize
        population = populationSize * [None]

        self.initialize(population)
        random.seed(round(time.time() * 1000))

        # Current generation
        currentGeneration = 0

        repeat = 0
        lastBestFit = 0.0

        while 1:            
            if currentGeneration > 0:
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
                    self._crossoverProbability += 1

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
                lastBestFit = best.fitness

            random.seed(round(time.time() * 1000))
            currentGeneration += 1
            
    def __str__(self):
        return "NSGA II"             
            