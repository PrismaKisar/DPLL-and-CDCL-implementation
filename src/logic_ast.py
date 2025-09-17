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

@dataclass
class Literal(Formula):
    variable: str
    negated: bool = False

    def __str__(self) -> str:
        if self.negated:
            return f"¬{self.variable}"
        else:
            return self.variable

@dataclass
class Clause(Formula):
    literals: list[Literal]

    def __str__(self) -> str:
        if not self.literals:
            return "⊥"
        if len(self.literals) == 1:
            return str(self.literals[0])
        return " ∨ ".join(str(lit) for lit in self.literals)

@dataclass
class CNFFormula(Formula):
    clauses: list[Clause]

    def __str__(self) -> str:
        if not self.clauses:
            return "⊤"
        if len(self.clauses) == 1:
            return str(self.clauses[0])
        return " ∧ ".join(f"({clause})" for clause in self.clauses)


