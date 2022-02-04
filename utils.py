"""
Utility  functions used in project.
"""

import math

def move_coordinates(x, y, angle, distance):
    """Return new coordinates based on old position, angle and distance. """
    dx = distance*math.sin(math.radians(angle))
    dy = distance*math.cos(math.radians(angle))
    return x + dx, y + dy

def heading_to_angle(x, y):
    """Return angle based on vector. """
    return math.degrees(math.atan2(x, y))
