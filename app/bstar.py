from astar import AStar
import math


class PathFinder(AStar):
    def __init__(self, width, height, grid):
        self.grid = grid
        self.width = width
        self.height = height

    def heuristic_cost_estimate(self, n1, n2):
        """computes the 'direct' distance between two (x,y) tuples"""
        (x1, y1) = n1
        (x2, y2) = n2
        return math.hypot(x2 - x1, y2 - y1)

    def distance_between(self, n1, n2):
        """this method returns the values n1 and n2"""
        n1x, n1y = n1
        n2x, n2y = n2
        return self.grid[n1y][n1x] + self.grid[n2y][n2x]

    def neighbors(self, node):
        """ for a given coordinate in the maze, returns up to 4 adjacent(north,east,south,west)
            nodes that can be reached (=any adjacent coordinate that is not a wall)
        """
        x, y = node
        possible_nodes = [
            (nx, ny) for nx, ny in [
                (x, y - 1), 
                (x, y + 1), 
                (x - 1, y), 
                (x + 1, y)
            ]
            if 0 <= nx < self.width and 0 <= ny < self.height and 
                self.grid[ny][nx] > 0]

        # print('Got node', node)
        # print('possible_nodes', possible_nodes)
        return possible_nodes
