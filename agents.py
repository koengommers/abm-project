from mesa import Agent
import random
from utils import move_coordinates, heading_to_angle
import numpy as np

class Death(Agent):
    def __init__(self, unique_id, model, pos, animal_type):
        super().__init__(unique_id, model)
        self.animal_type = animal_type
        self.pos = pos
        self.duration = 0

    def step(self):
        self.duration += 1
        if self.duration > 10:
            self.model.remove_agent(self)

class Animal(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)

        self.pos = pos

    def random_move(self, max_distance=25):
        distance = random.uniform(0, max_distance)
        direction = random.uniform(0, 360)
        x, y = self.pos
        new_pos = move_coordinates(x, y, direction, distance)
        self.model.space.move_agent(self, new_pos)

    def directed_move(self, direction, min_distance=0, max_distance=25):
        distance = random.uniform(min_distance, max_distance)
        x, y = self.pos
        new_pos = move_coordinates(x, y, direction, distance)
        self.model.space.move_agent(self, new_pos)

    def reproduce(self):
        self.model.new_agent(self.__class__, self.pos)

    def die(self):
        self.model.new_agent(Death, self.pos, self.__class__.__name__)
        self.model.remove_agent(self)

    def on_location(self, agent_type=None, radius=25):
        neighbors = self.model.space.get_neighbors(self.pos, radius)
        if agent_type is None:
            return neighbors
        else:
            return [agent for agent in neighbors if isinstance(agent, agent_type)]

    def get_vector(self, agent_type, distance=25, grass=False):
        if grass:
            agents = self.model.space.get_agent_neighbors(self.pos, agent_type, distance)
            fully_grown = [agent for agent in agents if agent.fully_grown]
            return self.model.space.get_heading_to_agents(self.pos, fully_grown)
        return self.model.space.get_vector_to_agents(self.pos, agent_type, distance)

class Prey(Animal):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)
        self.energy = 2*self.model.prey_gain_from_food

    def step(self):
        # Seperate: Don't get to close to other prey
        seperate_vector_prey = self.get_vector(Prey, self.model.prey_sight)

        # Seperate: move away from predators
        seperate_vector_predators = self.get_vector(Predator, self.model.prey_sight)

        # Move towards other prey in area
        cohere_vector = self.get_vector(Prey, self.model.prey_sight)

        # Move towards grass, only call/use when energy below certain value and no grass on locaton.
        fully_grown_grass = [grass for grass in self.on_location(Grass, self.model.prey_reach) if grass.fully_grown]
        if self.energy < self.model.prey_food_search_max and not fully_grown_grass: #This can probably be done better
            hungry_vector = self.get_vector(Grass, self.model.prey_sight, True)
        else:
            hungry_vector = np.zeros(2)

        # TODO: Tweak with multiplication factors
        result_vector = -1 * self.model.prey_separate_factor * seperate_vector_prey + \
                       -1 * self.model.prey_separate_predators_factor * seperate_vector_predators + \
                       self.model.prey_cohere_factor * cohere_vector + \
                       self.model.prey_hungry_factor * hungry_vector

        if not np.any(result_vector):
            self.random_move()
        else:
            self.directed_move(heading_to_angle(result_vector[0], result_vector[1]))

        if self.energy > self.model.prey_reproduction_min and random.random() < self.model.prey_reproduction_chance:
            self.reproduce()

        self.energy -= 1

        if len(fully_grown_grass) > 0:
            self.energy += self.model.prey_gain_from_food
            random.choice(fully_grown_grass).eaten()

        if self.energy < 0 or random.random() < self.model.prey_death_chance:
            self.die()

class Predator(Animal):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)
        self.energy = 2*self.model.predator_gain_from_food

    def step(self):
        if self.energy < self.model.predator_food_search_max:
            towards_prey = self.get_vector(Prey, self.model.predator_sight)
            if not np.any(towards_prey):
                self.random_move()
            else:
                self.directed_move(heading_to_angle(towards_prey[0], towards_prey[1]))
        else:
            self.random_move()

        prey_on_location = self.on_location(Prey)
        sorted_prey = sorted(prey_on_location, key=lambda p: len(p.on_location(Prey, self.model.predator_reach)))
        for prey in sorted_prey:
            prey.die()
            self.energy += self.model.predator_gain_from_food
            break

        if self.energy > self.model.predator_reproduction_min and random.random() < self.model.predator_reproduction_chance:
            self.reproduce()

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
