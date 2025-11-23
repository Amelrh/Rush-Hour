#solver.py
# solver.py
from typing import Optional, Callable, Tuple
import heapq
import time  # Ajouté pour mesurer le temps
from collections import deque
from node import Node
from rush_hour_puzzle import RushHourPuzzle

def heuristic_h1(puzzle: RushHourPuzzle) -> int:
    """
    Heuristique h1 : Distance de la voiture rouge (X) à la sortie.
    La voiture rouge est horizontale, donc la distance est board_width - (x + length).
    """
    red_car = next((v for v in puzzle.vehicles if v.id == 'X'), None)
    if not red_car or red_car.orientation != 'H':
        return 0
    return puzzle.board_width - (red_car.x + red_car.length)

def heuristic_h2(puzzle: RushHourPuzzle) -> int:
    """
    Heuristique h2 : h1 + nombre de véhicules bloquant le chemin de la voiture rouge vers la sortie.
    Les véhicules bloquants sont ceux dans la rangée de sortie (board_height//2 - 1) et à droite de la voiture rouge.
    """
    h1 = heuristic_h1(puzzle)
    red_car = next((v for v in puzzle.vehicles if v.id == 'X'), None)
    if not red_car:
        return h1
    exit_row = (puzzle.board_height // 2) - 1
    blocking_count = sum(1 for v in puzzle.vehicles if v.id != 'X' and v.y == exit_row and v.x > red_car.x)
    return h1 + blocking_count

def heuristic_h3(puzzle: RushHourPuzzle, red_car_init_pos: int) -> int:
    """
    Heuristique h3 : h2 + nombre de véhicules bloquant les véhicules bloquants (blockers des blockers).
    Cela rend l'heuristique plus informée en considérant les chaînes de blocage, améliorant potentiellement les performances
    (moins de nœuds explorés, temps réduit) tout en gardant un nombre de mouvements proche de BFS.
    """
    h2 = heuristic_h2(puzzle)
    red_car = next((v for v in puzzle.vehicles if v.id == 'X'), None)
    if not red_car:
        return h2
    exit_row = (puzzle.board_height // 2) - 1
    blocking_vehicles = [v for v in puzzle.vehicles if v.id != 'X' and v.y == exit_row and v.x > red_car.x]
    additional_blockers = sum(len(puzzle.get_blockers_of_vehicle_by_id(v.id)) for v in blocking_vehicles)
    return h2 + additional_blockers

def bfs(initial: RushHourPuzzle) -> Tuple[Optional[Node], int, float]:
    """
    Algorithme BFS : Recherche en largeur d'abord pour trouver la solution avec le nombre minimal de mouvements.
    Retourne : (nœud solution, nombre de nœuds explorés, temps d'exécution en secondes)
    """
    start_time = time.time()
    initial_node = Node(initial)
    if initial.isGoal():
        return initial_node, 1, time.time() - start_time
    frontier = deque([initial_node])
    explored = set([initial_node])
    explored_count = 1  # Compte le nœud initial
    while frontier:
        node = frontier.popleft()
        for action, successor in node.state.successorFunction():
            child = Node(successor, node, action, node.g + 1)
            if child not in explored:
                explored_count += 1
                if successor.isGoal():
                    return child, explored_count, time.time() - start_time
                explored.add(child)
                frontier.append(child)
    return None, explored_count, time.time() - start_time

def astar(initial: RushHourPuzzle, heuristic: Callable[[RushHourPuzzle], int]) -> Tuple[Optional[Node], int, float]:
    """
    Algorithme A* : Recherche avec heuristique pour trouver une solution optimale ou proche.
    Retourne : (nœud solution, nombre de nœuds explorés, temps d'exécution en secondes)
    """
    start_time = time.time()
    initial_node = Node(initial)
    initial_node.setF(heuristic(initial))
    frontier = []
    heapq.heappush(frontier, initial_node)
    explored = set()
    g_score = {initial_node: 0}
    explored_count = 0  # Sera incrémenté quand on explore
    while frontier:
        current = heapq.heappop(frontier)
        if current.state.isGoal():
            return current, explored_count, time.time() - start_time
        explored.add(current)
        explored_count += 1
        for action, successor in current.state.successorFunction():
            neighbor = Node(successor, current, action, current.g + 1)
            if neighbor in explored:
                continue
            tentative_g = current.g + 1
            if tentative_g < g_score.get(neighbor, float('inf')):
                g_score[neighbor] = tentative_g
                neighbor.setF(heuristic(successor))
                heapq.heappush(frontier, neighbor)
    return None, explored_count, time.time() - start_time
