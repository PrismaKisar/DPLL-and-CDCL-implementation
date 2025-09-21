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
        """Solve the CNF formula using DPLL algorithm.

        Returns:
            DecisionResult.SAT if formula is satisfiable, DecisionResult.UNSAT otherwise
        """
        assignment: Dict[str, bool] = {}
        return self._dpll(assignment)
    
    def _dpll(self, assignment: Dict[str, bool]) -> DecisionResult:
        """Core DPLL recursive algorithm.

        Args:
            assignment: Current partial variable assignment

        Returns:
            DecisionResult.SAT if satisfiable with this assignment, DecisionResult.UNSAT otherwise
        """
        assignment = assignment.copy()
        
        if not self._unit_propagation(assignment):
            return DecisionResult.UNSAT
        
        self._pure_literal_elimination(assignment)
        
        if self._all_clauses_satisfied(assignment):
            self.assignment = assignment
            return DecisionResult.SAT
        
        variable = self._choose_variable(assignment)

        assignment_true = assignment.copy()
        assignment_true[variable] = True
        if self._dpll(assignment_true) == DecisionResult.SAT:
            return DecisionResult.SAT
        
        assignment_false = assignment.copy()
        assignment_false[variable] = False
        return self._dpll(assignment_false)
    
    def _unit_propagation(self, assignment: Dict[str, bool]) -> bool:
        """Apply unit propagation to assignment.

        For each unit clause (only one unassigned literal), forces that literal's value.
        Continues until no more unit clauses or conflict found.

        Args:
            assignment: Variable assignment to modify

        Returns:
            False if conflict detected, True otherwise
        """
        while True:
            propagated = False

            for clause in self.cnf.clauses:
                state = self._evaluate_clause(clause, assignment)

                if state is False:
                    return False

                if state is not None:
                    continue

                # Find unit clause (exactly one unassigned literal)
                unassigned = [lit for lit in clause.literals if lit.variable not in assignment]
                if len(unassigned) == 1:
                    lit = unassigned[0]
                    assignment[lit.variable] = not lit.negated
                    propagated = True

            if not propagated:
                break

        return True
    
    def _pure_literal_elimination(self, assignment: Dict[str, bool]) -> None:
        """Eliminate pure literals from unassigned variables.

        A pure literal appears with only one polarity across all clauses.
        Can safely assign it the value that satisfies all its occurrences.

        Args:
            assignment: Variable assignment to modify
        """
        literal_polarities: Dict[str, Set[bool]] = {}

        for clause in self.cnf.clauses:
            # Skip already satisfied clauses
            if self._evaluate_clause(clause, assignment) is True:
                continue

            for lit in clause.literals:
                # Skip already assigned variables
                if lit.variable in assignment:
                    continue

                # Track polarity of this literal
                if lit.variable not in literal_polarities:
                    literal_polarities[lit.variable] = set()
                literal_polarities[lit.variable].add(not lit.negated)

        # Assign pure literals (appearing with only one polarity)
        for var, polarities in literal_polarities.items():
            if len(polarities) == 1:
                assignment[var] = list(polarities)[0]
    
    def _all_clauses_satisfied(self, assignment: Dict[str, bool]) -> bool:
        """Check if all clauses are satisfied by the current assignment.

        Args:
            assignment: Variable assignment to check

        Returns:
            True if all clauses satisfied, False otherwise
        """
        for clause in self.cnf.clauses:
            if self._evaluate_clause(clause, assignment) is not True:
                return False
        return True
    
    def _evaluate_clause(self, clause: Clause, assignment: Dict[str, bool]) -> Optional[bool]:
        """Evaluate a clause under the current assignment.

        Args:
            clause: Clause to evaluate
            assignment: Current variable assignment

        Returns:
            True if clause satisfied, False if unsatisfied, None if undetermined
        """
        satisfied = False
        unassigned_count = 0
        
        for lit in clause.literals:
            if lit.variable not in assignment:
                unassigned_count += 1
                continue

            # Check if this literal is satisfied
            lit_value = assignment[lit.variable]
            is_satisfied = (not lit.negated and lit_value) or (lit.negated and not lit_value)

            if is_satisfied:
                satisfied = True
                break
        
        if satisfied:
            return True
        elif unassigned_count == 0:
            return False
        else:
            return None
    
    def _choose_variable(self, assignment: Dict[str, bool]) -> str:
        """Choose next unassigned variable for branching.

        Args:
            assignment: Current variable assignment

        Returns:
            Variable name to branch on
        """
        all_variables: Set[str] = set()
        for clause in self.cnf.clauses:
            for lit in clause.literals:
                all_variables.add(lit.variable)
        
        for var in all_variables:
            if var not in assignment:
                return var

        # This should never happen due to DPLL invariants
        raise RuntimeError("No unassigned variables found, but not all clauses satisfied")


