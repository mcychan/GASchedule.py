import NsgaII
import sys


# Non-dominated Ranking Genetic Algorithm (NRGA)
class Ngra(NsgaII.NsgaII):
    # Initializes genetic algorithm
    def __init__(self, configuration, numberOfCrossoverPoints=2, mutationSize=2, crossoverProbability=80,
                 mutationProbability=3):
        NsgaII.NsgaII.__init__(self, configuration, numberOfCrossoverPoints, mutationSize, crossoverProbability, mutationProbability)

    # calculate crowding distance function
    def calculateCrowdingDistance(self, front, totalChromosome):
        N = self._populationSize
        divisor = N * (N + 1)
        distance = {m: 0.0 for m in front}
        obj = {m: 2 * self._rank[m] / divisor for m in front}
        sorted_keys = sorted(obj, key=obj.get)
        distance[sorted_keys[0]] = distance[sorted_keys[len(front) - 1]] = sys.float_info.max
        values_length = len(set(obj.values()))
        if values_length > 1:
            for i in range(1, len(front) - 1):
                distance[sorted_keys[i]] += (obj[sorted_keys[i + 1]] - obj[sorted_keys[i - 1]]) / (obj[sorted_keys[len(front) - 1]] - obj[sorted_keys[0]])

        return distance
    