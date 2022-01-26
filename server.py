import math
from mesa.visualization.modules import ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

from model import PreyPredatorModel
from agents import Death, Prey, Predator, Grass
from visualization import CanvasContinuous

def animal_portrayal(color):
    return {
        'Shape': 'circleWithTrail',
        'Color': color,
        'Filled': 'true',
        'Layer': 2,
        'r': 5,
        's': 2
    }

# You can change this to whatever ou want. Make sure to make the different types
# of agents distinguishable
def agent_portrayal(agent):
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
    'initial_prey': UserSettableParameter('slider', 'Initial Prey', 100, 10, 300),
    'initial_predator': UserSettableParameter('slider', 'Initial Predator', 20, 10, 300),
    'prey_reproduction_chance': UserSettableParameter('slider', 'Prey reproduction chance', 0.05, 0.01, 1.0, 0.01),
    'predator_death_chance': UserSettableParameter('slider', 'Predator death chance', 0.05, 0.01, 1.0, 0.01),
    'food_regrowth_time': UserSettableParameter('slider', 'Food regrowth time', 30, 1, 50),
    'prey_gain_from_food': UserSettableParameter('slider', 'Prey gain from food', 10, 1, 50),
    'predator_gain_from_food': UserSettableParameter('slider', 'Predator gain from food', 30, 1, 50),
    'grass_clusters': UserSettableParameter('slider', 'Grass clusters', 15, 1, 50),
    'grass_cluster_size': UserSettableParameter('slider', 'Grass cluster size', 400, 10, 1000, 10),
    'prey_sight_on_pred': UserSettableParameter('slider', 'Prey sight to Predators', 25, 10, 50),
    'min_distance_between_prey': UserSettableParameter('slider', 'Min distance between prey', 18, 10, 50),
}

# Create the server, and pass the grid and the graph
server = ModularServer(PreyPredatorModel, [grid, population_chart, energy_chart], 'Prey-Predator Model', model_params)
