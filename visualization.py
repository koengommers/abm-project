from collections import defaultdict
from mesa.visualization.ModularVisualization import VisualizationElement

class CanvasContinuous(VisualizationElement):
    local_includes = ['js/CanvasContinuousModule.js', 'js/ContinuousVisualization.js']
    
    def __init__(
        self,
        portrayal_method,
        canvas_width=500,
        canvas_height=500,
    ):
        self.portrayal_method = portrayal_method
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        new_element = 'new CanvasContinuousModule({}, {})'.format(
            self.canvas_width, self.canvas_height
        )
        
        self.js_code = 'elements.push(' + new_element + ');'

    def render(self, model):
        space_state = defaultdict(list)
        for agent in model.space._agent_to_index:
            portrayal = self.portrayal_method(agent)
            x, y = agent.pos
            x = (x - model.space.x_min) / (model.space.x_max - model.space.x_min)
            y = (y - model.space.y_min) / (model.space.y_max - model.space.y_min)
            portrayal['x'] = x
            portrayal['y'] = y
            if portrayal['Shape'] == 'circleWithTrail':
                fromx, fromy = agent.last_pos
                fromx = (fromx - model.space.x_min) / (model.space.x_max - model.space.x_min)
                fromy = (fromy - model.space.y_min) / (model.space.y_max - model.space.y_min)
                portrayal['fromx'] = fromx
                portrayal['fromy'] = fromy
            space_state[portrayal['Layer']].append(portrayal)
        return space_state
