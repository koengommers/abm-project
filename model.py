"""
The model class used in this project.

Core class: PreyPredatorModel

"""

import random

from mesa import Model
from mesa.time import BaseScheduler, RandomActivation

from agents import Prey, Predator, Grass
from datacollector import PreyPredatorCollector
from space import OptimizedContinuousSpace
from utils import move_coordinates


class PreyPredatorModel(Model):
    """Prey-Pretor model class. """

    def __init__(self, width=500, height=500, collect_data=True,
                 initial_prey=100, initial_predator=20,
                 grass_clusters=8, grass_cluster_size=60, food_regrowth_time=30,
                 prey_gain_from_food=10,
                 prey_reproduction_chance=0.05, prey_death_chance=0,
                 prey_reproduction_min=20, prey_food_search_max=40,
                 prey_sight=40, prey_reach=10,
                 prey_cohere_factor=1, prey_separate_factor=1, prey_separate_predators_factor=1,
                 prey_hungry_factor=1,
                 predator_gain_from_food=20,
                 predator_reproduction_chance=0.05, predator_death_chance=0.02,
                 predator_reproduction_min=40, predator_food_search_max=40,
                 predator_sight=40, predator_reach=25):
        """Create new model with given parameters.
        Initializes agents and schedulers. """

        super().__init__()
        self.space = OptimizedContinuousSpace(width, height, torus=True)

        self.grass_clusters = grass_clusters
        self.grass_cluster_size = grass_cluster_size
        self.food_regrowth_time = food_regrowth_time

        self.prey_gain_from_food = prey_gain_from_food
        self.prey_reproduction_chance = prey_reproduction_chance
        self.prey_death_chance = prey_death_chance
        self.prey_reproduction_min = prey_reproduction_min
        self.prey_food_search_max = prey_food_search_max
        self.prey_sight = prey_sight
        self.prey_reach = prey_reach

        self.prey_cohere_factor = prey_cohere_factor
        self.prey_separate_factor = prey_separate_factor
        self.prey_separate_predators_factor = prey_separate_predators_factor
        self.prey_hungry_factor = prey_hungry_factor

        self.predator_gain_from_food = predator_gain_from_food
        self.predator_reproduction_chance = predator_reproduction_chance
        self.predator_death_chance = predator_death_chance
        self.predator_reproduction_min = predator_reproduction_min
        self.predator_food_search_max = predator_food_search_max
        self.predator_sight = predator_sight
        self.predator_reach = predator_reach

        self.schedule_Prey = RandomActivation(self)
        self.schedule_Predator = RandomActivation(self)
        self.schedule_Death = RandomActivation(self)
        self.food_schedule = RandomActivation(self)
        self.schedule = BaseScheduler(self)

        self.collect_data = collect_data
        if self.collect_data:
            self.datacollector = PreyPredatorCollector()
        self.init_population(Prey, initial_prey)
        self.init_population(Predator, initial_predator)
        self.generate_grass_clusters(
            self.grass_clusters, self.grass_cluster_size)

        self.running = True
        if self.collect_data:
            self.datacollector.collect(self)

    def init_population(self, agent_type, n):
        """Method that provides an easy way of making a bunch of agents at once. """
        for i in range(n):
            x = random.randrange(self.space.width)
            y = random.randrange(self.space.height)

            self.new_agent(agent_type, (x, y))

    def generate_grass_clusters(self, n_clusters=8, cluster_size=100):
        """Generate given amount of grass clusters. Uses gaussian distribution
        to sample grass around initial grass position.
        """
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

    def new_agent(self, agent_type, pos, *args):
        """Method that creates a new agent, and adds it to the correct scheduler. """
        agent = agent_type(self.next_id(), self, pos, *args)

        self.space.place_agent(agent, pos)
        getattr(self, f'schedule_{agent_type.__name__}').add(agent)

    def remove_agent(self, agent):
        """Method that removes an agent from the space and the correct scheduler. """
        self.space.remove_agent(agent)
        getattr(self, f'schedule_{type(agent).__name__}').remove(agent)

    def step(self):
        """Method that calls the step method for each of the agent types.
        """
        self.schedule_Prey.step()
        self.schedule_Predator.step()
        self.schedule_Death.step()
        self.food_schedule.step()
        self.schedule.step()

        # Save the statistics
        if self.collect_data:
            self.datacollector.collect(self)

        if (self.schedule_Predator.get_agent_count() == 0 or
                self.schedule_Prey.get_agent_count() == 0):
            self.running = False

    def run_model(self, step_count=200):
        """Method that runs the model for a specific amount of steps. """
        for i in range(step_count):
            self.step()
