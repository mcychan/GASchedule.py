package hk.edu.gaSchedule.model;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

// Schedule chromosome
public class Schedule implements Chromosome<Schedule>
{
	private Configuration _configuration;		

	// Fitness value of chromosome
	private float _fitness;

	// Flags of class requirements satisfaction
	private boolean[] _criteria;

	// Time-space slots, one entry represent one hour in one classroom
	private List<CourseClass>[] _slots;

	// Class table for chromosome
	// Used to determine first time-space slot used by class
	private Map<CourseClass, Integer> _classes;
	
	private float _diversity;
	
	private int _rank;

	// Initializes chromosomes with configuration block (setup of chromosome)
	public Schedule(Configuration configuration)
	{
		_configuration = configuration;			
		_fitness = 0;

		// reserve space for time-space slots in chromosomes code
		_slots = (List<CourseClass>[]) new List[Constant.DAYS_NUM * Constant.DAY_HOURS * _configuration.getNumberOfRooms()];
		for(int i=0; i< _slots.length; ++i)
			_slots[i] = new ArrayList<CourseClass>();
		_classes = new TreeMap<>();

		// reserve space for flags of class requirements
		_criteria = new boolean[_configuration.getNumberOfCourseClasses() * Constant.CRITERIA_NUM];
	}

	// Copy constructor
	private Schedule copy(Schedule c, boolean setupOnly)
	{		
		if (!setupOnly)
		{
			_configuration = c._configuration;
			// copy code				
			_slots = c._slots.clone();
			_classes = new TreeMap<>(c._classes);

			// copy flags of class requirements
			_criteria = c._criteria.clone();

			// copy fitness
			_fitness = c._fitness;
			return this;
		}
		return new Schedule(c._configuration);
	}

	// Makes new chromosome with same setup but with randomly chosen code
	public Schedule makeNewFromPrototype(List<Float> positions)
	{
		// make new chromosome, copy chromosome setup
		Schedule newChromosome = copy(this, true);
		int nr = _configuration.getNumberOfRooms();

		// place classes at random position
		List<CourseClass> c = _configuration.getCourseClasses();
		for (CourseClass courseClass : c)
		{
			// determine random position of class			
			int dur = courseClass.Duration;

			int day = Configuration.rand(0, Constant.DAYS_NUM - 1);
			int room = Configuration.rand(0, nr - 1);
			int time = Configuration.rand(0, Constant.DAY_HOURS - 1 - dur);
			Reservation reservation = Reservation.getReservation(nr, day, time, room);
			if(positions != null) {
				positions.add(day * 1.0f);
				positions.add(room * 1.0f);
				positions.add(time * 1.0f);
			}

			// fill time-space slots, for each hour of class
			for (int i = dur - 1; i >= 0; --i)
				newChromosome._slots[reservation.hashCode() + i].add(courseClass);

			// insert in class table of chromosome
			newChromosome._classes.put(courseClass, reservation.hashCode());
		}

		newChromosome.calculateFitness();
		return newChromosome;
	}
	
	public Schedule makeNewFromPrototype()
	{
		return makeNewFromPrototype(null);
	}

	// Performes crossover operation using to chromosomes and returns pointer to offspring
	public Schedule crossover(Schedule parent, int numberOfCrossoverPoints, float crossoverProbability)
	{
		// check probability of crossover operation
		if (Configuration.rand() % 100 > crossoverProbability)
			// no crossover, just copy first parent
			return copy(this, false);

		// new chromosome object, copy chromosome setup
		Schedule n = copy(this, true);

		// number of classes
		int size = _classes.size();

		boolean[] cp = new boolean[size];

		// determine crossover point (randomly)
		for (int i = numberOfCrossoverPoints; i > 0; --i)
		{
			for(; ;)
			{
				int p = Configuration.rand() % size;
				if (!cp[p])
				{
					cp[p] = true;
					break;
				}
			}
		}

		// make new code by combining parent codes
		boolean first = Configuration.rand() % 2 == 0;
		CourseClass[] classes = _classes.keySet().toArray(new CourseClass[0]);
		CourseClass[] parentClasses = parent._classes.keySet().toArray(new CourseClass[0]);
		for (int i = 0; i < size; ++i)
		{
			if (first)
			{
				CourseClass courseClass = classes[i];
				Reservation reservation = Reservation.getReservation(_classes.get(courseClass));
				// insert class from first parent into new chromosome's class table
				n._classes.put(courseClass, reservation.hashCode());
				// all time-space slots of class are copied
				for (int j = courseClass.Duration - 1; j >= 0; --j)
					n._slots[reservation.hashCode() + j].add(courseClass);
			}
			else
			{
				CourseClass courseClass = parentClasses[i];
				Reservation reservation = Reservation.getReservation(parent._classes.get(courseClass));
				// insert class from second parent into new chromosome's class table
				n._classes.put(courseClass, reservation.hashCode());
				// all time-space slots of class are copied
				for (int j = courseClass.Duration - 1; j >= 0; --j)
					n._slots[reservation.hashCode() + j].add(courseClass);
			}

			// crossover point
			if (cp[i])
				// change source chromosome
				first = !first;
		}

		n.calculateFitness();

		// return smart pointer to offspring
		return n;
	}
	
