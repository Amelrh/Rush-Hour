#rush hour_puzzle.py
import csv
from typing import Literal, List, Tuple, Optional

Action = Tuple[str, int]
Orientation = Literal['H', 'V']


class Vehicle:
    def __init__(self,
                 id: str,
                 x: str,
                 y: str,
                 orientation: str,
                 length: str):
        self.id: str = id
        self.orientation: Orientation = orientation.upper()
        if self.orientation not in ['H', 'V']:
            raise ValueError(f"L'orientation doit être 'H' ou 'V' (Véhicule {id}).")
        try:
            self.x: int = int(x)
            self.y: int = int(y)
            self.length: int = int(length)
        except ValueError as e:
            raise ValueError(f"Les coordonnées et la longueur du véhicule {id} doivent être des nombres entiers. Erreur: {e}")

    def __repr__(self) -> str:
        return f"Vehicle('{self.id}', pos=({self.x},{self.y}), orient='{self.orientation}', len={self.length})"

    def __hash__(self):
        return hash((self.id, self.x, self.y, self.orientation, self.length))

    def __eq__(self, other):
        if not isinstance(other, Vehicle):
            return NotImplemented
        return (self.id, self.x, self.y, self.orientation, self.length) == \
               (other.id, other.x, other.y, other.orientation, other.length)


