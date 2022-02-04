"""
Launches server for visualization of the model with population and energy charts.
"""

import math

from mesa.visualization.modules import ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

from agents import Death, Prey, Predator, Grass
from model import PreyPredatorModel
from visualization import CanvasContinuous

def animal_portrayal(color):
    """Returns visualization properties of animals. """
    return {
        'Shape': 'circleWithTrail',
        'Color': color,
        'Filled': 'true',
        'Layer': 2,
        'r': 5,
        's': 2
    }

def agent_portrayal(agent):
    """Returns visualization properties of agents. """
    if isinstance(agent, Death):
        opacity = (10 - agent.duration)/10
        rgb = '237, 58, 28' if agent.animal_type == 'Predator' else '0, 24, 248'
        return {
            'Shape': 'cross',
            'Color': f'rgba({rgb}, {opacity})',
            'Filled': 'true',
            'Layer': 1,
            'r': 5,
            's': 2
        }
    elif isinstance(agent, Prey):
        return animal_portrayal('blue')
    elif isinstance(agent, Predator):
        return animal_portrayal('red')
    elif isinstance(agent, Grass):
        if agent.fully_grown:
            color = 'rgb(0, 150, 0)'
        else:
            growth_time = agent.model.food_regrowth_time
            opacity = (growth_time-agent.countdown)/growth_time
            color = f'rgba(0, 150, 0, {opacity})'
        return {
            'Shape': 'circle',
            'Color': color,
            'Filled': 'true',
            'Layer': 0,
            'r': 10
        }

# Create a 500 by 500 pixels canvas for the space
grid = CanvasContinuous(agent_portrayal, 500, 500)

# Create a dynamic linegraph
population_chart = ChartModule([{
    'Label': 'Prey',
    'Color': 'blue'
}, {
    'Label': 'Predators',
    'Color': 'red'
}], data_collector_name='datacollector')

energy_chart = ChartModule([{
    'Label': 'Prey energy',
    'Color': 'blue'
}, {
    'Label': 'Predator energy',
    'Color': 'red'
}], data_collector_name='datacollector')

model_params = {
    'grass_clusters': UserSettableParameter('slider', 'Grass clusters', 15, 1, 50),
    'grass_cluster_size': UserSettableParameter('slider', 'Grass cluster size', 400, 10, 1000, 10),
    'food_regrowth_time': UserSettableParameter('slider', 'Food regrowth time', 30, 1, 50),
    'initial_prey': UserSettableParameter('slider', 'Initial Prey', 100, 10, 300),
    'prey_gain_from_food': UserSettableParameter('slider', 'Prey gain from food', 10, 1, 50),
    'prey_reproduction_chance': UserSettableParameter('slider', 'Prey reproduction chance', 0.05, 0.01, 1.0, 0.01),
    'prey_death_chance': UserSettableParameter('slider', 'Prey death chance', 0, 0.01, 1.0, 0.01),
    'prey_reproduction_min': UserSettableParameter('slider', 'Prey reproduction minimum', 40, 0, 100),
    'prey_food_search_max': UserSettableParameter('slider', 'Prey food search maximum', 40, 0, 100),
    'prey_sight': UserSettableParameter('slider', 'Prey sight', 25, 0, 100),
    'prey_reach': UserSettableParameter('slider', 'Prey reach', 10, 0, 50),
    'prey_cohere_factor': UserSettableParameter('number', 'Prey cohere factor', 1),
    'prey_separate_factor': UserSettableParameter('number', 'Prey separate factor', 1),
    'prey_separate_predators_factor': UserSettableParameter('number', 'Prey separate from separate factor', 1),
    'prey_hungry_factor': UserSettableParameter('number', 'Prey hungry factor', 1),
    'initial_predator': UserSettableParameter('slider', 'Initial Predator', 20, 10, 300),
    'predator_gain_from_food': UserSettableParameter('slider', 'Predator gain from food', 30, 1, 50),
    'predator_reproduction_chance': UserSettableParameter('slider', 'Predator reproduction chance', 0.05, 0.01, 1.0, 0.01),
    'predator_death_chance': UserSettableParameter('slider', 'Predator death chance', 0.05, 0.01, 1.0, 0.01),
    'predator_reproduction_min': UserSettableParameter('slider', 'Predator reproduction minimum', 20, 0, 50),
    'predator_food_search_max': UserSettableParameter('slider', 'Predator food search maximum', 40, 0, 100),
    'predator_sight': UserSettableParameter('slider', 'Predator sight', 50, 0, 100),
    'predator_reach': UserSettableParameter('slider', 'Predator reach', 25, 0, 50),
}

# Create the server, and pass the grid and the graph
server = ModularServer(PreyPredatorModel, [grid, population_chart, energy_chart], 'Prey-Predator Model', model_params)
