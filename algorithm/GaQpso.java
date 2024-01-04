package hk.edu.gaSchedule.algorithm;
/*
 * Jun Sun, Wei Fang, Vasile Palade, Xiaojun Wu, Wenbo Xu, "Quantum-behaved particle swarm optimization with Gaussian distributed local attractor point," 
 * Applied Mathematics and Computation, Volume 218, Issue 7, 2011,
 * Pages 3763-3775, doi: 10.1016/j.amc.2011.09.021
 * Copyright (c) 2024 Miller Cy Chan
 */

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

import hk.edu.gaSchedule.model.Chromosome;
import hk.edu.gaSchedule.model.Configuration;

public class GaQpso<T extends Chromosome<T> > extends NsgaIII<T> {
	private int _currentGeneration = 0, _max_iterations = 5000;
	
	private int _chromlen;

	private float[] _gBest, _pBestScore;
			
	private float[][] _pBestPosition = null, _current_position = null;

	private static final double _alpha0 = .5, _alpha1 = .96;

	private static Random _random = new Random(System.currentTimeMillis());

	// Initializes GAQPSO
	public GaQpso(T prototype, int numberOfCrossoverPoints, int mutationSize, float crossoverProbability, float mutationProbability)
	{
		super(prototype, numberOfCrossoverPoints, mutationSize, crossoverProbability, mutationProbability);
	}

	protected void initialize(List<T> population)
	{
		for (int i = 0; i < _populationSize; ++i) {
			List<Float> positions = new ArrayList<>();
			
			// initialize new population with chromosomes randomly built using prototype
			population.add(_prototype.makeNewFromPrototype(positions));	
			
			if(i < 1) {
				_chromlen = positions.size();
				_gBest = new float[_chromlen];
				_pBestScore = new float[_populationSize];
				_pBestPosition = new float[_populationSize][_chromlen];
				_current_position = new float[_populationSize][_chromlen];
			}
		}
	}
	
	private float[] optimum(float[] localVal, T chromosome)
	{
		T localBest = _prototype.makeEmptyFromPrototype(null);
		localBest.updatePositions(localVal);
		
		if(localBest.dominates(chromosome)) {
			chromosome.updatePositions(localVal);
			return localVal;
		}
		
		float[] positions = new float[_chromlen];
		chromosome.extractPositions(positions);
		return positions;
	}
	
	// return gaussian(x) = standard Gaussian N
	private static double gaussian(double x)
	{
		return Math.exp(-x * x / 2) / Math.sqrt(2 * Math.PI);
	}

	// return gaussian(x, mu, sigma) = Gaussian N with mean mu and stddev sigma
	private static double gaussian(double x, float mu, float sigma)
	{
		if(sigma == 0)
			return gaussian(x);
		return gaussian((x - mu) / sigma) / sigma;
	}

	private void updatePosition(List<T> population)
	{
		float[] mBest = new float[_chromlen];
		float[][] currentPosition = _current_position.clone();
		for(int i = 0; i < _populationSize; ++i) {
			if(i == 0)
				population.get(i).extractPositions(_gBest);
			else {
				float fitness = population.get(i).getFitness();
				if(fitness > _pBestScore[i]) {
					_pBestScore[i] = fitness;
					population.get(i).extractPositions(_current_position[i]);
					_pBestPosition[i] = _current_position[i].clone();
				}
				_gBest = optimum(_gBest, population.get(i));
			}
			
			for(int j = 0; j < _chromlen; ++j)
				mBest[j] += _pBestPosition[i][j] / _populationSize;
		}

		double alpha = _alpha0 + (_max_iterations - _currentGeneration) * (_alpha1 - _alpha0) / _max_iterations;
		for(int i = 0; i < _populationSize; ++i) {
			for(int j = 0; j < _chromlen; ++j) {
				double phi = _random.nextDouble();
				double u = _random.nextDouble();
				double p = phi * _pBestPosition[i][j] + (1 - phi) * _gBest[j];
				double np = gaussian(p, mBest[j], mBest[j] - _pBestPosition[i][j]);
				double NP = (Configuration.rand(100) < _mutationProbability) ? np : p; 
				
				if(_random.nextDouble() > .5)
					_current_position[i][j] += (float) (NP + alpha * Math.abs(mBest[j] - currentPosition[i][j]) * Math.log(1.0 / u));
				else
					_current_position[i][j] += (float) (NP - alpha * Math.abs(mBest[j] - currentPosition[i][j]) * Math.log(1.0 / u));
			}

			_current_position[i] = optimum(_current_position[i], population.get(i));
		}
	}

	@Override
	protected List<T> replacement(List<T> population)
	{
		updatePosition(population);
		
		for (int i = 0; i < _populationSize; ++i) {
			T chromosome = _prototype.makeEmptyFromPrototype(null);
			chromosome.updatePositions(_current_position[i]);
			population.set(i, chromosome);
		}

		return super.replacement(population);
	}
	
	// Starts and executes algorithm
	public void run(int maxRepeat, double minFitness)
	{
		if (_prototype == null)
			return;

		List<T>[] pop = new ArrayList[2];
		pop[0] = new ArrayList<>();
		initialize(pop[0]);

		// Current generation
		_currentGeneration = 0;
		int bestNotEnhance = 0;
		double lastBestFit = 0.0;

		int cur = 0, next = 1;
		while(_currentGeneration < _max_iterations)
		{
			T best = getResult();
			if(_currentGeneration > 0) {
				String status = String.format("\rFitness: %f\t Generation: %d    ", best.getFitness(), _currentGeneration);	
				System.out.print(status);
				
				// algorithm has reached criteria?
				if (best.getFitness() > minFitness)
					break;
	
				double difference = Math.abs(best.getFitness() - lastBestFit);
				if (difference <= 0.0000001)
					++bestNotEnhance;
				else {
					lastBestFit = best.getFitness();
					bestNotEnhance = 0;
				}

				if (bestNotEnhance > (maxRepeat / 100))
					reform();
			}			
			
			/******************* crossover *****************/
			List<T> offspring = crossing(pop[cur]);
			
			/******************* mutation *****************/
			for(T child : offspring)
				child.mutation(_mutationSize, _mutationProbability);
			
			pop[cur].addAll(offspring);
			
			/******************* replacement *****************/	
			pop[next] = replacement(pop[cur]);
			_best = pop[next].get(0).dominates( pop[cur].get(0)) ? pop[next].get(0) : pop[cur].get(0);
			
			int temp = cur;
			cur = next;
			next = temp;
			++_currentGeneration;
		}
	}
	
	@Override
	public String toString()
	{
		return "Gaussian distributed local attractor QPSO (GAQPSO) algorithm";
	}
}
