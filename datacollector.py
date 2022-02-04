"""
The collector class used in this project.

Core class: PreyPredatorCollector

"""
import numpy as np

from mesa.datacollection import DataCollector

def get_average_energy(animal):
    """Returns average energy of a type of animal. """
    def calc_average_energy(model):
        """Calculates and return average energy. """
        agents = getattr(model, f'schedule_{animal}').agents
        if len(agents) > 0:
            return np.mean([agent.energy for agent in agents])
        else:
            return 0
    return calc_average_energy

class PreyPredatorCollector(DataCollector):
    """Prey-predator collector class extending DataCollector """

    def __init__(self, **params):
        """Create model reporter which collect animal count and average energy. """
        model_reporters = {
            'Prey': lambda m: m.schedule_Prey.get_agent_count(),
            'Predators': lambda m: m.schedule_Predator.get_agent_count(),
            'Prey energy': get_average_energy('Prey'),
            'Predator energy': get_average_energy('Predator'),
        }
        super().__init__(model_reporters, **params)
