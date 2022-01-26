import random
from mesa import Model
from mesa.time import RandomActivation
from space import OptimizedContinuousSpace
from agents import Prey, Predator, Grass
from datacollector import PreyPredatorCollector
from utils import move_coordinates

class PreyPredatorModel(Model):
    def __init__(self, width=500, height=500,
                 initial_prey=100, initial_predator=30,
                 prey_reproduction_chance=0.05, predator_death_chance=0.05,
                 predator_reproduction_chance=0.05, predator_min_reproduction_energy=20,
                 prey_gain_from_food=4, predator_gain_from_food=20, food_regrowth_time=30,
                 grass_clusters=8, grass_cluster_size=100, prey_sight_on_pred=25,
                 min_distance_between_prey=18):

        super().__init__()
        self.space = OptimizedContinuousSpace(width, height, torus=True)

        self.prey_reproduction_chance = prey_reproduction_chance
        self.predator_death_chance = predator_death_chance
        self.predator_reproduction_chance = predator_reproduction_chance
        self.predator_min_reproduction_energy = predator_min_reproduction_energy

        self.prey_gain_from_food = prey_gain_from_food
        self.predator_gain_from_food = predator_gain_from_food
        self.food_regrowth_time = food_regrowth_time
        self.grass_clusters = grass_clusters
        self.grass_cluster_size = grass_cluster_size
        self.prey_sight_on_pred = prey_sight_on_pred
        self.min_distance_between_prey = min_distance_between_prey

        self.schedule_Prey = RandomActivation(self)
        self.schedule_Predator = RandomActivation(self)
        self.food_schedule = RandomActivation(self)

        self.datacollector = PreyPredatorCollector()
        self.init_population(Prey, initial_prey)
        self.init_population(Predator, initial_predator)
        self.generate_grass_clusters(self.grass_clusters, self.grass_cluster_size)

        self.running = True
        self.datacollector.collect(self)

    def init_population(self, agent_type, n):
        '''
        Method that provides an easy way of making a bunch of agents at once.
        '''
        for i in range(n):
            x = random.randrange(self.space.width)
            y = random.randrange(self.space.height)

            self.new_agent(agent_type, (x, y))

    def generate_grass_clusters(self, n_clusters=8, cluster_size=100):
        for _ in range(n_clusters):
            cx = random.uniform(self.space.x_min, self.space.x_max)
            cy = random.uniform(self.space.y_min, self.space.y_max)
            for _ in range(cluster_size):
                angle = random.uniform(0, 360)
                distance = random.gauss(0, 50)
                pos = move_coordinates(cx, cy, angle, distance)

                fully_grown = random.choice([True, False])
                if fully_grown:
                    countdown = self.food_regrowth_time
                else:
                    countdown = random.randrange(self.food_regrowth_time)

                agent = Grass(self.next_id(), self, pos, fully_grown, countdown)
                self.space.place_agent(agent, pos)
                self.food_schedule.add(agent)

    def new_agent(self, agent_type, pos):
        '''
        Method that creates a new agent, and adds it to the correct scheduler.
        '''
        agent = agent_type(self.next_id(), self, pos)

        self.space.place_agent(agent, pos)
        getattr(self, f'schedule_{agent_type.__name__}').add(agent)

    def remove_agent(self, agent):
        '''
        Method that removes an agent from the space and the correct scheduler.
        '''
        self.space.remove_agent(agent)
        getattr(self, f'schedule_{type(agent).__name__}').remove(agent)

    def step(self):
        '''
        Method that calls the step method for each of the prey, and then for each of the predators.
        '''
        self.schedule_Prey.step()
        self.schedule_Predator.step()
        self.food_schedule.step()

        # Save the statistics
        self.datacollector.collect(self)

    def run_model(self, step_count=200):
        '''
        Method that runs the model for a specific amount of steps.
        '''
        for i in range(step_count):
            self.step()