class CDCLSolver:
    """CDCL (Conflict-Driven Clause Learning) SAT solver.

    Implements modern SAT solving algorithm with conflict analysis,
    clause learning, and non-chronological backtracking.
    """

    def __init__(self, cnf_formula: CNFFormula):
        """Initialize CDCL solver with CNF formula.

        Args:
            cnf_formula: CNF formula to solve
        """
        self.cnf = cnf_formula
        self.assignment: Dict[str, bool] = {}
        self.decision_stack: List[Assignment] = []
        self.learned_clauses: List[Clause] = []
        self.decision_level = 0
        self.implication_graph: Dict[str, ImplicationNode] = {}
        
    def _unit_propagation(self) -> Optional[Clause]:
        """Apply unit propagation to current assignment.

        For each unit clause (only one unassigned literal), forces that literal's value.
        Continues until no more unit clauses or conflict found.

        Returns:
            Conflict clause if conflict detected, None otherwise
        """

            for clause in self.cnf.clauses + self.learned_clauses:

                    return clause


                    value = not lit.negated
                    self._add_implication(lit.variable, value, clause)

        return None
    
    def _evaluate_clause(self, clause: Clause) -> Optional[bool]:
        """Evaluate a clause under the current assignment.

        Args:
            clause: Clause to evaluate

        Returns:
            True if clause satisfied, False if unsatisfied, None if undetermined
        """
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
        """Analyze conflict to derive learned clause (1UIP).

        Uses resolution to derive a clause that captures the reason for the conflict.
        Implements First Unique Implication Point (1UIP) strategy.

        Args:
            conflict_clause: The clause that caused the conflict

        Returns:
            Learned clause to prevent similar conflicts
        """
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
        """Determine backjump level for non-chronological backtracking.

        Finds the second highest decision level in the learned clause
        to enable non-chronological backtracking.

        Args:
            learned_clause: Clause learned from conflict analysis

        Returns:
            Decision level to backjump to
        """
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
        """Backtrack to specified decision level.

        Removes all assignments and implications made at levels
        higher than the target level.

        Args:
            target_level: Decision level to backtrack to
        """
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
        """Choose next unassigned variable for branching.

        Returns:
            Variable name to branch on, None if all variables assigned
        """
        all_variables: Set[str] = set()
        for clause in self.cnf.clauses + self.learned_clauses:
            for lit in clause.literals:
                all_variables.add(lit.variable)
        
        for var in all_variables:
            if var not in self.assignment:
                return var
        return None
    
    def _make_decision(self, variable: str, value: bool):
        """Make a decision assignment at new decision level.

        Creates a new decision level and assigns the variable.
        Updates decision stack and implication graph.

        Args:
            variable: Variable to assign
            value: Value to assign to variable
        """
        self.decision_level += 1
        assignment = Assignment(variable, value, self.decision_level, None)
        self.decision_stack.append(assignment)
        self.assignment[variable] = value
        
        node = ImplicationNode(variable, value, self.decision_level, None, [])
        self.implication_graph[variable] = node
    
    def _add_implication(self, variable: str, value: bool, reason: Clause):
        """Add an implication from unit propagation.

        Records the assignment with its reason clause for conflict analysis.
        Updates assignment, decision stack, and implication graph.

        Args:
            variable: Variable to assign
            value: Value to assign to variable
            reason: Clause that forced this assignment
        """
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
        """Check if all clauses are satisfied by current assignment.

        Returns:
            True if all clauses satisfied, False otherwise
        """
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
        """Solve the CNF formula using CDCL algorithm.

        Implements Conflict-Driven Clause Learning with:
        - Unit propagation
        - Conflict analysis (1UIP)
        - Clause learning
        - Non-chronological backtracking

        Returns:
            DecisionResult.SAT if formula is satisfiable, DecisionResult.UNSAT otherwise
        """
        while True:
            # Propagate: unit propagation
            conflict_clause = self._unit_propagation()

            if conflict_clause is not None:
                # Conflict: analyze the conflict
                learned_clause = self._analyze_conflict(conflict_clause)
                # Learn: add learned clause
                self.learned_clauses.append(learned_clause)

                if self.decision_level == 0:
                    return DecisionResult.UNSAT

                # Backjump: non-chronological backtracking
                backjump_level = self._backjump(learned_clause)
                self._backtrack_to_level(backjump_level)
                continue

            if self._all_clauses_satisfied():
                return DecisionResult.SAT

            # Decide: choose variable and assign value
            variable = self._choose_variable()
            if variable is None:
                return DecisionResult.SAT

            self._make_decision(variable, True)