	// Performes crossover operation using to chromosomes and returns pointer to offspring
	public Schedule crossover(Schedule parent, Schedule r1, Schedule r2, Schedule r3, float etaCross, float crossoverProbability)
	{
		// number of classes
		int size = _classes.size();
		int jrand = Configuration.rand(size);
		
		// new chromosome object, copy chromosome setup
		Schedule n = copy(this, true);
		
		int nr = _configuration.getNumberOfRooms();
		CourseClass[] classes = _classes.keySet().toArray(new CourseClass[0]);
		CourseClass[] parentClasses = parent._classes.keySet().toArray(new CourseClass[0]);
		for (int i = 0; i < size; ++i)
		{
			// check probability of crossover operation
			if (Configuration.rand() % 100 > crossoverProbability || i == jrand) {
				CourseClass courseClass = classes[i];
				Reservation reservation1 = Reservation.getReservation(r1.getClasses().get(courseClass));
				Reservation reservation2 = Reservation.getReservation(r2.getClasses().get(courseClass));
				Reservation reservation3 = Reservation.getReservation(r3.getClasses().get(courseClass));
				
				// determine random position of class				
				int dur = courseClass.Duration;
				int day = (int) (reservation3.getDay() + etaCross * (reservation1.getDay() - reservation2.getDay()));
				if(day < 0)
					day = 0;
				else if(day >= Constant.DAYS_NUM)
					day = Constant.DAYS_NUM - 1;
				
				int room = (int) (reservation3.getRoom() + etaCross * (reservation1.getRoom() - reservation2.getRoom()));
				if(room < 0)
					room = 0;
				else if(room >= nr)
					room = nr - 1;
				
				int time = (int) (reservation3.getTime() + etaCross * (reservation1.getTime() - reservation2.getTime()));
				if(time < 0)
					time = 0;
				else if(time >= (Constant.DAY_HOURS - dur))
					time = Constant.DAY_HOURS - 1 - dur;				

				Reservation reservation = Reservation.getReservation(nr, day, time, room);

				// fill time-space slots, for each hour of class
				for (int j = courseClass.Duration - 1; j >= 0; --j)
					n._slots[reservation.hashCode() + j].add(courseClass);

				// insert in class table of chromosome
				n._classes.put(courseClass, reservation.hashCode());
			} else {
				CourseClass courseClass = parentClasses[i];
				Reservation reservation = Reservation.getReservation(parent._classes.get(courseClass));
				
				// all time-space slots of class are copied
				for (int j = courseClass.Duration - 1; j >= 0; --j)
					n._slots[reservation.hashCode() + j].add(courseClass);
				
				// insert class from second parent into new chromosome's class table
				n._classes.put(courseClass, reservation.hashCode());
			}
		}			

		n.calculateFitness();

		// return smart pointer to offspring
		return n;
	}
	
	private void repair(CourseClass cc1, int reservation1_index, Reservation reservation2)
	{
		int dur = cc1.Duration;
		// move all time-space slots
		for (int j = dur - 1; j >= 0; --j)
		{
			// remove class hour from current time-space slot
			List<CourseClass> cl = _slots[reservation1_index + j];
			cl.removeIf(cc -> cc == cc1);

			// move class hour to new time-space slot
			_slots[reservation2.hashCode() + j].add(cc1);
		}

		// change entry of class table to point to new time-space slots
		_classes.put(cc1, reservation2.hashCode());
	}

