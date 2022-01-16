from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule

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

model_params = {}

# Create the server, and pass the grid and the graph
server = ModularServer(PreyPredatorModel, [grid, chart], 'Prey-Predator Model', model_params)
