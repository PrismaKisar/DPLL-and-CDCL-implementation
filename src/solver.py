from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
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
    reason: Optional[Clause] = None


@dataclass
class ImplicationNode:
    variable: str
    value: bool
    decision_level: int
    reason: Optional[Clause] = None
    antecedents: List[str] = field(default_factory=lambda: [])
    

class DPLLSolver:
    def __init__(self, cnf_formula: CNFFormula):
        self.cnf = cnf_formula
        self.assignment: Dict[str, bool] = {}
    
    def solve(self) -> DecisionResult:
        assignment: Dict[str, bool] = {}
        return self._dpll(assignment)
    
    def _dpll(self, assignment: Dict[str, bool]) -> DecisionResult:
        assignment = assignment.copy()
        changed = True
        while changed:
            changed = False
            for clause in self.cnf.clauses:
                state = self._evaluate_clause(clause, assignment)
                if state is False:
                    return DecisionResult.UNSAT
                
                if state is None:
                    unassigned = [lit for lit in clause.literals if lit.variable not in assignment]
                    if len(unassigned) == 1:
                        lit = unassigned[0]
                        value = not lit.negated
                        assignment[lit.variable] = value
                        changed = True
        
        literal_polarities: Dict[str, Set[bool]] = {}
        for clause in self.cnf.clauses:
            if self._evaluate_clause(clause, assignment) is not True:
                for lit in clause.literals:
                    if lit.variable not in assignment:
                        if lit.variable not in literal_polarities:
                            literal_polarities[lit.variable] = set()
                        literal_polarities[lit.variable].add(not lit.negated)
        
        for var, polarities in literal_polarities.items():
            if len(polarities) == 1:
                assignment[var] = list(polarities)[0]
        
        all_satisfied = True
        for clause in self.cnf.clauses:
            if self._evaluate_clause(clause, assignment) is not True:
                all_satisfied = False
                break
        
        if all_satisfied:
            self.assignment = assignment
            return DecisionResult.SAT
        
        variable = self._choose_variable(assignment)
        if variable is None:
            self.assignment = assignment
            return DecisionResult.SAT
        
        assignment_true = assignment.copy()
        assignment_true[variable] = True
        
        result = self._dpll(assignment_true)
        if result == DecisionResult.SAT:
            return DecisionResult.SAT
        
        assignment_false = assignment.copy()
        assignment_false[variable] = False
        
        result = self._dpll(assignment_false)
        return result
    
    def _evaluate_clause(self, clause: Clause, assignment: Dict[str, bool]) -> Optional[bool]:
        satisfied = False
        unassigned_count = 0
        
        for lit in clause.literals:
            if lit.variable in assignment:
                lit_value = assignment[lit.variable]
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
    
    def _choose_variable(self, assignment: Dict[str, bool]) -> Optional[str]:
        all_variables: Set[str] = set()
        for clause in self.cnf.clauses:
            for lit in clause.literals:
                all_variables.add(lit.variable)
        
        for var in all_variables:
            if var not in assignment:
                return var
        return None


