"""
Agent classes
=============

Contains agent classes which can be used in a model.

Death: agent used after animal dies, used for visualization.
Animal: base agent
Prey: extension to Animal implementing step function for prey
Predator: extension to Animal implementing step function for predators
Grass: agent used for environment and food sourch prey.
"""

import random
import numpy as np

from mesa import Agent

from utils import move_coordinates, heading_to_angle


class Death(Agent):
    """Death agent used after an animal has died.
    Only used for visualization purpose.
    """

    def __init__(self, unique_id, model, pos, animal_type):
        """Create a new death agent.

        Args:
            unique_id (int): A unique identifier for the agent
            model (Model): Instance of the model which contains the agent.
            pos (float, float): Coordinate tuple of the position of the agent.
            animal_type (Animal): Animal type which died.
        """
        super().__init__(unique_id, model)
        self.animal_type = animal_type
        self.pos = pos
        self.duration = 0

    def step(self):
        """Performs single time step for death agent.
        Removes agent if it exists for more than 10 time steps.
        """
        self.duration += 1
        if self.duration > 10:
            self.model.remove_agent(self)


class Animal(Agent):
    """Animal base class. """

    def __init__(self, unique_id, model, pos):
        """Create a new animal agent.

        Args:
            unique_id (int): A unique identifier for the agent
            model (Model): Instance of the model which contains the agent.
            pos (float, float): Coordinate tuple of the position of the agent.
        """
        super().__init__(unique_id, model)
        self.pos = pos

    def directed_move(self, direction, distance=25):
        """Moves the animal towards a new position.

        Args:
            direction (float): angle in degrees
            distance (float): Distance to move in direction
        """
        x, y = self.pos
        new_pos = move_coordinates(x, y, direction, distance)
        self.model.space.move_agent(self, new_pos)

    def random_move(self, max_distance=25):
        """Moves the animal randomly.

        Args:
            max_distance (float): max distance to be travelled.
        """
        distance = random.uniform(0, max_distance)
        direction = random.uniform(0, 360)
        self.directed_move(direction, distance)

    def reproduce(self):
        """Add new animal agent to the model. """
        self.model.new_agent(self.__class__, self.pos)

    def die(self):
        """Removes animal agent from the model and creates a new death agent. """
        self.model.new_agent(Death, self.pos, self.__class__.__name__)
        self.model.remove_agent(self)

    def get_neighbors(self, radius, agent_type=None):
        """Returns the neighbors for an animal present within a radius.
        If agent_type is given, only returns corresponding neighbors.

        Args:
            radius (float): get all objects within this distance of the center.
            agent_type (Agent): agent type to return.
        """
        if agent_type is None:
            return self.model.space.get_neighbors(self.pos, radius)
        else:
            return self.model.space.get_agent_neighbors(self.pos, agent_type, radius)

    def get_vector(self, agent_type, radius=25, grass=False):
        """Return mean vector of all agents of agent_type within distance
        of the agent.

        Args:
            agent_type (Agent): agent type to match.
            radius (float): get all agents within this distance of the center.
        """
        if grass:
            agents = self.get_neighbors(radius, agent_type)
            fully_grown = [agent for agent in agents if agent.fully_grown]
            return self.model.space.get_heading_to_agents(self.pos, fully_grown)
        return self.model.space.get_vector_to_agents(self.pos, agent_type, radius)


