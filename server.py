from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

from model import PreyPredatorModel

# You can change this to whatever ou want. Make sure to make the different types
# of agents distinguishable
def agent_portrayal(agent):
    return {
        'Shape': 'circle',
        'Color': 'blue' if agent.__class__.__name__ == 'Prey' else 'red',
        'Filled': 'true',
        'Layer': 0,
        'r': 0.5
    }

# Create a grid of 20 by 20 cells, and display it as 500 by 500 pixels
grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500)

# Create a dynamic linegraph
chart = ChartModule([{
    'Label': 'Prey',
    'Color': 'blue'
}, {
    'Label': 'Predators',
    'Color': 'red'
}], data_collector_name='datacollector')

model_params = {
    'initial_prey': UserSettableParameter('slider', 'Initial Prey', 100, 10, 300),
    'initial_predator': UserSettableParameter('slider', 'Initial Predator', 30, 10, 300),
    'prey_reproduction_chance': UserSettableParameter('slider', 'Prey reproduction chance', 0.05, 0.01, 1.0, 0.01),
    'predator_death_chance': UserSettableParameter('slider', 'Predator death chance', 0.05, 0.01, 1.0, 0.01)
}

# Create the server, and pass the grid and the graph
server = ModularServer(PreyPredatorModel, [grid, chart], 'Prey-Predator Model', model_params)
