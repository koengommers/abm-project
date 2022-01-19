import math

def move_coordinates(x, y, angle, distance):
    dx = distance*math.sin(math.radians(angle))
    dy = distance*math.cos(math.radians(angle))
    return x + dx, y + dy