class Prey(Animal):
    """ Prey class: extends Animal class with step function designed to
    immitate prey animals.
    """

    def __init__(self, unique_id, model, pos):
        """Create a new Prey agent.

        Args:
            unique_id (int): A unique identifier for the agent
            model (Model): Instance of the model which contains the prey.
            pos (float, float): Coordinate tuple of the position of the prey.
        """
        super().__init__(unique_id, model, pos)
        self.energy = 2*self.model.prey_gain_from_food

    def step(self):
        """Perform a single time step for prey agent. """

        # Seperate vector from other prey.
        seperate_vector_prey = self.get_vector(Prey, self.model.prey_reach)

        # Seperate vector from predators.
        seperate_vector_predators = self.get_vector(
            Predator, self.model.prey_sight)

        # Coherence vector towards other prey.
        cohere_vector = self.get_vector(Prey, self.model.prey_sight)

        fully_grown_grass = [grass for grass in self.get_neighbors(
            self.model.prey_reach, Grass) if grass.fully_grown]

        # Food vector towards grass which is fully grown.
        # Zero when already on grass or energy level sufficiently high.
        if self.energy < self.model.prey_food_search_max and not fully_grown_grass:
            hungry_vector = self.get_vector(Grass, self.model.prey_sight, True)
        else:
            hungry_vector = np.zeros(2)

        # Result vecor calculated from the four vectors calculated above,
        # multiplied with specific factors.
        result_vector = \
            -1 * self.model.prey_separate_factor * seperate_vector_prey + \
            -1 * self.model.prey_separate_predators_factor * seperate_vector_predators + \
            self.model.prey_cohere_factor * cohere_vector + \
            self.model.prey_hungry_factor * hungry_vector

        # Move randomly when result vector is zero.
        # Else move towards calculated heading.
        if not np.any(result_vector):
            self.random_move()
        else:
            self.directed_move(heading_to_angle(result_vector[0],
                                                result_vector[1]))

        # Reproduce randomly when energy level is sufficient.
        if self.energy > self.model.prey_reproduction_min and random.random() < self.model.prey_reproduction_chance:
            self.reproduce()

        self.energy -= 1

        # If present, eat one patch of fully grown grass.
        if len(fully_grown_grass) > 0:
            self.energy += self.model.prey_gain_from_food
            random.choice(fully_grown_grass).eaten()

        # Die randomly or when energy level lower than zero.
        if self.energy < 0 or random.random() < self.model.prey_death_chance:
            self.die()


class Predator(Animal):
    """ Predator class: extends Animal class with step function designed to
    immitate predator animals.
    """

    def __init__(self, unique_id, model, pos):
        """Create a new Predator agent.

        Args:
            unique_id (int): A unique identifier for the agent
            model (Model): Instance of the model which contains the predator.
            pos (float, float): Coordinate tuple of the position of the predator.
        """
        super().__init__(unique_id, model, pos)
        self.energy = 2*self.model.predator_gain_from_food

    def step(self):
        """Perform a single time step for predator agent. """

        # If energy is low enough, move towards prey if any in neighborhoud.
        # Else move randomly.
        if self.energy < self.model.predator_food_search_max:
            towards_prey = self.get_vector(Prey, self.model.predator_sight)
            if not np.any(towards_prey):
                self.random_move()
            else:
                self.directed_move(heading_to_angle(
                    towards_prey[0], towards_prey[1]))
        else:
            self.random_move()

        # Get list with prey on location with less than 5 other prey
        # surrounding it. Eat only first prey in the list.
        prey_on_location = self.get_neighbors(self.model.predator_reach, Prey)
        lonely_prey = filter(lambda p: len(p.get_neighbors(
            self.model.predator_reach, Prey)) < 5, prey_on_location)
        for prey in lonely_prey:
            prey.die()
            self.energy += self.model.predator_gain_from_food
            break

        # Reproduce randomly when energy level is sufficient.
        if self.energy > self.model.predator_reproduction_min and random.random() < self.model.predator_reproduction_chance:
            self.reproduce()

        self.energy -= 1

        # Die randomly or when energy level lower than zero.
        if self.energy < 0 or random.random() < self.model.predator_death_chance:
            self.die()


class Grass(Agent):
    """ Grass class: agent designed to be eaten after which it will regrow. """

    def __init__(self, unique_id, model, pos, fully_grown, countdown):
        """Create one patch of grass.

        Args:
            unique_id (int): A unique identifier for the agent
            model (Model): Instance of the model which contains the grass.
            pos (float, float): Coordinate tuple of the position of the grass patch.
            fully_grown (bool): Boolean if grass if fully grown.
            countdown (int): Counter in how many timesteps grass will be fully grown.
        """
        super().__init__(unique_id, model)
        self.fully_grown = fully_grown
        self.countdown = countdown
        self.pos = pos

    def step(self):
        """Perform a single time step for grass. """
        if not self.fully_grown:
            if self.countdown <= 0:
                self.fully_grown = True
                self.countdown = self.model.food_regrowth_time
            else:
                self.countdown -= 1

    def eaten(self):
        """Set grass to eaten. """
        self.fully_grown = False
