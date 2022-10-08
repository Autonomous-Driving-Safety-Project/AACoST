import os
import math
from shapely.geometry import LinearRing


class Utils:

    @classmethod
    def __coordinates(cls, vehicle_state):
        center_x = vehicle_state.x + vehicle_state.center_offset_x
        center_y = vehicle_state.y + vehicle_state.center_offset_y
        width = vehicle_state.width
        length = vehicle_state.length
        heading = vehicle_state.h
        lx = length / 2.0 * math.fabs(math.cos(heading))
        ly = length / 2.0 * math.fabs(math.sin(heading))
        wx = width / 2.0 * math.fabs(math.sin(heading))
        wy = width / 2.0 * math.fabs(math.cos(heading))
        return (center_x + lx + wx, center_y + ly - wy), (center_x - lx + wx, center_y - ly - wy), \
               (center_x - lx - wx, center_y - ly + wy), (center_x + lx - wx, center_y + ly + wy)

    @classmethod
    def gap(cls, vehicle_state_a, vehicle_state_b):
        bounding_box_a = LinearRing(cls.__coordinates(vehicle_state_a))
        bounding_box_b = LinearRing(cls.__coordinates(vehicle_state_b))
        return bounding_box_a.distance(bounding_box_b)
