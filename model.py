import random
from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
from agents import Prey, Predator

class PreyPredatorModel(Model):
    def __init__(self, width=20, height=20,
                 initial_prey=100, initial_predator=30,
                 prey_reproduction_chance=0.05, predator_death_chance=0.05):

        super().__init__()
        self.grid = MultiGrid(width, height, torus=True)
        
        self.prey_reproduction_chance = prey_reproduction_chance
        self.predator_death_chance = predator_death_chance

        self.schedule_Prey = RandomActivation(self)
        self.schedule_Predator = RandomActivation(self)

        self.datacollector = DataCollector({
            'Prey': lambda m: m.schedule_Prey.get_agent_count(),
            'Predators': lambda m: m.schedule_Predator.get_agent_count()
        })

        self.init_population(Prey, initial_prey)
        self.init_population(Predator, initial_predator)

        self.running = True
        self.datacollector.collect(self)

    def init_population(self, agent_type, n):
        '''
        Method that provides an easy way of making a bunch of agents at once.
        '''
        for i in range(n):
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)

            self.new_agent(agent_type, (x, y))

    def new_agent(self, agent_type, pos):
        '''
        Method that creates a new agent, and adds it to the correct scheduler.
        '''
        agent = agent_type(self.next_id(), self, pos)

        self.grid.place_agent(agent, pos)
        getattr(self, f'schedule_{agent_type.__name__}').add(agent)

    def remove_agent(self, agent):
        '''
        Method that removes an agent from the grid and the correct scheduler.
        '''
        self.grid.remove_agent(agent)
        getattr(self, f'schedule_{type(agent).__name__}').remove(agent)

    def step(self):
        '''
        Method that calls the step method for each of the prey, and then for each of the predators.
        '''
        self.schedule_Prey.step()
        self.schedule_Predator.step()

        # Save the statistics
        self.datacollector.collect(self)

    def run_model(self, step_count=200):
        '''
        Method that runs the model for a specific amount of steps.
        '''
        for i in range(step_count):
            self.step()
