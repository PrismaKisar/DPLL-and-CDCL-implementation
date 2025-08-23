from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

from src.logic_ast import CNFFormula, Clause, Literal


class DecisionResult(Enum):
    SAT = "SAT"
    UNSAT = "UNSAT"


@dataclass
class Assignment:
    variable: str
    value: bool
    decision_level: int = 0
    

class DPLLSolver:
    def __init__(self, cnf_formula: CNFFormula):
        self.cnf = cnf_formula
        self.assignment: Dict[str, bool] = {}
        self.decision_stack: List[Assignment] = []
        
    def _evaluate_clause(self, clause: Clause) -> Optional[bool]:
        satisfied = False
        unassigned_count = 0
        
        for lit in clause.literals:
            if lit.variable in self.assignment:
                lit_value = self.assignment[lit.variable]
                if (not lit.negated and lit_value) or (lit.negated and not lit_value):
                    satisfied = True
                    break
            else:
                unassigned_count += 1
        
        if satisfied:
            return True
        elif unassigned_count == 0:
            return False
        else:
            return None
    
    def _unit_propagation(self) -> Optional[DecisionResult]:
        changed = True
        while changed:
            changed = False
            
            if not self._simplify_formula():
                return DecisionResult.UNSAT
            
            for clause in self.cnf.clauses:
                if len(clause.literals) == 1:
                    lit = clause.literals[0]
                    if lit.variable not in self.assignment:
                        self.assignment[lit.variable] = not lit.negated
                        changed = True
        return None
    
    def _choose_variable(self) -> Optional[str]:
        all_variables: Set[str] = set()
        for clause in self.cnf.clauses:
            for lit in clause.literals:
                all_variables.add(lit.variable)
        
        for var in all_variables:
            if var not in self.assignment:
                return var
        return None
    
    def _make_decision(self, variable: str, value: bool):
        decision_level = len(self.decision_stack)
        assignment = Assignment(variable, value, decision_level)
        self.decision_stack.append(assignment)
        self.assignment[variable] = value
    
    def _backtrack(self):
        if not self.decision_stack:
            return
        
        last_decision = self.decision_stack.pop()
        del self.assignment[last_decision.variable]
        
        while (self.decision_stack and 
               self.decision_stack[-1].decision_level == last_decision.decision_level):
            assignment = self.decision_stack.pop()
            del self.assignment[assignment.variable]
        
        if last_decision.value:
            self._make_decision(last_decision.variable, False)
    
    def _all_clauses_satisfied(self) -> bool:
        for clause in self.cnf.clauses:
            if self._evaluate_clause(clause) is not True:
                return False
        return True
    
    def _simplify_formula(self) -> bool:
        original_clauses = self.cnf.clauses[:]
        simplified_clauses: List[Clause] = []
        
        for clause in original_clauses:
            clause_satisfied = False
            simplified_literals: List[Literal] = []
            
            for lit in clause.literals:
                if lit.variable in self.assignment:
                    lit_value = self.assignment[lit.variable]
                    if (not lit.negated and lit_value) or (lit.negated and not lit_value):
                        clause_satisfied = True
                        break
                else:
                    simplified_literals.append(lit)
            
            if not clause_satisfied:
                if not simplified_literals:
                    return False
                simplified_clauses.append(Clause(simplified_literals))
        
        self.cnf.clauses = simplified_clauses
        return True
    
    def _pure_literal_elimination(self) -> Optional[DecisionResult]:
        literal_polarities: Dict[str, Set[bool]] = {}
        
        for clause in self.cnf.clauses:
            if self._evaluate_clause(clause) is not True:
                for lit in clause.literals:
                    if lit.variable not in self.assignment:
                        if lit.variable not in literal_polarities:
                            literal_polarities[lit.variable] = set()
                        literal_polarities[lit.variable].add(not lit.negated)
        
        for var, polarities in literal_polarities.items():
            if len(polarities) == 1:
                self.assignment[var] = list(polarities)[0]
        
        return None
    
    def solve(self) -> DecisionResult:
        while True:
            result = self._unit_propagation()
            if result == DecisionResult.UNSAT:
                if not self.decision_stack:
                    return DecisionResult.UNSAT
                self._backtrack()
                continue
            
            result = self._pure_literal_elimination()
            if result == DecisionResult.UNSAT:
                if not self.decision_stack:
                    return DecisionResult.UNSAT
                self._backtrack()
                continue
            
            if self._all_clauses_satisfied():
                return DecisionResult.SAT
            
            variable = self._choose_variable()
            if variable is None:
                return DecisionResult.SAT
            
            self._make_decision(variable, True)