	// Performs mutation on chromosome
	public void mutation(int mutationSize, float mutationProbability)
	{
		// check probability of mutation operation
		if (Configuration.rand() % 100 > mutationProbability)
			return;

		// number of classes
		int numberOfClasses = _classes.size();
		int nr = _configuration.getNumberOfRooms();

		CourseClass[] classes = _classes.keySet().toArray(new CourseClass[0]);
		// move selected number of classes at random position
		for (int i = mutationSize; i > 0; --i)
		{
			// select ranom chromosome for movement
			int mpos = Configuration.rand() % numberOfClasses;

			// current time-space slot used by class
			CourseClass cc1 = classes[mpos];

			// determine position of class randomly			
			int dur = cc1.Duration;
			int day = Configuration.rand(0, Constant.DAYS_NUM - 1);
			int room = Configuration.rand(0, nr - 1);
			int time = Configuration.rand(0, (Constant.DAY_HOURS - 1 - dur));
			Reservation reservation2 = Reservation.getReservation(nr, day, time, room);

			repair(cc1, _classes.get(cc1), reservation2);
		}

		calculateFitness();
	}

	// Calculates fitness value of chromosome
	public void calculateFitness()
	{
		// chromosome's score
		int score = 0;

		int numberOfRooms = _configuration.getNumberOfRooms();
		int daySize = Constant.DAY_HOURS * numberOfRooms;

		int ci = 0;
		// check criterias and calculate scores for each class in schedule
		for (CourseClass cc : _classes.keySet())
		{
			// coordinate of time-space slot
			Reservation reservation = Reservation.getReservation(_classes.get(cc));
			int day = reservation.getDay();
			int time = reservation.getTime();
			int room = reservation.getRoom();

			int dur = cc.Duration;

			boolean ro = Criteria.isRoomOverlapped(_slots, reservation, dur);
			// on room overlapping
			if (!ro)
				score++;
			else
				score = 0;

			_criteria[ci + 0] = !ro;
			
			Room r = _configuration.getRoomById(room);
			_criteria[ci + 1] = Criteria.isSeatEnough(r, cc);
			if (_criteria[ci + 1])
				score++;
			else
				score /= 2;

			_criteria[ci + 2] = Criteria.isComputerEnough(r, cc);
			if (_criteria[ci + 2])
				score++;
			else
				score /= 2;

			boolean[] total_overlap = Criteria.isOverlappedProfStudentGrp(_slots, cc, numberOfRooms, day * daySize + time, dur);

			// professors have no overlapping classes?
			if (!total_overlap[0])
				score++;
			else
				score = 0;
			_criteria[ci + 3] = !total_overlap[0];

			// student groups has no overlapping classes?
			if (!total_overlap[1])
				score++;
			else
				score = 0;
			_criteria[ci + 4] = !total_overlap[1];
			
			ci += Constant.CRITERIA_NUM;
		}

		// calculate fitess value based on score
		_fitness = (float)score / (_configuration.getNumberOfCourseClasses() * Constant.DAYS_NUM);		
	}

	// Returns fitness value of chromosome
	public float getFitness() { return _fitness; }

	public Configuration getConfiguration() { return _configuration; }

	// Returns reference to table of classes
	public Map<CourseClass, Integer> getClasses() { return _classes; }

	// Returns array of flags of class requiroments satisfaction
	public boolean[] getCriteria() { return _criteria; }

	// Return reference to array of time-space slots
	public List<CourseClass>[] getSlots() { return _slots; }
	
	@Override
	public int getDifference(Schedule other)
	{
		boolean[] criteria = other.getCriteria();
		int val = 0;
		for(int i = 0; i < _criteria.length && i < criteria.length; ++i) {
			if(_criteria[i] ^ criteria[i])
				++val;
		}
		return val;
	}

	@Override
	public float getDiversity() {
		return _diversity;
	}

	@Override
	public void setDiversity(float diversity) {
		_diversity = diversity;
	}

	@Override
	public int getRank() {
		return _rank;
	}

	@Override
	public void setRank(int rank) {
		_rank = rank;
	}
	
	@Override
	public void extractPositions(float[] positions) {
		int i = 0;
		for (CourseClass cc : _classes.keySet())
		{
			Reservation reservation = Reservation.getReservation(_classes.get(cc));
			positions[i++] = reservation.getDay();
			positions[i++] = reservation.getRoom();
			positions[i++] = reservation.getTime();
		}
	}
	
	@Override
	public void updatePositions(float[] positions) {
		int nr = _configuration.getNumberOfRooms();
		int i = 0;
		for (CourseClass cc : _classes.keySet())
		{
			int dur = cc.Duration;
			int day = (int) Math.abs(positions[i++] % Constant.DAYS_NUM);			
			int room = (int) Math.abs(positions[i++] % nr);			
			int time = (int) Math.abs(positions[i++] % (Constant.DAY_HOURS - dur));
			
			Reservation reservation2 = Reservation.getReservation(nr, day, time, room);			
			repair(cc, _classes.get(cc), reservation2);
		}

		calculateFitness();
	}
	
}
