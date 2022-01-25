from mesa import Agent
import random
from utils import move_coordinates, heading_to_angle
import numpy as np

class Animal(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)

        self.pos = pos

    def random_move(self, max_distance=25, max_turn=10):
        distance = random.uniform(0, max_distance)
        self.direction = random.uniform(0, 360)
        x, y = self.pos
        new_pos = move_coordinates(x, y, self.direction, distance)
        self.model.space.move_agent(self, new_pos)

    def directed_move(self, direction, min_distance=0, max_distance=25):
        distance = random.uniform(min_distance, max_distance)
        x, y = self.pos
        new_pos = move_coordinates(x, y, direction, distance)
        self.model.space.move_agent(self, new_pos)

    def reproduce(self):
        self.model.new_agent(self.__class__, self.pos)

    def die(self):
        self.model.remove_agent(self)

    def on_location(self, agent_type=None, radius=10):
        neighbors = self.model.space.get_neighbors(self.pos, radius)
        if agent_type is None:
            return neighbors
        else:
            return [agent for agent in neighbors if isinstance(agent, agent_type)]

class Prey(Animal):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)
        self.energy = 2*self.model.prey_gain_from_food

    def get_vector(self, agent_type, distance=25, direction=1, grass=False):
        if grass:
            agents = self.model.space.get_agent_neighbors(self.pos, agent_type, distance)
            fully_grown = [agent for agent in agents if agent.fully_grown]
            return direction * self.model.space.get_heading_to_agents(self.pos, fully_grown)
        return direction * self.model.space.get_vector_to_agents(self.pos, agent_type, distance)

    def step(self):
        # Seperate: Don't get to close to other prey, TODO: might massively slow down program when herd is big
        seperate_vector_prey = self.get_vector(Prey, self.model.min_distance_between_prey, -1)

        # Seperate: move away from predators
        seperate_vector_predators = self.get_vector(Predator, self.model.prey_sight_on_pred, -1)

        # Move towards other prey in area, TODO: might massively slow down program when herd is big
        cohere_vector = self.get_vector(Prey, 25)
        # Move towards grass, only call/use when energy below certain value
        if self.energy < 40: #?
            hungry_vector = self.get_vector(Grass, 25, grass=True)
        else:
            hungry_vector = np.zeros(2)

        # TODO: Tweak with multiplication factors
        result_vecor = 1 * seperate_vector_prey + \
                       1 * seperate_vector_predators + \
                       1 * cohere_vector + \
                       1 * hungry_vector

        if not np.any(result_vecor):
            self.random_move()
        else:
            self.directed_move(heading_to_angle(result_vecor[0], result_vecor[1]))

        if random.random() < self.model.prey_reproduction_chance:
            self.reproduce()

        self.energy -= 1

        fully_grown_grass = [grass for grass in self.on_location(Grass) if grass.fully_grown]
        if len(fully_grown_grass) > 0:
            self.energy += self.model.prey_gain_from_food
            random.choice(fully_grown_grass).eaten()

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
