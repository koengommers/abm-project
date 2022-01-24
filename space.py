from collections import defaultdict
import numpy as np
from mesa.space import ContinuousSpace

class OptimizedContinuousSpace(ContinuousSpace):
    def __init__(self, x_max, y_max, torus, x_min=0, y_min=0):
        super().__init__(x_max, y_max, torus, x_min, y_min)
        self._type_to_indices = defaultdict(list)

    def place_agent(self, agent, pos):
        super().place_agent(agent, pos)
        index = self._agent_points.shape[0] - 1
        self._type_to_indices[agent.__class__.__name__].append(index)

    def remove_agent(self, agent):
        idx = self._agent_to_index[agent]
        self._type_to_indices[agent.__class__.__name__].remove(idx)
        super().remove_agent(agent)
        for t in self._type_to_indices:
            for i, index in enumerate(self._type_to_indices[t]):
                if index > idx:
                    self._type_to_indices[t][i] -= 1

    def get_vector_to_agents(self, pos, agent_type, radius):
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

        # calculate vector
        if self.torus:
            pos = (pos - self.center) % self.size
            in_radius = (in_radius - self.center) % self.size

        vectors = in_radius - pos
        return np.sum(vectors, axis=0)
