from mesa import Agent
import random

class Animal(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)

        self.pos = pos

    def random_move(self):
        neighbors = self.model.grid.get_neighborhood(self.pos, moore=True)
        self.model.grid.move_agent(self, random.choice(neighbors))

    def reproduce(self):
        self.model.new_agent(self.__class__, self.pos)

class Prey(Animal):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)

    def step(self):
        self.random_move()
        if random.random() < self.model.prey_reproduction_chance:
            self.reproduce()

class Predator(Animal):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)

    def step(self):
        self.random_move()
        on_location = self.model.grid.get_neighbors(self.pos, moore=True, include_center=True, radius=0)
        for agent in on_location:
            if isinstance(agent, Prey):
                self.model.remove_agent(agent)
                self.reproduce()
                break

        if random.random() < self.model.predator_death_chance:
            self.model.remove_agent(self)
