"""
A toolset to solve the shortest path of graphs

1. For unweighted graphs, BFS is used.
2. For non-negative wweighted graph, Dijkstra's algorithm is used.
3. For general graph, Bellman-Ford is used.

"""

import heapq
import math
from typing import Tuple, List, Dict, Callable, Optional, Union

inf = float('inf')

def bfs(net: dict, start, end) -> int:
    """
    Breaadth-first search algorithm
    """

    if start not in net or end not in net:
        return -1

    visited = {start}
    current_level = {start}
    distance = 0

    while current_level:
        # Judge if reached
        if end in current_level:
            return distance

        # Generate next level
        next_level = set()
        for node in current_level:
            for neighbor in net.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    next_level.add(neighbor)

        if not next_level:
            return -1

        current_level = next_level
        distance += 1

    return -1


def dijkstra_list(graph: dict, start) -> tuple:
    """
    Dijkstra's algorithm using adjacency list
    
    Args:
        graph: dict {node: [(neighbor, weight), ...]}
        start: starting node
    
    Returns:
        distances: dict {node: shortest distance from start}
        previous: dict {node: previous node in shortest path}
    """

    # Initialize distances with infinity
    distances = {node: float('inf') for node in graph}
    distances[start] = 0

    # Priority queue: (distance, node)
    pq = [(0, start)]

    # Track previous nodes for path reconstruction
    previous = {node: None for node in graph}
    visited = set()

    while pq:
        current_dist, current = heapq.heappop(pq)

        # If we already found a better path, skip
        if current_dist > distances[current]:
            continue

        visited.add(current)  # Mark as visited

        # Explore neighbors
        for neighbor, weight in graph[current]:
            distance = current_dist + weight

            # If found shorter path to neighbor
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current
                heapq.heappush(pq, (distance, neighbor))

    return distances, previous


def reconstruct_path(previous: dict, start, target) -> list:
    """Reconstruct the shortest path from start to target"""
    if previous[target] is None and target != start:
        return []  # No path exists

    path = []
    current = target

    while current is not None:
        path.append(current)
        current = previous[current]

    return path[::-1]  # Reverse to get start→target


def BellmanFordDicts(graph: dict, start) -> tuple[dict, dict]:
    """
    BellmanFordDicts
    
    :param graph: A dictionary to express a graph. 
        {node: [(neighbor, weight), ...]}
    :type graph: dict
    :param start: Source node or starting node
    :return: distances to every other node and parent node of other nodes
    :rtype: tuple[dict[Any, Any], dict[Any, Any]]
    """
    # Boundary check
    if start not in graph:
        raise ValueError

    # Initialization
    distances = {node: inf for node in graph}
    distances[start] = 0
    parentNodes = {node: None for node in graph}
    step = 0
    updated = True

    # Iteration
    while step <= len(graph) and updated:
        step += 1
        updated = False

        for node in graph:
            if distances[node] == inf:
                continue

            if not graph[node]:
                continue

            for neighbor, weight in graph[node]:
                distance = distances[node] + weight
                if distance < distances[neighbor]:
                    updated = True
                    distances[neighbor] = distance
                    parentNodes[neighbor] = node

    # Unreachable: step = len(graph), there are cycles
    if step == len(graph) + 1:
        return {}, {}

    # Return distances and parent nodes
    return distances, parentNodes


def reconstructPath(previous: dict, start, target) -> list:
    if not previous:
        return ['Negative cycle exists.']  # Negative cycle exists

    if previous[target] is None and target != start:
        return ['No path exists.']  # No path exists

    path = []
    current = target

    while current != None:
        path.append(current)
        current = previous[current]

    return path[::-1]  # Reverse to get from start to target


class heuristics:
    def __init__(self):
        pass


    @staticmethod
    def heuristic_euclidean(node: Tuple[float, float], target: Tuple[float, float]) -> float:
        """
        Euclidean distance heuristic for A*
        Suitable for 2D navigation systems (maps, pathfinding)
        
        Args:
            node: (x, y) coordinates
            target: (x, y) target coordinates
        
        Returns:
            Euclidean distance
        """
        dx = node[0] - target[0]
        dy = node[1] - target[1]
        return math.sqrt(dx*dx + dy*dy)


    @staticmethod
    def heuristic_manhattan(node: Tuple[float, float], target: Tuple[float, float]) -> float:
        """
        Manhattan distance heuristic for A*
        Better for grid-based navigation (city blocks)
        
        Args:
            node: (x, y) coordinates
            target: (x, y) target coordinates
        
        Returns:
            Manhattan distance
        """
        return abs(node[0] - target[0]) + abs(node[1] - target[1])


    @staticmethod
    def heuristic_chebyshev(node: Tuple[float, float], target: Tuple[float, float]) -> float:
        """
        Chebyshev distance heuristic (max of absolute differences)
        For 8-directional movement (chess king moves)
        
        Args:
            node: (x, y) coordinates
            target: (x, y) target coordinates
        
        Returns:
            Chebyshev distance
        """
        return max(abs(node[0] - target[0]), abs(node[1] - target[1]))