class CDCLSolver:
    def __init__(self, cnf_formula: CNFFormula):
        self.cnf = cnf_formula
        self.assignment: Dict[str, bool] = {}
        self.decision_stack: List[Assignment] = []
        self.learned_clauses: List[Clause] = []
        self.decision_level = 0
        self.implication_graph: Dict[str, ImplicationNode] = {}
        
    def _unit_propagation(self) -> Optional[Clause]:
        changed = True
        while changed:
            changed = False
            
            for clause in self.cnf.clauses + self.learned_clauses:
                clause_state = self._evaluate_clause(clause)
                
                if clause_state is False:
                    return clause
                
                if clause_state is None:
                    unassigned_literals: List[Literal] = []
                    for lit in clause.literals:
                        if lit.variable not in self.assignment:
                            unassigned_literals.append(lit)
                    
                    if len(unassigned_literals) == 1:
                        lit = unassigned_literals[0]
                        value = not lit.negated
                        self._add_implication(lit.variable, value, clause)
                        changed = True
        
        return None
    
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
    
    def _analyze_conflict(self, conflict_clause: Clause) -> Clause:
        if self.decision_level == 0:
            return conflict_clause
            
        current_clause = conflict_clause
        current_level_vars = 0
        
        for lit in current_clause.literals:
            if (lit.variable in self.implication_graph and 
                self.implication_graph[lit.variable].decision_level == self.decision_level):
                current_level_vars += 1
        
        if current_level_vars <= 1:
            return current_clause
            
        most_recent_var = None
        most_recent_idx = -1
        
        for lit in current_clause.literals:
            if (lit.variable in self.implication_graph and 
                self.implication_graph[lit.variable].decision_level == self.decision_level):
                for i, assignment in enumerate(self.decision_stack):
                    if (assignment.variable == lit.variable and 
                        assignment.decision_level == self.decision_level):
                        if i > most_recent_idx:
                            most_recent_idx = i
                            most_recent_var = lit.variable
                        break
        
        if most_recent_var is None or most_recent_var not in self.implication_graph:
            return current_clause
            
        node = self.implication_graph[most_recent_var]
        if node.reason is None:
            return current_clause
            
        resolved_literals: List[Literal] = []
        
        for lit in current_clause.literals:
            if lit.variable != most_recent_var:
                resolved_literals.append(lit)
                
        for lit in node.reason.literals:
            if lit.variable != most_recent_var:
                already_exists = False
                for existing_lit in resolved_literals:
                    if (existing_lit.variable == lit.variable and 
                        existing_lit.negated == lit.negated):
                        already_exists = True
                        break
                if not already_exists:
                    resolved_literals.append(lit)
        
        resolved_clause = Clause(resolved_literals)
        
        new_current_level_vars = 0
        for lit in resolved_clause.literals:
            if (lit.variable in self.implication_graph and 
                self.implication_graph[lit.variable].decision_level == self.decision_level):
                new_current_level_vars += 1
                
        if new_current_level_vars <= 1:
            return resolved_clause
        else:
            return self._analyze_conflict(resolved_clause)
    
    def _backjump(self, learned_clause: Clause) -> int:
        if len(learned_clause.literals) <= 1:
            return 0
            
        max_level = 0
        second_max_level = 0
        
        for lit in learned_clause.literals:
            if lit.variable in self.implication_graph:
                level = self.implication_graph[lit.variable].decision_level
                if level > max_level:
                    second_max_level = max_level
                    max_level = level
                elif level > second_max_level and level < max_level:
                    second_max_level = level
        
        return second_max_level
    
    def _backtrack_to_level(self, target_level: int):
        while self.decision_level > target_level:
            assignments_to_remove: List[Assignment] = []
            
            for assignment in reversed(self.decision_stack):
                if assignment.decision_level == self.decision_level:
                    assignments_to_remove.append(assignment)
                else:
                    break
            
            for assignment in assignments_to_remove:
                self.decision_stack.remove(assignment)
                del self.assignment[assignment.variable]
                if assignment.variable in self.implication_graph:
                    del self.implication_graph[assignment.variable]
            
            self.decision_level -= 1
    
    def _choose_variable(self) -> Optional[str]:
        all_variables: Set[str] = set()
        for clause in self.cnf.clauses + self.learned_clauses:
            for lit in clause.literals:
                all_variables.add(lit.variable)
        
        for var in all_variables:
            if var not in self.assignment:
                return var
        return None
    
    def _make_decision(self, variable: str, value: bool):
        self.decision_level += 1
        assignment = Assignment(variable, value, self.decision_level, None)
        self.decision_stack.append(assignment)
        self.assignment[variable] = value
        
        node = ImplicationNode(variable, value, self.decision_level, None, [])
        self.implication_graph[variable] = node
    
    def _add_implication(self, variable: str, value: bool, reason: Clause):
        assignment = Assignment(variable, value, self.decision_level, reason)
        self.decision_stack.append(assignment)
        self.assignment[variable] = value
        
        antecedents: List[str] = []
        for lit in reason.literals:
            if lit.variable != variable and lit.variable in self.assignment:
                antecedents.append(lit.variable)
        
        node = ImplicationNode(variable, value, self.decision_level, reason, antecedents)
        self.implication_graph[variable] = node
    
    def _all_clauses_satisfied(self) -> bool:
        for clause in self.cnf.clauses + self.learned_clauses:
            satisfied = False
            for lit in clause.literals:
                if lit.variable in self.assignment:
                    lit_value = self.assignment[lit.variable]
                    if (not lit.negated and lit_value) or (lit.negated and not lit_value):
                        satisfied = True
                        break
            if not satisfied:
                return False
        return True
    
    def solve(self) -> DecisionResult:
        while True:
            conflict_clause = self._unit_propagation()
            
            if conflict_clause is not None:
                learned_clause = self._analyze_conflict(conflict_clause)
                self.learned_clauses.append(learned_clause)
                
                if self.decision_level == 0:
                    return DecisionResult.UNSAT
                
                backjump_level = self._backjump(learned_clause)
                self._backtrack_to_level(backjump_level)
                continue
            
            if self._all_clauses_satisfied():
                return DecisionResult.SAT
            
            variable = self._choose_variable()
            if variable is None:
                return DecisionResult.SAT
            
            self._make_decision(variable, True)