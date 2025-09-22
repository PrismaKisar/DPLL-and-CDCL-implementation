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
        while True:
            propagated = False

            for clause in self.cnf.clauses + self.learned_clauses:
                clause_state = self._evaluate_clause(clause)

                # Check for conflict
                if clause_state is False:
                    return clause

                # Skip satisfied or undetermined non-unit clauses
                if clause_state is True:
                    continue

                # Find unassigned literals in undetermined clause
                unassigned_literals = [
                    literal for literal in clause.literals
                    if literal.variable not in self.assignment
                ]

                # Process unit clause (exactly one unassigned literal)
                if len(unassigned_literals) == 1:
                    unit_literal = unassigned_literals[0]
                    implied_value = not unit_literal.negated
                    self._add_implication(unit_literal.variable, implied_value, clause)
                    propagated = True

            if not propagated:
                break

        return None
    
    def _evaluate_clause(self, clause: Clause) -> Optional[bool]:
        """Evaluate a clause under the current assignment.

        Args:
            clause: Clause to evaluate

        Returns:
            True if clause satisfied, False if unsatisfied, None if undetermined
        """
        unassigned_count = 0

        for literal in clause.literals:
            if literal.variable not in self.assignment:
                unassigned_count += 1
                continue

            # Check if this literal is satisfied
            variable_value = self.assignment[literal.variable]
            literal_satisfied = (not literal.negated and variable_value) or (literal.negated and not variable_value)

            if literal_satisfied:
                return True

        # No literal satisfied the clause
        return False if unassigned_count == 0 else None
    
    def _analyze_conflict(self, conflict_clause: Clause) -> Clause:
        """Analyze conflict to derive learned clause using First Unique Implication Point (1UIP).

        Performs iterative resolution starting from the conflict clause until reaching
        a clause with at most one variable from the current decision level (1UIP condition).

        Args:
            conflict_clause: The clause that caused the conflict

        Returns:
            Learned clause that prevents similar conflicts
        """
        # Base case: conflicts at decision level 0 are unresolvable
        if self.decision_level == 0:
            return conflict_clause

        resolvent_clause = conflict_clause

        # Iteratively resolve until 1UIP condition is satisfied
        while not self._is_first_unique_implication_point(resolvent_clause):
            # Find the next variable to resolve on (most recently assigned at current level)
            resolution_variable = self._find_most_recent_current_level_variable(resolvent_clause)

            if not self._can_resolve_on_variable(resolution_variable):
                # Cannot resolve further - return current clause as learned clause
                return resolvent_clause

            # Perform resolution step
            reason_clause = self.implication_graph[resolution_variable].reason
            resolvent_clause = self._resolve_clauses(
                resolvent_clause,
                reason_clause,
                resolution_variable
            )

        return resolvent_clause

    def _is_first_unique_implication_point(self, clause: Clause) -> bool:
        """Check if clause satisfies 1UIP condition.

        1UIP condition: at most one variable from current decision level.

        Args:
            clause: Clause to check

        Returns:
            True if clause satisfies 1UIP condition
        """
        return self._count_current_level_variables(clause) <= 1

    def _count_current_level_variables(self, clause: Clause) -> int:
        """Count variables in clause that belong to current decision level.

        Args:
            clause: Clause to analyze

        Returns:
            Number of variables from current decision level
        """
        return sum(
            1 for literal in clause.literals
            if self._is_variable_at_current_level(literal.variable)
        )

    def _find_most_recent_current_level_variable(self, clause: Clause) -> Optional[str]:
        """Find the most recently assigned variable in clause at current decision level.

        Args:
            clause: Clause to search in

        Returns:
            Most recently assigned variable at current level, None if none found
        """
        current_level_variables = [
            literal.variable for literal in clause.literals
            if self._is_variable_at_current_level(literal.variable)
        ]

        if not current_level_variables:
            return None

        # Find variable with highest assignment index (most recent)
        return max(
            current_level_variables,
            key=self._find_variable_assignment_index
        )

    def _is_variable_at_current_level(self, variable: str) -> bool:
        """Check if variable belongs to current decision level.

        Args:
            variable: Variable to check

        Returns:
            True if variable is assigned at current decision level
        """
        return (variable in self.implication_graph and
                self.implication_graph[variable].decision_level == self.decision_level)

    def _find_variable_assignment_index(self, variable: str) -> int:
        """Find index of variable assignment in decision stack at current level.

        Args:
            variable: Variable to find

        Returns:
            Index in decision stack, -1 if not found
        """
        for index, assignment in enumerate(self.decision_stack):
            if (assignment.variable == variable and
                assignment.decision_level == self.decision_level):
                return index
        return -1

    def _can_resolve_on_variable(self, variable: Optional[str]) -> bool:
        """Check if resolution can be performed on the given variable.

        Args:
            variable: Variable to check for resolution

        Returns:
            True if variable can be used for resolution
        """
        if variable is None:
            return False

        implication_node = self.implication_graph.get(variable)
        return (implication_node is not None and
                implication_node.reason is not None)

    def _resolve_clauses(self, clause1: Clause, clause2: Clause, pivot_var: str) -> Clause:
        """Resolve two clauses on pivot variable.

        Args:
            clause1: First clause in resolution
            clause2: Second clause in resolution
            pivot_var: Variable to resolve on

        Returns:
            Resolved clause without pivot variable
        """
        resolved_literals: List[Literal] = []

        # Collect all non-pivot literals from both clauses
        for clause in [clause1, clause2]:
            for literal in clause.literals:
                if (literal.variable != pivot_var and
                    not self._literal_exists(literal, resolved_literals)):
                    resolved_literals.append(literal)

        return Clause(resolved_literals)

    def _literal_exists(self, literal: Literal, literal_list: List[Literal]) -> bool:
        """Check if literal already exists in list.

        Args:
            literal: Literal to search for
            literal_list: List of literals to search in

        Returns:
            True if literal exists in list, False otherwise
        """
        return any(
            existing_literal.variable == literal.variable and
            existing_literal.negated == literal.negated
            for existing_literal in literal_list
        )
    
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

        # Collect decision levels from literals in the learned clause
        decision_levels = [
            self.implication_graph[literal.variable].decision_level
            for literal in learned_clause.literals
            if literal.variable in self.implication_graph
        ]

        if len(decision_levels) <= 1:
            return 0

        # Return second highest decision level from the variables in the learned clause
        unique_sorted_levels = sorted(set(decision_levels), reverse=True)
        return unique_sorted_levels[1] if len(unique_sorted_levels) > 1 else 0
    
    def _backtrack_to_level(self, target_level: int):
        """Backtrack to specified decision level.

        Removes all assignments and implications made at levels
        higher than the target level.

        Args:
            target_level: Decision level to backtrack to
        """
        while self.decision_level > target_level:
            self._remove_current_level_assignments()
            self.decision_level -= 1

    def _remove_current_level_assignments(self):
        """Remove all assignments from the current decision level.

        Efficiently removes assignments from the end of decision stack
        and updates assignment dictionary and implication graph.
        """
        # Remove assignments from current level (they're at the end of the stack)
        while (self.decision_stack and
               self.decision_stack[-1].decision_level == self.decision_level):
            assignment = self.decision_stack.pop()
            del self.assignment[assignment.variable]
            if assignment.variable in self.implication_graph:
                del self.implication_graph[assignment.variable]
    
    def _choose_variable(self) -> Optional[str]:
        """Choose next unassigned variable for branching.

        Returns:
            Variable name to branch on, None if all variables assigned
        """
        # Find first unassigned variable from any clause
        for clause in self.cnf.clauses + self.learned_clauses:
            for literal in clause.literals:
                if literal.variable not in self.assignment:
                    return literal.variable
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
        # Record assignment
        assignment = Assignment(variable, value, self.decision_level, reason)
        self.decision_stack.append(assignment)
        self.assignment[variable] = value

        # Build antecedent nodes for implication graph
        antecedent_nodes = [
            self.implication_graph[literal.variable]
            for literal in reason.literals
            if (literal.variable != variable and
                literal.variable in self.implication_graph)
        ]

        # Create implication node
        node = ImplicationNode(variable, value, self.decision_level, reason, antecedent_nodes)
        self.implication_graph[variable] = node
    
    def _all_clauses_satisfied(self) -> bool:
        """Check if all clauses are satisfied by current assignment.

        Returns:
            True if all clauses satisfied, False otherwise
        """
        return all(
            self._evaluate_clause(clause) is True
            for clause in self.cnf.clauses + self.learned_clauses
        )
    
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
                result = self._handle_conflict(conflict_clause)
                if result is not None:
                    return result
                continue

            # Check for satisfiability
            if self._all_clauses_satisfied():
                return DecisionResult.SAT

            # Decide: choose variable and assign value
            if not self._make_next_decision():
                return DecisionResult.SAT

    def _handle_conflict(self, conflict_clause: Clause) -> Optional[DecisionResult]:
        """Handle conflict by learning clause and backtracking.

        Args:
            conflict_clause: The clause that caused the conflict

        Returns:
            DecisionResult.UNSAT if conflict at level 0, None to continue
        """
        # Analyze: derive learned clause from conflict
        learned_clause = self._analyze_conflict(conflict_clause)

        # Learn: add learned clause to prevent similar conflicts
        self.learned_clauses.append(learned_clause)

        # Check for unsatisfiability (conflict at decision level 0)
        if self.decision_level == 0:
            return DecisionResult.UNSAT

        # Backjump: perform non-chronological backtracking
        backjump_level = self._backjump(learned_clause)
        self._backtrack_to_level(backjump_level)

        return None

    def _make_next_decision(self) -> bool:
        """Make the next decision assignment.

        Returns:
            True if decision was made, False if no variables left to assign
        """
        variable = self._choose_variable()
        if variable is None:
            return False

        self._make_decision(variable, True)
        return True