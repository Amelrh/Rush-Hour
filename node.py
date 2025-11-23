#node.py 
from typing import  List, Optional

from rush_hour_puzzle import Action, RushHourPuzzle
class Node:
    
    def __init__(self, 
                 state: RushHourPuzzle, 
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

    # ----------------------------------------------------------------------

    def getPath(self) -> List[RushHourPuzzle]:
        path: List[RushHourPuzzle] = []
        current: Optional[Node] = self
        while current:
            path.append(current.state)
            current = current.parent
        return path[::-1]

    def getSolution(self) -> List[Action]:
        actions: List[Action] = []
        current: Optional[Node] = self
        while current and current.action:
            actions.append(current.action)
            current = current.parent
        return actions[::-1] 
       
    # ----------------------------------------------------------------------

    def setF(self, h: float):
        self.f = self.g + h