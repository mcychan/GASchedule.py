import NsgaII
import random


# Non-dominated Ranking Genetic Algorithm (NRGA)
class Ngra(NsgaII.NsgaII):
    # Initializes genetic algorithm
    def __init__(self, configuration, numberOfCrossoverPoints=2, mutationSize=2, crossoverProbability=80,
                 mutationProbability=3):
        NsgaII.NsgaII.__init__(self, configuration, numberOfCrossoverPoints, mutationSize, crossoverProbability, mutationProbability)
        
    # get the cumulative sum of a list
    @staticmethod    
    def __cumulative(lists): 
        cu_list = [] 
        length = len(lists) 
        cu_list = [sum(lists[0:x:1]) for x in range(0, length+1)] 
        return cu_list[1:]
        
    # ranked based roulette wheel function
    def replacement(self, population):
        populationSize = self._populationSize
        numberOfCrossoverPoints = self._numberOfCrossoverPoints
        crossoverProbability = self._crossoverProbability
        
        obj = {m: population[m].fitness for m in range(populationSize)}
        sortedIndices = list(reversed(sorted(obj, key=obj.get)))
        totalFitness = (populationSize + 1) * populationSize / 2
        probSelection = [i / totalFitness for i in range(populationSize)]
        cumProb = self.__cumulative(probSelection)
        selectIndices = [random.random() for i in range(populationSize)]
        
        parent = 2 * [None]
        parentIndex = 0        
        offspring = []
        for i in range(populationSize):
            selected = False
            for j in range(populationSize - 1):
                if cumProb[j] < selectIndices[i] and cumProb[j + 1] >= selectIndices[i]:
                    parent[parentIndex % 2] = population[sortedIndices[j + 1]]
                    parentIndex += 1
                    selected = True
                    break
                    
            if not selected:
                parent[parentIndex % 2] = population[sortedIndices[i]]
                parentIndex += 1
                
            if parentIndex % 2 == 0:
                child0 = parent[0].crossover(parent[1], numberOfCrossoverPoints, crossoverProbability)
                child1 = parent[1].crossover(parent[0], numberOfCrossoverPoints, crossoverProbability)
                # append child chromosome to offspring list
                offspring.extend((child0, child1))
            
        return offspring
        
    def initialize(self, population):
        super().initialize(population)
        offspring = self.replacement(population)
        population.clear()
        population.extend(offspring)
        
    def __str__(self):
        return "Non-dominated Ranking Genetic Algorithm (NRGA)"
             