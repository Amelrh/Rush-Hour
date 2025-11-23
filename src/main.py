#main.py 
from typing import Literal, List, Tuple, Optional
import os
import copy
import tkinter as tk
from rush_hour_puzzle import RushHourPuzzle, Vehicle
from solver import bfs, astar, heuristic_h1, heuristic_h2, heuristic_h3
from interface import animate_solution


Action = Tuple[str, int]
CONFIG_FILES = [
    "data/1.csv", "data/2-a.csv", "data/2-b.csv", "data/2-c.csv",
    "data/2-d.csv", "data/2-e.csv", "data/e-f.csv"
]


class Node:
    def __init__(self, state: RushHourPuzzle,
                 parent: Optional['Node'] = None,
                 action: Optional[Action] = None,
                 g: int = 0):
        self.state: RushHourPuzzle = state
        self.parent: Optional['Node'] = parent
        self.action: Optional[Action] = action
        self.g: int = g
        self.f: float = 0.0

    def __lt__(self, other: 'Node') -> bool:
        if self.f != other.f:
            return self.f < other.f
        return self.g < other.g

    def __hash__(self):
        return hash(self.state)

    def __eq__(self, other):
        if not isinstance(other, Node):
            return NotImplemented
        return self.state == other.state

    def getPath(self) -> List[RushHourPuzzle]:
        path: List[RushHourPuzzle] = []
        current: Optional['Node'] = self
        while current:
            path.append(current.state)
            current = current.parent
        return path[::-1]

    def getSolution(self) -> List[Action]:
        actions: List[Action] = []
        current: Optional['Node'] = self
        while current and current.action:
            actions.append(current.action)
            current = current.parent
        return actions[::-1]

    def setF(self, h: float):
        self.f = self.g + h


def choisir_algorithme():
    algos = [
        ("Breadth-First Search (BFS)", "bfs"),
        ("A*  Heuristic 1 (h1)", "astar1"),
        ("A*  Heuristic 2 (h2)", "astar2"),
        ("A*  Heuristic 3 (h3)", "astar3")
    ]
    choix = [algos[0][1]]  # valeur par défaut

    def on_submit():
        choix[0] = var.get()
        root.destroy()

    root = tk.Tk()
    root.title("Choisissez l'algorithme Rush Hour")
    var = tk.StringVar(value=algos[0][1])
    label = tk.Label(root, text="Sélectionnez l'algorithme à utiliser :", font=("Arial", 12))
    label.pack(pady=6)
    for texte, valeur in algos:
        tk.Radiobutton(root, text=texte, variable=var, value=valeur).pack(anchor='w')
    tk.Button(root, text="Lancer", command=on_submit).pack(pady=10)
    root.mainloop()
    return choix[0]


def choisir_fichier_csv(config_files):
    choix = [config_files[0]]  # valeur par défaut

    def on_submit():
        choix[0] = var.get()
        root.destroy()

    root = tk.Tk()
    root.title("Choisissez le fichier de configuration")
    var = tk.StringVar(value=config_files[0])
    label = tk.Label(root, text="Sélectionnez le fichier CSV à utiliser :", font=("Arial", 12))
    label.pack(pady=6)
    for file in config_files:
        tk.Radiobutton(root, text=file, variable=var, value=file).pack(anchor='w')
    tk.Button(root, text="Lancer", command=on_submit).pack(pady=10)
    root.mainloop()
    return choix[0]


def display_board_info(game: RushHourPuzzle, file_name: str):
    print("\n" + "=" * 80)
    print(f"FICHIER : {file_name}")
    print(f"DIMENSIONS : {game.board_width} x {game.board_height}")
    print(f"VEHICULES : {len(game.vehicles)} | MURS : {len(game.walls)}")
    print("=" * 80)
    print("\n[REPRESENTATION DU PLATEAU]")
    print(game)
    print("\n[LISTE DES VÉHICULES CHARGÉS]")
    for v in game.vehicles:
        print(f"  {v}")
    print("\n[LISTE DES MURS CHARGÉS]")
    if game.walls:
        for x, y in game.walls:
            print(f"  Mur à la position (x={x}, y={y})")
    else:
        print("  Aucun mur détecté.")
    print(f"\nStatut: {'Objectif atteint!' if game.isGoal() else 'Non objectif.'}")
    print("\n" + "-" * 80)


def run_solver_on_puzzle(game: RushHourPuzzle, algorithme: str):
    solution_node = None
    explored_count = 0
    exec_time = 0.0
    print(f"\n[Recherche avec l'algorithme sélectionné : {algorithme}]")

    # Sauvegarde de la position initiale de la voiture rouge pour heuristique h3
    red_car_init_pos = next((v.x for v in game.vehicles if v.id == 'X'), 0)

    if algorithme == "bfs":
        algorithme_display_name = "BFS"
        solution_node, explored_count, exec_time = bfs(game)
        if solution_node:
            print(f" Solution BFS trouvée en {solution_node.g} mouvements.")
        else:
            print("Aucune solution trouvée par BFS.")
    elif algorithme == "astar1":
        algorithme_display_name = "A* (h1)"
        solution_node, explored_count, exec_time = astar(game, heuristic_h1)
        if solution_node:
            print(f"Solution A* (h1) trouvée en {solution_node.g} mouvements.")
        else:
            print("Aucune solution trouvée par A* (h1).")
    elif algorithme == "astar2":
        algorithme_display_name = "A* (h2)"
        solution_node, explored_count, exec_time = astar(game, heuristic_h2)
        if solution_node:
            print(f"Solution A* (h2) trouvée en {solution_node.g} mouvements.")
        else:
            print("Aucune solution trouvée par A* (h2).")
    elif algorithme == "astar3":
        algorithme_display_name = "A* (h3)"
        # Passe la position initiale à l'heuristique h3
        solution_node, explored_count, exec_time = astar(game, lambda puzzle: heuristic_h3(puzzle, red_car_init_pos))
        if solution_node:
            print(f"Solution A* (h3) trouvée en {solution_node.g} mouvements.")
        else:
            print("Aucune solution trouvée par A* (h3).")
    else:
        algorithme_display_name = "Inconnu"
        print("Algorithme inconnu.")
    
    # Affichage des métriques
    print(f"Nombre de nœuds explorés : {explored_count}")
    print(f"Temps d'exécution : {exec_time:.4f} secondes")
    
    print("\n" + "#" * 80)
    if solution_node:
        print("\n Démarrage de l'animation de la solution sélectionnée")
        game_for_animation = copy.deepcopy(game)
        try:
            animate_solution(game_for_animation, solution_node.getSolution(), algorithm_name=algorithme_display_name)
        except Exception as e:
            print(f"\n[INFO] Pygame s'est terminé ou a rencontré une erreur : {e}")



if __name__ == "__main__":
    choix_algo = choisir_algorithme()
    fichier_choisi = choisir_fichier_csv(CONFIG_FILES)
    game = RushHourPuzzle()
    try:
        game.setVehicles(fichier_choisi)
        game.setBoard()
        display_board_info(game, fichier_choisi)
        run_solver_on_puzzle(game, choix_algo)
    except FileNotFoundError:
        print(f"Échec de chargement pour {fichier_choisi}: Fichier non trouvé. Vérifiez le chemin : {fichier_choisi}")
    except Exception as e:
        print(f"Échec de chargement/affichage pour {fichier_choisi}: {e}")

