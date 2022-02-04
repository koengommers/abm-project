"""
Space class

Core class: OptimizedContinuousSpace

"""

from collections import defaultdict
import numpy as np

from mesa.space import ContinuousSpace


class OptimizedContinuousSpace(ContinuousSpace):
    """Extends ContinuousSpace for better efficiency using numpy """

    def __init__(self, x_max, y_max, torus, x_min=0, y_min=0):
        """Create new space. """
        super().__init__(x_max, y_max, torus, x_min, y_min)
        self._type_to_indices = defaultdict(list)

    def place_agent(self, agent, pos):
        """Place a new agent in the space. """
        super().place_agent(agent, pos)
        agent.last_pos = pos
        index = self._agent_points.shape[0] - 1
        self._type_to_indices[agent.__class__.__name__].append(index)

    def move_agent(self, agent, pos):
         """Move an agent from its current position to a new position. """
         agent.last_pos = agent.pos
         super().move_agent(agent, pos)

    def remove_agent(self, agent):
        """Remove an agent from the simulation. """
        idx = self._agent_to_index[agent]
        self._type_to_indices[agent.__class__.__name__].remove(idx)
        super().remove_agent(agent)
        for t in self._type_to_indices:
            for i, index in enumerate(self._type_to_indices[t]):
                if index > idx:
                    self._type_to_indices[t][i] -= 1

    def calculate_heading(self, pos, points):
        """ Calculate vector from list of points. """
        if self.torus:
            pos = (pos - self.center) % self.size
            points = (points - self.center) % self.size

        vectors = points - pos
        return np.sum(vectors, axis=0)

    def get_vector_to_agents(self, pos, agent_type, radius):
        """ Calculate vector from parameters agent type and a radius. """
        # get points of agent type
        agent_type_indices = self._type_to_indices[agent_type.__name__]
        points_of_type = self._agent_points[agent_type_indices]

        # get points within radius
        pos = np.array(pos)
        deltas = np.abs(points_of_type - pos)
        if self.torus:
            deltas = np.minimum(deltas, self.size - deltas)
        dists = deltas[:, 0] ** 2 + deltas[:, 1] ** 2
        (idxs,) = np.where(dists <= radius ** 2)
        in_radius = points_of_type[idxs]
        heading = self.calculate_heading(pos, in_radius)
        norm = np.linalg.norm(heading)
        if norm:
            return heading / norm
        return heading

    def get_agent_neighbors(self, pos, agent_type, radius):
        """ Get list of agents of a certain agent type and within a radius. """
        # get points of agent type
        agent_type_indices = self._type_to_indices[agent_type.__name__]
        points_of_type = self._agent_points[agent_type_indices]

        # get points within radius
        pos = np.array(pos)
        deltas = np.abs(points_of_type - pos)
        if self.torus:
            deltas = np.minimum(deltas, self.size - deltas)
        dists = deltas[:, 0] ** 2 + deltas[:, 1] ** 2
        (idxs,) = np.where(dists <= radius ** 2)
        return [self._index_to_agent[i] for i in np.array(agent_type_indices)[idxs]]

    def get_heading_to_agents(self, pos, agents):
        """ Calculate vector from a list of agents """
        agent_indices = [self._agent_to_index[agent] for agent in agents]
        points = self._agent_points[agent_indices]
        return self.calculate_heading(np.array(pos), points)
