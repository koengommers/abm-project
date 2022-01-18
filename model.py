import random
from mesa import Model
from mesa.space import ContinuousSpace
from mesa.time import RandomActivation
from agents import Prey, Predator, Grass
from datacollector import PreyPredatorCollector

class PreyPredatorModel(Model):
    def __init__(self, width=500, height=500,
                 initial_prey=100, initial_predator=30,
                 prey_reproduction_chance=0.05, predator_death_chance=0.05,
                 prey_gain_from_food=4, predator_gain_from_food=20, food_regrowth_time=30):

        super().__init__()
        self.space = ContinuousSpace(width, height, torus=True)
        
        self.prey_reproduction_chance = prey_reproduction_chance
        self.predator_death_chance = predator_death_chance

        self.prey_gain_from_food = prey_gain_from_food
        self.predator_gain_from_food = predator_gain_from_food
        self.food_regrowth_time = food_regrowth_time

        self.schedule_Prey = RandomActivation(self)
        self.schedule_Predator = RandomActivation(self)
        self.food_schedule = RandomActivation(self)

        self.datacollector = PreyPredatorCollector()
        self.init_population(Prey, initial_prey)
        self.init_population(Predator, initial_predator)
        # self.init_food()

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

    # def init_food(self):
    #     for _, x, y in self.grid.coord_iter():
    #         fully_grown = random.choice([True, False])
    #
    #         if fully_grown:
    #             countdown = self.food_regrowth_time
    #         else:
    #             countdown = random.randrange(self.food_regrowth_time)
    #
    #         agent = Grass(self.next_id(), self, (x, y), fully_grown, countdown)
    #         self.grid.place_agent(agent, (x, y))
    #         self.food_schedule.add(agent)

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
