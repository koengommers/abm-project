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

    def die(self):
        self.model.remove_agent(self)

    def on_location(self, agent_type=None):
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        if agent_type is None:
            return this_cell
        else:
            return [agent for agent in this_cell if isinstance(agent, agent_type)]

class Prey(Animal):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)
        self.energy = 2*self.model.prey_gain_from_food

    def step(self):
        self.random_move()
        if random.random() < self.model.prey_reproduction_chance:
            self.reproduce()

        self.energy -= 1

        grass = self.on_location(Grass)[0]
        if grass.fully_grown:
            self.energy += self.model.prey_gain_from_food
            grass.eaten()

        if self.energy < 0:
            self.die()

class Predator(Animal):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)
        self.energy = 2*self.model.predator_gain_from_food

    def step(self):
        self.random_move()

        prey_on_location = self.on_location(Prey)
        for prey in prey_on_location:
            prey.die()
            self.energy += self.model.predator_gain_from_food
            self.reproduce()
            break

        self.energy -= 1

        if self.energy < 0 or random.random() < self.model.predator_death_chance:
            self.die()

class Grass(Agent):
    def __init__(self, unique_id, model, pos, fully_grown, countdown):
        super().__init__(unique_id, model)
        self.fully_grown = fully_grown
        self.countdown = countdown
        self.pos = pos

    def step(self):
        if not self.fully_grown:
            if self.countdown <= 0:
                self.fully_grown = True
                self.countdown = self.model.food_regrowth_time
            else:
                self.countdown -= 1

    def eaten(self):
        self.fully_grown = False

