using System;
using System.Collections.Generic;
using System.Linq;
using GaSchedule.Model;

/*
 * Jun Sun, Wei Fang, Vasile Palade, Xiaojun Wu, Wenbo Xu, "Quantum-behaved particle swarm optimization with Gaussian distributed local attractor point," 
 * Applied Mathematics and Computation, Volume 218, Issue 7, 2011,
 * Pages 3763-3775, doi: 10.1016/j.amc.2011.09.021
 * Copyright (c) 2024 Miller Cy Chan
 */

namespace GaSchedule.Algorithm
{
	/****************** Cuckoo Search Optimization (CSO) **********************/
	public class GaQpso<T> : NsgaIII<T> where T : Chromosome<T>
	{
		private int _currentGeneration = 0, _max_iterations = 5000;
		private int _chromlen;
		private float[] _gBest, _pBestScore;
		private float[][] _pBestPosition = null, _current_position = null;
		private const double _alpha0 = .5, _alpha1 = .96;

		// Initializes GAQPSO
		public GaQpso(T prototype, int numberOfCrossoverPoints = 2, int mutationSize = 2, float crossoverProbability = 80, float mutationProbability = 3) : base(prototype, numberOfCrossoverPoints, mutationSize, crossoverProbability, mutationProbability)
		{
		}

		static E[][] CreateArray<E>(int rows, int cols)
		{
			E[][] array = new E[rows][];
			for (int i = 0; i < array.GetLength(0); i++)
				array[i] = new E[cols];

			return array;
		}

		protected override void Initialize(List<T> population)
		{
			for (int i = 0; i < _populationSize; ++i) {
				List<float> positions = new();

				// initialize new population with chromosomes randomly built using prototype
				population.Add(_prototype.MakeNewFromPrototype(positions));

				if(i < 1) {
					_chromlen = positions.Count;
					_gBest = new float[_chromlen];
					_pBestScore = new float[_populationSize];
					_pBestPosition = CreateArray<float>(_populationSize, _chromlen);
					_current_position = CreateArray<float>(_populationSize, _chromlen);
				}
			}
		}

		private float[] Optimum(float[] localVal, T chromosome)
		{
			var localBest = _prototype.MakeEmptyFromPrototype();
			localBest.UpdatePositions(localVal);
			
			if(localBest.Dominates(chromosome)) {
				chromosome.UpdatePositions(localVal);
				return localVal;
			}

			var positions = new float[_chromlen];
			chromosome.ExtractPositions(positions);
			return positions;
		}

		// return Gaussian(x, mu, sigma) = Gaussian N with mean mu and stddev sigma
		private static double Gaussian(double x, float sigma)
		{
			return Configuration.NextGaussian() * sigma + x;
		}

		private void UpdatePosition(List<T> population)
		{
			var mBest = new float[_chromlen];
			var current_position = _current_position.ToArray();
			for(int i = 0; i < _populationSize; ++i) {
				var fitness = population[i].Fitness;
				if (fitness > _pBestScore[i])
				{
					_pBestScore[i] = fitness;
					population[i].ExtractPositions(_current_position[i]);
                    _pBestPosition[i] = _current_position[i].ToArray();
				}
				_gBest = Optimum(_pBestScore, population[i]);

				for(int j = 0; j < _chromlen; ++j)
					mBest[j] += _pBestPosition[i][j] / _populationSize;
			}

			var alpha = _alpha0 + (_max_iterations - _currentGeneration) * (_alpha1 - _alpha0) / _max_iterations;
			for(int i = 0; i < _populationSize; ++i) {
				for(int j = 0; j < _chromlen; ++j) {
					var phi = Configuration.Random();
					var u = Configuration.Random();
					var p = phi * _pBestPosition[i][j] + (1 - phi) * _gBest[j];
					var np = Gaussian(p, mBest[j] - _pBestPosition[i][j]);
					var NP = (Configuration.Rand(100) < _mutationProbability) ? p : np;

					if(Configuration.Random() > .5)
						_current_position[i][j] += (float) (NP + alpha * Math.Abs(mBest[j] - current_position[i][j]) * Math.Log(1.0 / u));
					else
						_current_position[i][j] += (float) (NP - alpha * Math.Abs(mBest[j] - current_position[i][j]) * Math.Log(1.0 / u));
				}
				_current_position[i] = Optimum(_current_position[i], population[i]);
			}
		}


		protected override List<T> Replacement(List<T> population)
		{
			UpdatePosition(population);

			for (int i = 0; i < _populationSize; ++i) {
				var chromosome = _prototype.MakeEmptyFromPrototype();
				chromosome.UpdatePositions(_current_position[i]);
				population[i] = chromosome;
			}

			return base.Replacement(population);
		}

		// Starts and executes algorithm
		public override void Run(int maxRepeat = 9999, double minFitness = 0.999)
		{
			if (_prototype == null)
				return;

			var pop = new List<T>[2];
			pop[0] = new List<T>();
			Initialize(pop[0]);

			// Current generation
			_currentGeneration = 0;
			int bestNotEnhance = 0;
			double lastBestFit = 0.0;

			int cur = 0, next = 1;
			while(_currentGeneration < _max_iterations)
			{
				var best = Result;
				if (_currentGeneration > 0)
				{
					var status = string.Format("\rFitness: {0:F6}\t Generation: {1}", best.Fitness, _currentGeneration);
					Console.Write(status);

					// algorithm has reached criteria?
					if (best.Fitness > minFitness)
						break;

					var difference = Math.Abs(best.Fitness - lastBestFit);
					if (difference <= 1e-6)
						++bestNotEnhance;
					else {
						lastBestFit = best.Fitness;
						bestNotEnhance = 0;
					}

					if (bestNotEnhance > (maxRepeat / 100))
						Reform();
				}

				/******************* crossover *****************/
				var offspring = Crossing(pop[cur]);

				/******************* mutation *****************/
				foreach (var child in offspring)
					child.Mutation(_mutationSize, _mutationProbability);

				pop[cur].AddRange(offspring);

				/******************* replacement *****************/
				pop[next] = Replacement(pop[cur]);
				_best = pop[next][0].Dominates(pop[cur][0]) ? pop[next][0] : pop[cur][0];

				(cur, next) = (next, cur);
				++_currentGeneration;
			}
		}

		public override string ToString()
		{
			return "Gaussian distributed local attractor QPSO (GAQPSO)";
		}
	}
}
