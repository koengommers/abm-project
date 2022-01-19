from mesa import Agent
import random
from utils import move_coordinates

class Animal(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)

        self.pos = pos
        self.direction = random.uniform(0, 360)

    def random_move(self, max_distance=20, directed=True, max_turn=10):
        distance = random.uniform(0, max_distance)
        if directed:
            self.direction += random.uniform(-max_turn, max_turn)
        else:
            self.direction = random.uniform(0, 360)
        x, y = self.pos
        new_pos = move_coordinates(x, y, self.direction, distance)
        self.model.space.move_agent(self, new_pos)

    def directed_move(self, direction, max_distance=20):
        distance = random.uniform(0, max_distance)
        self.direction = direction
        x, y = self.pos
        new_pos = move_coordinates(x, y, self.direction, distance)
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

    def step(self):
        in_sight = self.model.space.get_neighbors(self.pos, radius=20)
        grass_in_sight = [grass for grass in in_sight if isinstance(grass, Grass) and grass.fully_grown]
        if grass_in_sight:
            self.model.space.move_agent(self, random.choice(grass_in_sight).pos)
        else:
            self.random_move(directed=True)
        #self.random_move()
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
