from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class Formula(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass

@dataclass
class Variable(Formula):
    name: str

    def __str__(self) -> str:
        return self.name
    
@dataclass
class Not(Formula):
    operand: Formula

    def __str__(self) -> str:
        if isinstance(self.operand, Variable):
            return f"¬{self.operand}"
        else:
            return f"¬({self.operand})" 

@dataclass
class And(Formula):
    left: Formula
    right: Formula

    def __str__(self) -> str:
        left_str = str(self.left) if isinstance(self.left, Variable) else f"({self.left})"
        right_str = str(self.right) if isinstance(self.right, Variable) else f"({self.right})"
        return f"{left_str} ∧ {right_str}"
    
@dataclass
class Or(Formula):
    left: Formula
    right: Formula

    def __str__(self) -> str:
        left_str = str(self.left) if isinstance(self.left, (Variable, Not)) else f"({self.left})"
        right_str = str(self.right) if isinstance(self.right, (Variable, Not)) else f"({self.right})"
        return f"{left_str} ∨ {right_str}" 
    
@dataclass
class Implies(Formula):
    left: Formula
    right: Formula

    def __str__(self) -> str:
        left_str = str(self.left) if isinstance(self.left, Variable) else f"({self.left})"
        right_str = str(self.right) if isinstance(self.right, Variable) else f"({self.right})"
        return f"{left_str} → {right_str}" 

@dataclass
class Biconditional(Formula):
    left: Formula
    right: Formula

    def __str__(self) -> str:
        left_str = str(self.left) if isinstance(self.left, Variable) else f"({self.left})"
        right_str = str(self.right) if isinstance(self.right, Variable) else f"({self.right})"
        return f"{left_str} ↔ {right_str}" 
    

