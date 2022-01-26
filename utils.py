import math

def move_coordinates(x, y, angle, distance):
    dx = distance*math.sin(math.radians(angle))
    dy = distance*math.cos(math.radians(angle))
    return x + dx, y + dy

def heading_to_angle(x, y):
    return math.degrees(math.atan2(x, y))