class WeightedGraphSolutions:
    """
    A set of algorithms for weighted graphs
    """

    def __init__(self, graph: dict):
        self.graph = graph


    def Dijkstra(self, start, target) -> tuple[list, int | float]:
        """
        Dijkstra's algorithm using adjacency list
        
        Args:
            graph: dict {node: [(neighbor, weight), ...]}
            start: starting node
            target: target node
        
        Returns:
            distance: the minimal weight
            path: the shortest path
        """

        graph = self.graph

        if not (start in graph and target in graph):
            return [], inf

        distances, previous = dijkstra_list(graph, start)
        path = reconstruct_path(previous, start, target)

        return path, distances[target]


    def BellmanFord(self, start, target) -> tuple[list, int | float]:
        """
        Bellman-Ford Algorithm
        
        :param graph: A dictionary to express a graph.
            {node: [(neighbor, weight), ...]}
        :type graph: dict
        :param start: Source node or starting node
        :param target: Target node
        :return: The shortest path and the total weight of it
        :rtype: tuple[list[Any], int | float]
        """

        graph = self.graph

        if not (start in graph and target in graph):
            return ['Start or target not in the graph.'], inf

        distances, previous = BellmanFordDicts(graph, start)
        if not previous:
            return ['Negative cycle exists'], -inf

        path = reconstructPath(previous, start, target)
        if path == ['No path exists.']:
            return path, inf

        return path, distances[target]


    def AStar(
        self,
        start,
        target,
        heuristic: Union[str, Callable] = "euclidean",
        positions: Optional[Dict] = None
    ) -> Tuple[List, int | float]:
        """
        A* pathfinding algorithm
        
        Perfect for modern GPS navigation systems, game AI, and robotics
        
        Args:
            graph: Adjacency list {node: [(neighbor, cost), ...]}
                or if positions dict provided: {node: [(neighbor, cost), ...]}
            start: Starting node
            target: target node
            heuristic: Heuristic function h(node, target) -> estimated cost to target
                    Default: Euclidean distance
            positions: Dict mapping nodes to (x, y) coordinates
                    Required if nodes aren't tuples themselves
        
        Returns:
            path: List of nodes from start to target (empty if no path)
            cost: Total cost of the path (float('inf') if no path)
        
        Example:
            graph = {
                'A': [('B', 4), ('C', 2)],
                'B': [('D', 5)],
                'C': [('D', 1)],
                'D': []
            }
            positions = {
                'A': (0, 0),
                'B': (1, 3),
                'C': (2, 0),
                'D': (3, 2)
            }
            path, cost = AStar(graph, 'A', 'D', positions=positions)
        """

        if not isinstance(heuristic, str):
            raise TypeError("Unsupported heuristic type.")

        if isinstance(heuristic, str):
            heuristic_map = {
                "euclidean": heuristics.heuristic_euclidean,
                "manhattan": heuristics.heuristic_manhattan,
                "chebyshev": heuristics.heuristic_chebyshev
            }
            heuristic_lower = heuristic.lower()
            if heuristic_lower in heuristic_map:
                heuristic = heuristic_map[heuristic_lower]
            else:
                raise ValueError(f"Unsupported heuristic: '{heuristic}'. "
                                f"Choose from: {list(heuristic_map.keys())}")

        graph = self.graph
        use_heuristic = positions is not None

        # Validate inputs
        if start not in graph or target not in graph:
            return [], float('inf')

        if start == target:
            return [start], 0

        # Priority queue: (f_score, counter, node)
        # counter breaks ties for consistent behavior
        open_set = [(0, 0, start)]
        counter = 1

        # Track best cost to reach each node
        g_score = {node: float('inf') for node in graph}
        g_score[start] = 0

        # Track parent for path reconstruction
        came_from = {node: None for node in graph}

        # Track nodes in open set for efficient checking
        open_set_check = {start}

        # Track visited nodes
        closed_set = set()

        while open_set:
            _, _, current = heapq.heappop(open_set)
            open_set_check.discard(current)

            # target reached
            if current == target:
                path = []
                node = target
                while node is not None:
                    path.append(node)
                    node = came_from[node]
                return path[::-1], g_score[target]

            closed_set.add(current)

            # Explore neighbors
            for neighbor, cost in graph.get(current, []):
                if neighbor in closed_set:
                    continue

                # Calculate tentative g_score
                tentative_g = g_score[current] + cost

                # If this path to neighbor is better than any previous one
                if tentative_g < g_score[neighbor]:
                    # Record this as the best path so far
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g

                    # Calculate f_score = g + h
                    h_score = heuristic(
                        positions[neighbor], positions[target]) if use_heuristic else 0

                    f_score = tentative_g + h_score

                    # Add to open set if not already there
                    if neighbor not in open_set_check:
                        heapq.heappush(open_set, (f_score, counter, neighbor))
                        open_set_check.add(neighbor)
                        counter += 1

        # No path found
        return [], inf