class RushHourPuzzle:

    def __init__(self, board_height: int = 6, board_width: int = 6):
        self.board_height: int = board_height
        self.board_width: int = board_width
        self.vehicles: List[Vehicle] = []
        self.walls: List[Tuple[int, int]] = []
        self.board: Optional[List[List[str]]] = None

    def setVehicles(self, csv_file_path: str):
        self.vehicles = []
        self.walls = []
        try:
            with open(csv_file_path, mode='r', newline='') as file:
                reader = csv.reader(file)
                dims = next(reader)
                if len(dims) < 2:
                    raise ValueError("Dimensions manquantes.")
                self.board_width, self.board_height = int(dims[0]), int(dims[1])
                for row in reader:
                    if not row: continue
                    if row[0].strip() == '#':
                        if len(row) >= 3:
                            try:
                                self.walls.append((int(row[1]), int(row[2])))
                            except ValueError:
                                pass
                    elif len(row) >= 5:
                        try:
                            self.vehicles.append(Vehicle(row[0], row[1], row[2], row[3], row[4]))
                        except ValueError:
                            pass
        except FileNotFoundError:
            raise FileNotFoundError(f"Erreur: Fichier non trouvé à {csv_file_path}")
        except Exception as e:
            raise Exception(f"Erreur lors du parsing du CSV: {e}")

    def setBoard(self):
        self.board = [[' ' for _ in range(self.board_width)] for _ in range(self.board_height)]

        for x, y in self.walls:
            if 0 <= x < self.board_width and 0 <= y < self.board_height:
                self.board[y][x] = '#'

        for v in self.vehicles:
            for i in range(v.length):
                x = v.x + i if v.orientation == 'H' else v.x
                y = v.y + i if v.orientation == 'V' else v.y

                if 0 <= x < self.board_width and 0 <= y < self.board_height:
                    self.board[y][x] = v.id

    def isGoal(self) -> bool:
        red_car = next((v for v in self.vehicles if v.id == 'X'), None)
        if not red_car or red_car.orientation != 'H':
            return False
        exit_row = (self.board_height // 2) - 1
        target_x_start = self.board_width - red_car.length

        return (red_car.y == exit_row and red_car.x == target_x_start)

    def __str__(self):
        if self.board is None:
            return "Plateau non initialisé. Appelez setBoard() en premier."

        board_str = []
        col_indices = "  " + " ".join(map(str, range(self.board_width)))
        board_str.append(col_indices)
        board_str.append("  " + "—" * (self.board_width * 2 - 1))

        exit_row_index = (self.board_height // 2) - 1

        for i, row in enumerate(self.board):
            row_display = f"{i}|" + " ".join(row) + "|"
            if i == exit_row_index:
                row_display += " <- EXIT"

            board_str.append(row_display)

        board_str.append("  " + "—" * (self.board_width * 2 - 1))

        return "\n".join(board_str)

    def __eq__(self, other):
        if not isinstance(other, RushHourPuzzle):
            return NotImplemented
        return sorted(self.vehicles, key=lambda v: v.id) == sorted(other.vehicles, key=lambda v: v.id)

    def __hash__(self):
        return hash(tuple(sorted(v.__hash__() for v in self.vehicles)))

    def get_potential_moves(self, vehicle: 'Vehicle', direction: int) -> int:
        max_moves = 0
        if self.board is None:
            self.setBoard()

        if direction == -1:
            start_offset = -1
        else:
            start_offset = vehicle.length

        while True:
            if vehicle.orientation == 'H':
                next_x = vehicle.x + start_offset + (direction * max_moves)
                next_y = vehicle.y
            else:
                next_x = vehicle.x
                next_y = vehicle.y + start_offset + (direction * max_moves)

            is_out_of_bounds = not (0 <= next_x < self.board_width and 0 <= next_y < self.board_height)

            if is_out_of_bounds:
                exit_row = (self.board_height // 2) - 1
                if vehicle.id == 'X' and vehicle.orientation == 'H' and next_x == self.board_width and next_y == exit_row:
                    max_moves += 1
                break

            cell_content = self.board[next_y][next_x]

            if cell_content == ' ':
                max_moves += 1
            elif cell_content == '#':
                break
            else:
                break

        return max_moves

    def create_new_state(self, vehicle_index: int, displacement: int) -> 'RushHourPuzzle':
        new_puzzle = RushHourPuzzle(self.board_height, self.board_width)
        new_puzzle.walls = list(self.walls)

        new_vehicles = []
        old_v = self.vehicles[vehicle_index]

        for j, v in enumerate(self.vehicles):
            if j == vehicle_index:
                new_x = old_v.x + displacement if old_v.orientation == 'H' else old_v.x
                new_y = old_v.y + displacement if old_v.orientation == 'V' else old_v.y
                moved_v = Vehicle(old_v.id, str(new_x), str(new_y), old_v.orientation, str(old_v.length))
                new_vehicles.append(moved_v)
            else:
                new_vehicles.append(Vehicle(v.id, str(v.x), str(v.y), v.orientation, str(v.length)))

        new_puzzle.vehicles = new_vehicles
        new_puzzle.setBoard()

        return new_puzzle

    def get_vehicle_index(self, vehicle_id: str) -> Optional[int]:
        try:
            return next(i for i, v in enumerate(self.vehicles) if v.id == vehicle_id)
        except StopIteration:
            return None

    def move_vehicle(self, action: Action):
        vehicle_id, displacement = action
        vehicle_index = self.get_vehicle_index(vehicle_id)
        if vehicle_index is None:
            return
        old_v = self.vehicles[vehicle_index]
        new_x = old_v.x + displacement if old_v.orientation == 'H' else old_v.x
        new_y = old_v.y + displacement if old_v.orientation == 'V' else old_v.y
        self.vehicles[vehicle_index].x = new_x
        self.vehicles[vehicle_index].y = new_y
        self.setBoard()

    def successorFunction(self) -> List[Tuple[Action, 'RushHourPuzzle']]:
        successors: List[Tuple[Action, 'RushHourPuzzle']] = []

        if self.board is None:
            self.setBoard()

        for i, vehicle in enumerate(self.vehicles):
            moves_backward = self.get_potential_moves(vehicle, direction=-1)
            for d in range(1, moves_backward + 1):
                new_state = self.create_new_state(vehicle_index=i, displacement=-d)
                action: Action = (vehicle.id, -d)
                successors.append((action, new_state))

            moves_forward = self.get_potential_moves(vehicle, direction=+1)
            for d in range(1, moves_forward + 1):
                new_state = self.create_new_state(vehicle_index=i, displacement=+d)
                action: Action = (vehicle.id, +d)
                successors.append((action, new_state))

        return successors

    # Méthodes ajoutées pour h3 améliorée

    def get_blockers_of_vehicle_by_id(self, vehicle_id: str) -> List[str]:
        if self.board is None:
            self.setBoard()

        vehicle = next((v for v in self.vehicles if v.id == vehicle_id), None)
        if not vehicle:
            return []
        blockers = set()

        if vehicle.orientation == 'H':
            start_x = vehicle.x + vehicle.length
            y = vehicle.y
            if start_x < self.board_width:
                cell = self.board[y][start_x]
                if cell != ' ' and cell != '#':
                    blockers.add(cell)
        else:
            x = vehicle.x
            start_y = vehicle.y - 1
            if start_y >= 0:
                cell = self.board[start_y][x]
                if cell != ' ' and cell != '#':
                    blockers.add(cell)
            start_y = vehicle.y + vehicle.length
            if start_y < self.board_height:
                cell = self.board[start_y][x]
                if cell != ' ' and cell != '#':
                    blockers.add(cell)
        return list(blockers)

    def no_moves_possible(self, vehicle: Vehicle) -> bool:
        moves_back = self.get_potential_moves(vehicle, direction=-1)
        moves_forw = self.get_potential_moves(vehicle, direction=+1)
        return moves_back == 0 and moves_forw == 0

    def estimate_mobility(self, vehicle: Vehicle) -> int:
        """
        Nouvelle fonction pour estimer la mobilité locale du véhicule (utile pour l'heuristique).
        """
        moves_back = self.get_potential_moves(vehicle, direction=-1)
        moves_forw = self.get_potential_moves(vehicle, direction=+1)
        return moves_back + moves_forw
