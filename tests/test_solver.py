# pyright: reportPrivateUsage=false
# pylint: disable=protected-access

import pytest
from src.solver import DPLLSolver, DecisionResult, Assignment, CDCLSolver, ImplicationNode
from src.logic_ast import CNFFormula, Clause, Literal


P = Literal("p", negated=False)
P_NEG = Literal("p", negated=True)
Q = Literal("q", negated=False)
Q_NEG = Literal("q", negated=True)
R = Literal("r", negated=False)
R_NEG = Literal("r", negated=True)


class TestDPLLSolver:
    
    def test_init(self):
        cnf = CNFFormula([])
        solver = DPLLSolver(cnf)
        assert solver.cnf == cnf
        assert solver.assignment == {}
    
    def test_evaluate_clause_satisfied(self):
        clause = Clause([P, Q_NEG])
        cnf = CNFFormula([clause])
        solver = DPLLSolver(cnf)

        assignment = {"p": True}
        result = solver._evaluate_clause(clause, assignment)
        assert result is True
    
    def test_evaluate_clause_unsatisfied(self):
        clause = Clause([P, Q])
        cnf = CNFFormula([clause])
        solver = DPLLSolver(cnf)

        assignment = {"p": False, "q": False}
        result = solver._evaluate_clause(clause, assignment)
        assert result is False
    
    def test_evaluate_clause_unassigned(self):
        clause = Clause([P, Q])
        cnf = CNFFormula([clause])
        solver = DPLLSolver(cnf)

        assignment = {}
        result = solver._evaluate_clause(clause, assignment)
        assert result is None
    
    def test_evaluate_clause_partial_assignment(self):
        clause = Clause([P, Q])
        cnf = CNFFormula([clause])
        solver = DPLLSolver(cnf)

        assignment = {"p": False}
        result = solver._evaluate_clause(clause, assignment)
        assert result is None
    
    def test_unit_propagation_success(self):
        clause = Clause([P])
        cnf = CNFFormula([clause])
        solver = DPLLSolver(cnf)

        assignment = {}
        result = solver._unit_propagation(assignment)
        assert result is True
        assert assignment["p"] is True
    
    def test_unit_propagation_conflict(self):
        clause1 = Clause([P])
        clause2 = Clause([P_NEG])
        cnf = CNFFormula([clause1, clause2])
        solver = DPLLSolver(cnf)

        assignment = {}
        result = solver._unit_propagation(assignment)
        assert result is False
    
    def test_unit_propagation_chain(self):
        clause1 = Clause([P])
        clause2 = Clause([Q_NEG])
        clause3 = Clause([Q, R])
        cnf = CNFFormula([clause1, clause2, clause3])
        solver = DPLLSolver(cnf)

        assignment = {}
        result = solver._unit_propagation(assignment)
        assert result is True
        assert assignment["p"] is True
        assert assignment["q"] is False
        assert assignment["r"] is True
    
    def test_choose_variable(self):
        clause = Clause([P, Q])
        cnf = CNFFormula([clause])
        solver = DPLLSolver(cnf)

        assignment = {}
        var = solver._choose_variable(assignment)
        assert var in ["p", "q"]

        assignment["p"] = True
        var = solver._choose_variable(assignment)
        assert var == "q"

        assignment["q"] = False
        # Now all variables assigned, but our new implementation raises RuntimeError
        with pytest.raises(RuntimeError):
            solver._choose_variable(assignment)
    
    def test_all_clauses_satisfied(self):
        clause1 = Clause([P])
        clause2 = Clause([Q])
        cnf = CNFFormula([clause1, clause2])
        solver = DPLLSolver(cnf)

        assignment = {}
        assert solver._all_clauses_satisfied(assignment) is False

        assignment["p"] = True
        assert solver._all_clauses_satisfied(assignment) is False

        assignment["q"] = True
        assert solver._all_clauses_satisfied(assignment) is True
    
    def test_pure_literal_elimination_positive(self):
        clause1 = Clause([P, Q])
        clause2 = Clause([P, R_NEG])
        cnf = CNFFormula([clause1, clause2])
        solver = DPLLSolver(cnf)

        assignment = {}
        solver._pure_literal_elimination(assignment)
        assert assignment["p"] is True
    
    def test_pure_literal_elimination_negative(self):
        clause1 = Clause([P, Q_NEG])
        clause2 = Clause([Q_NEG, R])
        cnf = CNFFormula([clause1, clause2])
        solver = DPLLSolver(cnf)

        assignment = {}
        solver._pure_literal_elimination(assignment)
        assert assignment["q"] is False
    
    def test_pure_literal_elimination_mixed_polarity(self):
        clause1 = Clause([P, Q])
        clause2 = Clause([P_NEG, Q])
        cnf = CNFFormula([clause1, clause2])
        solver = DPLLSolver(cnf)

        assignment = {}
        solver._pure_literal_elimination(assignment)
        assert "p" not in assignment
        assert assignment["q"] is True
    
    def test_pure_literal_elimination_already_satisfied(self):
        clause1 = Clause([P])
        clause2 = Clause([Q])
        cnf = CNFFormula([clause1, clause2])
        solver = DPLLSolver(cnf)

        assignment = {"p": True}
        solver._pure_literal_elimination(assignment)
        assert assignment["q"] is True
    
    def test_solve_simple_sat(self):
        clause = Clause([P])
        cnf = CNFFormula([clause])
        solver = DPLLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert solver.assignment["p"] is True
    
    def test_solve_simple_unsat(self):
        clause1 = Clause([P])
        clause2 = Clause([P_NEG])
        cnf = CNFFormula([clause1, clause2])
        solver = DPLLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.UNSAT
    
    def test_solve_empty_formula(self):
        cnf = CNFFormula([])
        solver = DPLLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
    
    def test_solve_two_variables_sat(self):
        clause1 = Clause([P, Q])
        clause2 = Clause([P_NEG, Q])
        cnf = CNFFormula([clause1, clause2])
        solver = DPLLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert solver.assignment["q"] is True
    
    def test_solve_horn_clause_sat(self):
        clause1 = Clause([P_NEG, Q])
        clause2 = Clause([Q_NEG, R])
        clause3 = Clause([P])
        cnf = CNFFormula([clause1, clause2, clause3])
        solver = DPLLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert solver.assignment["p"] is True
        assert solver.assignment["q"] is True
        assert solver.assignment["r"] is True
    
    def test_solve_requires_backtracking(self):
        clause1 = Clause([P, Q])
        clause2 = Clause([P, Q_NEG])
        clause3 = Clause([P_NEG, R])
        clause4 = Clause([P_NEG, R_NEG])
        cnf = CNFFormula([clause1, clause2, clause3, clause4])
        solver = DPLLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.UNSAT
    
    def test_solve_three_sat_problem(self):
        clause1 = Clause([P, Q, R])
        clause2 = Clause([P_NEG, Q_NEG, R])
        clause3 = Clause([P, Q_NEG, R_NEG])
        cnf = CNFFormula([clause1, clause2, clause3])
        solver = DPLLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
    
    def test_solve_pure_literal_elimination_case(self):
        clause1 = Clause([P, Q_NEG])
        clause2 = Clause([P, R])
        clause3 = Clause([Q_NEG, R])
        cnf = CNFFormula([clause1, clause2, clause3])
        solver = DPLLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert solver.assignment["p"] is True
        assert solver.assignment["q"] is False
        assert solver.assignment["r"] is True
    
    def test_solve_unit_propagation_chain(self):
        clause1 = Clause([P])
        clause2 = Clause([P_NEG, Q])
        clause3 = Clause([Q_NEG, R])
        cnf = CNFFormula([clause1, clause2, clause3])
        solver = DPLLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert solver.assignment["p"] is True
        assert solver.assignment["q"] is True
        assert solver.assignment["r"] is True
    
    def test_solve_complex_unsat(self):
        clause1 = Clause([P, Q])
        clause2 = Clause([P, Q_NEG])
        clause3 = Clause([P_NEG, Q])
        clause4 = Clause([P_NEG, Q_NEG])
        clause5 = Clause([R])
        clause6 = Clause([R_NEG])
        cnf = CNFFormula([clause1, clause2, clause3, clause4, clause5, clause6])
        solver = DPLLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.UNSAT
    
    def test_solve_all_variables_assigned(self):
        clause1 = Clause([P])
        clause2 = Clause([Q])
        cnf = CNFFormula([clause1, clause2])
        solver = DPLLSolver(cnf)
        
        solver.assignment["p"] = True
        solver.assignment["q"] = True
        
        result = solver.solve()
        assert result == DecisionResult.SAT
    
    def test_solve_pure_literal_elimination_unsat_case(self):
        # Test scenario where pure literal elimination would detect UNSAT
        # Create a formula that becomes unsatisfiable after pure literal assignment
        clause1 = Clause([P])      # Pure literal: p must be True
        clause2 = Clause([P_NEG])  # Conflict: p must be False
        cnf = CNFFormula([clause1, clause2])
        solver = DPLLSolver(cnf)

        result = solver.solve()
        assert result == DecisionResult.UNSAT
    


class TestCDCLSolver:
    
    def test_init(self):
        cnf = CNFFormula([])
        solver = CDCLSolver(cnf)
        assert solver.cnf == cnf
        assert solver.assignment == {}
        assert solver.decision_stack == []
        assert solver.learned_clauses == []
        assert solver.decision_level == 0
        assert solver.implication_graph == {}
    
    def test_make_decision(self):
        cnf = CNFFormula([])
        solver = CDCLSolver(cnf)
        
        solver._make_decision("p", True)
        
        assert solver.assignment["p"] is True
        assert solver.decision_level == 1
        assert len(solver.decision_stack) == 1
        
        assignment = solver.decision_stack[0]
        assert assignment.variable == "p"
        assert assignment.value is True
        assert assignment.decision_level == 1
        assert assignment.reason is None
        
        node = solver.implication_graph["p"]
        assert node.variable == "p"
        assert node.value is True
        assert node.decision_level == 1
        assert node.reason is None
        assert node.antecedents == []
    
    def test_add_implication(self):
        reason_clause = Clause([P, Q_NEG])
        cnf = CNFFormula([reason_clause])
        solver = CDCLSolver(cnf)

        solver.assignment["q"] = False
        solver.implication_graph["q"] = ImplicationNode("q", False, 0)
        solver._add_implication("p", True, reason_clause)

        assert solver.assignment["p"] is True
        assert len(solver.decision_stack) == 1

        assignment = solver.decision_stack[0]
        assert assignment.variable == "p"
        assert assignment.value is True
        assert assignment.decision_level == 0
        assert assignment.reason == reason_clause

        node = solver.implication_graph["p"]
        assert node.variable == "p"
        assert node.value is True
        assert node.decision_level == 0
        assert node.reason == reason_clause
        antecedent_vars = [n.variable for n in node.antecedents]
        assert "q" in antecedent_vars
    
    def test_choose_variable_with_learned_clauses(self):
        original_clause = Clause([P])
        learned_clause = Clause([Q, R])
        
        cnf = CNFFormula([original_clause])
        solver = CDCLSolver(cnf)
        solver.learned_clauses.append(learned_clause)
        
        solver.assignment["p"] = True
        var = solver._choose_variable()
        assert var in ["q", "r"]
        
        solver.assignment["q"] = True
        var = solver._choose_variable()
        assert var == "r"
        
        solver.assignment["r"] = False
        var = solver._choose_variable()
        assert var is None
    
    
    def test_implication_node_creation(self):
        node = ImplicationNode("p", True, 2, None, ["q", "r"])
        assert node.variable == "p"
        assert node.value is True
        assert node.decision_level == 2
        assert node.reason is None
        assert node.antecedents == ["q", "r"]
    
    def test_implication_node_default_antecedents(self):
        node = ImplicationNode("p", False, 1)
        assert node.antecedents == []
    
    def test_assignment_with_reason(self):
        reason_clause = Clause([P])
        assignment = Assignment("p", True, 1, reason_clause)
        
        assert assignment.variable == "p"
        assert assignment.value is True
        assert assignment.decision_level == 1
        assert assignment.reason == reason_clause
    
    def test_multiple_decisions_increment_level(self):
        cnf = CNFFormula([])
        solver = CDCLSolver(cnf)
        
        solver._make_decision("p", True)
        assert solver.decision_level == 1
        
        solver._make_decision("q", False)
        assert solver.decision_level == 2
        
        assert solver.implication_graph["p"].decision_level == 1
        assert solver.implication_graph["q"].decision_level == 2
    
    def test_unit_propagation_no_conflict(self):
        clause = Clause([P])
        cnf = CNFFormula([clause])
        solver = CDCLSolver(cnf)
        
        conflict = solver._unit_propagation()
        assert conflict is None
        assert solver.assignment["p"] is True
        assert "p" in solver.implication_graph
        assert solver.implication_graph["p"].reason == clause
    
    def test_unit_propagation_with_conflict(self):
        clause1 = Clause([P])
        clause2 = Clause([P_NEG])
        cnf = CNFFormula([clause1, clause2])
        solver = CDCLSolver(cnf)
        
        conflict = solver._unit_propagation()
        assert conflict == clause2
        assert solver.assignment["p"] is True
    
    def test_unit_propagation_chain(self):
        clause1 = Clause([P])
        clause2 = Clause([P_NEG, Q])
        clause3 = Clause([Q_NEG, R])
        cnf = CNFFormula([clause1, clause2, clause3])
        solver = CDCLSolver(cnf)
        
        conflict = solver._unit_propagation()
        assert conflict is None
        assert solver.assignment["p"] is True
        assert solver.assignment["q"] is True
        assert solver.assignment["r"] is True
        
        assert solver.implication_graph["p"].reason == clause1
        assert solver.implication_graph["q"].reason == clause2
        assert solver.implication_graph["r"].reason == clause3
        q_antecedents = [n.variable for n in solver.implication_graph["q"].antecedents]
        r_antecedents = [n.variable for n in solver.implication_graph["r"].antecedents]
        assert "p" in q_antecedents
        assert "q" in r_antecedents
    
    def test_unit_propagation_with_learned_clauses(self):
        original_clause = Clause([P])
        learned_clause = Clause([P_NEG, Q])
        
        cnf = CNFFormula([original_clause])
        solver = CDCLSolver(cnf)
        solver.learned_clauses.append(learned_clause)
        
        conflict = solver._unit_propagation()
        assert conflict is None
        assert solver.assignment["p"] is True
        assert solver.assignment["q"] is True
        assert solver.implication_graph["q"].reason == learned_clause
    
    def test_evaluate_clause_satisfied(self):
        clause = Clause([P, Q_NEG])
        cnf = CNFFormula([clause])
        solver = CDCLSolver(cnf)
        
        solver.assignment["p"] = True
        result = solver._evaluate_clause(clause)
        assert result is True
    
    def test_evaluate_clause_unsatisfied(self):
        clause = Clause([P, Q])
        cnf = CNFFormula([clause])
        solver = CDCLSolver(cnf)
        
        solver.assignment["p"] = False
        solver.assignment["q"] = False
        result = solver._evaluate_clause(clause)
        assert result is False
    
    def test_evaluate_clause_unassigned(self):
        clause = Clause([P, Q])
        cnf = CNFFormula([clause])
        solver = CDCLSolver(cnf)
        
        result = solver._evaluate_clause(clause)
        assert result is None
    
    def test_evaluate_clause_partial_assignment(self):
        clause = Clause([P, Q])
        cnf = CNFFormula([clause])
        solver = CDCLSolver(cnf)
        
        solver.assignment["p"] = False
        result = solver._evaluate_clause(clause)
        assert result is None
    
    def test_backtrack_to_level_single_level(self):
        cnf = CNFFormula([])
        solver = CDCLSolver(cnf)
        
        solver._make_decision("p", True)
        solver._make_decision("q", False)
        
        assert solver.decision_level == 2
        assert solver.assignment["p"] is True
        assert solver.assignment["q"] is False
        assert len(solver.decision_stack) == 2
        assert len(solver.implication_graph) == 2
        
        solver._backtrack_to_level(1)
        
        assert solver.decision_level == 1
        assert solver.assignment["p"] is True
        assert "q" not in solver.assignment
        assert len(solver.decision_stack) == 1
        assert "p" in solver.implication_graph
        assert "q" not in solver.implication_graph
    
    def test_backtrack_to_level_multiple_levels(self):
        cnf = CNFFormula([])
        solver = CDCLSolver(cnf)
        
        solver._make_decision("p", True)
        solver._make_decision("q", False)
        solver._make_decision("r", True)
        
        assert solver.decision_level == 3
        assert len(solver.assignment) == 3
        
        solver._backtrack_to_level(1)
        
        assert solver.decision_level == 1
        assert solver.assignment["p"] is True
        assert "q" not in solver.assignment
        assert "r" not in solver.assignment
        assert len(solver.decision_stack) == 1
        assert len(solver.implication_graph) == 1
    
    def test_backtrack_to_level_zero(self):
        cnf = CNFFormula([])
        solver = CDCLSolver(cnf)
        
        solver._make_decision("p", True)
        solver._make_decision("q", False)
        
        solver._backtrack_to_level(0)
        
        assert solver.decision_level == 0
        assert len(solver.assignment) == 0
        assert len(solver.decision_stack) == 0
        assert len(solver.implication_graph) == 0
    
    def test_backtrack_to_level_with_implications(self):
        reason_clause = Clause([P, Q])
        cnf = CNFFormula([reason_clause])
        solver = CDCLSolver(cnf)
        
        solver._make_decision("r", True)
        solver._add_implication("p", True, reason_clause)
        solver._make_decision("s", False)
        
        assert solver.decision_level == 2
        assert len(solver.assignment) == 3
        assert len(solver.implication_graph) == 3
        
        solver._backtrack_to_level(1)
        
        assert solver.decision_level == 1
        assert solver.assignment["r"] is True
        assert solver.assignment["p"] is True
        assert "s" not in solver.assignment
        assert len(solver.decision_stack) == 2
        assert len(solver.implication_graph) == 2
    
    def test_backtrack_to_level_current_level(self):
        cnf = CNFFormula([])
        solver = CDCLSolver(cnf)
        
        solver._make_decision("p", True)
        initial_level = solver.decision_level
        initial_assignments = dict(solver.assignment)
        
        solver._backtrack_to_level(initial_level)
        
        assert solver.decision_level == initial_level
        assert solver.assignment == initial_assignments
    
    def test_backtrack_to_level_mixed_assignments_same_level(self):
        reason1 = Clause([P])
        reason2 = Clause([Q])
        
        cnf = CNFFormula([])
        solver = CDCLSolver(cnf)
        
        solver._make_decision("s", True)
        solver._add_implication("p", True, reason1)
        solver._add_implication("q", False, reason2)
        solver._make_decision("t", False)
        
        assert solver.decision_level == 2
        assert len(solver.assignment) == 4
        
        solver._backtrack_to_level(1)
        
        assert solver.decision_level == 1
        assert solver.assignment["s"] is True
        assert solver.assignment["p"] is True
        assert solver.assignment["q"] is False
        assert "t" not in solver.assignment
        assert len(solver.decision_stack) == 3
        assert len(solver.implication_graph) == 3
    
    def test_solve_simple_sat(self):
        clause = Clause([P])
        cnf = CNFFormula([clause])
        solver = CDCLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert solver.assignment["p"] is True
    
    def test_solve_simple_unsat(self):
        clause1 = Clause([P])
        clause2 = Clause([P_NEG])
        cnf = CNFFormula([clause1, clause2])
        solver = CDCLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.UNSAT
    
    def test_solve_empty_formula(self):
        cnf = CNFFormula([])
        solver = CDCLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
    
    def test_solve_with_unit_propagation(self):
        clause1 = Clause([P])
        clause2 = Clause([P_NEG, Q])
        cnf = CNFFormula([clause1, clause2])
        solver = CDCLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert solver.assignment["p"] is True
        assert solver.assignment["q"] is True
    
    def test_solve_with_decision_making(self):
        clause = Clause([P, Q])
        cnf = CNFFormula([clause])
        solver = CDCLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert (solver.assignment.get("p", False) is True or solver.assignment.get("q", False) is True)
    
    def test_solve_with_conflict_and_learning(self):
        clause1 = Clause([P, Q])
        clause2 = Clause([P_NEG])
        clause3 = Clause([Q_NEG])
        cnf = CNFFormula([clause1, clause2, clause3])
        solver = CDCLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.UNSAT
        assert len(solver.learned_clauses) > 0
    
    def test_solve_horn_clauses(self):
        clause1 = Clause([P_NEG, Q])
        clause2 = Clause([Q_NEG, R])
        clause3 = Clause([P])
        cnf = CNFFormula([clause1, clause2, clause3])
        solver = CDCLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert solver.assignment["p"] is True
        assert solver.assignment["q"] is True
        assert solver.assignment["r"] is True
    
    def test_solve_multiple_decisions(self):
        clause1 = Clause([P, Q])
        clause2 = Clause([R])
        cnf = CNFFormula([clause1, clause2])
        solver = CDCLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert solver.assignment["r"] is True
        assert (solver.assignment.get("p", False) is True or solver.assignment.get("q", False) is True)
    
    def test_solve_with_learned_clauses_consideration(self):
        clause1 = Clause([P])
        clause2 = Clause([Q])
        cnf = CNFFormula([clause1, clause2])
        solver = CDCLSolver(cnf)
        
        learned_clause = Clause([R])
        solver.learned_clauses.append(learned_clause)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert solver.assignment["p"] is True
        assert solver.assignment["q"] is True
        assert solver.assignment["r"] is True
    
    def test_solve_conflict_at_decision_level_zero(self):
        clause1 = Clause([P])
        clause2 = Clause([P_NEG])
        cnf = CNFFormula([clause1, clause2])
        solver = CDCLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.UNSAT
    
    def test_solve_all_variables_assigned_early(self):
        clause1 = Clause([P])
        clause2 = Clause([Q])
        cnf = CNFFormula([clause1, clause2])
        solver = CDCLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert solver.assignment["p"] is True
        assert solver.assignment["q"] is True
    
    def test_solve_no_variables_to_choose(self):
        cnf = CNFFormula([])
        solver = CDCLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert len(solver.assignment) == 0
    
    def test_solve_complex_satisfiable(self):
        clause1 = Clause([P, Q])
        clause2 = Clause([P_NEG, R])
        clause3 = Clause([Q_NEG, R])
        cnf = CNFFormula([clause1, clause2, clause3])
        solver = CDCLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        
        if "p" in solver.assignment and "q" in solver.assignment:
            if solver.assignment["p"] and solver.assignment["q"]:
                assert True
            else:
                assert solver.assignment["r"] is True
        else:
            assert solver.assignment.get("r", False) is True
    
    def test_solve_with_backtracking_scenario(self):
        clause1 = Clause([P, Q])
        clause2 = Clause([P, Q_NEG])
        clause3 = Clause([P_NEG, R])
        clause4 = Clause([R_NEG])
        cnf = CNFFormula([clause1, clause2, clause3, clause4])
        solver = CDCLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.UNSAT
    
    def test_backjump_method(self):
        clause = Clause([P])
        cnf = CNFFormula([clause])
        solver = CDCLSolver(cnf)
        
        learned_clause = Clause([P])
        level = solver._backjump(learned_clause)
        assert level == 0
    
    def test_backjump_scenario_calls_backtrack(self):
        clause1 = Clause([P, Q])
        cnf = CNFFormula([clause1])
        
        class BackjumpTestSolver(CDCLSolver):
            def __init__(self, cnf: CNFFormula):
                super().__init__(cnf)
                self.conflict_forced = False
                
            def _unit_propagation(self):
                if self.decision_level > 0 and not self.conflict_forced:
                    self.conflict_forced = True
                    fake_literal = Literal("fake_conflict", negated=True)
                    return Clause([fake_literal])
                return super()._unit_propagation()
                
        test_solver = BackjumpTestSolver(cnf)
        result = test_solver.solve()
        assert result in [DecisionResult.SAT, DecisionResult.UNSAT]
        assert len(test_solver.learned_clauses) > 0 or not test_solver.conflict_forced
    
    def test_choose_variable_returns_none_scenario(self):
        clause = Clause([P])
        cnf = CNFFormula([clause])
        solver = CDCLSolver(cnf)
        
        solver.assignment["p"] = True
        variable = solver._choose_variable()
        assert variable is None
        
        class TestCDCLSolver(CDCLSolver):
            def __init__(self, cnf: CNFFormula):
                super().__init__(cnf)
                self.force_none = False
                
            def _choose_variable(self):
                if self.force_none:
                    return None
                return super()._choose_variable()
                
            def _all_clauses_satisfied(self):
                if not hasattr(self, '_first_check'):
                    self._first_check = True
                    self.force_none = True
                    return False
                return True
        
        test_solver = TestCDCLSolver(cnf)
        result = test_solver.solve()
        assert result == DecisionResult.SAT
    
    def test_analyze_conflict_1uip(self):
        clause1 = Clause([P, Q])
        clause2 = Clause([P_NEG, R])
        clause3 = Clause([Q_NEG, R_NEG])
        cnf = CNFFormula([clause1, clause2, clause3])
        solver = CDCLSolver(cnf)
        
        solver._make_decision("p", True)
        solver._add_implication("q", True, clause1)
        solver._add_implication("r", True, clause2)
        
        conflict_clause = clause3
        learned = solver._analyze_conflict(conflict_clause)
        
        assert len(learned.literals) >= 1
        
    def test_analyze_conflict_decision_level_zero(self):
        conflict_clause = Clause([P])
        cnf = CNFFormula([])
        solver = CDCLSolver(cnf)
        
        result = solver._analyze_conflict(conflict_clause)
        assert result == conflict_clause
        
    def test_backjump_single_literal(self):
        learned_clause = Clause([P])
        cnf = CNFFormula([])
        solver = CDCLSolver(cnf)
        
        level = solver._backjump(learned_clause)
        assert level == 0
        
    def test_backjump_multiple_levels(self):
        learned_clause = Clause([P, Q, R])
        cnf = CNFFormula([])
        solver = CDCLSolver(cnf)
        
        solver._make_decision("p", True)
        solver._make_decision("q", True)
        solver._make_decision("r", True)
        
        level = solver._backjump(learned_clause)
        assert level == 2
        
    def test_backjump_with_implications(self):
        reason = Clause([P])
        learned_clause = Clause([P, R])
        cnf = CNFFormula([])
        solver = CDCLSolver(cnf)
        
        solver._make_decision("p", True)
        solver._make_decision("q", True)
        solver._add_implication("r", True, reason)
        
        level = solver._backjump(learned_clause)
        assert level == 1
    
    def test_analyze_conflict_edge_cases(self):
        conflict_clause = Clause([P, Q])
        cnf = CNFFormula([])
        solver = CDCLSolver(cnf)
        solver.decision_level = 1
        
        result = solver._analyze_conflict(conflict_clause)
        assert result == conflict_clause
        
        solver._make_decision("p", True)
        solver._make_decision("q", True)
        
        reason_p = Clause([P_NEG, Q])
        solver.implication_graph["p"].reason = reason_p
        
        result = solver._analyze_conflict(conflict_clause)
        assert len(result.literals) >= 1
        
    def test_backjump_with_same_levels(self):
        learned_clause = Clause([P, Q, R])
        cnf = CNFFormula([])
        solver = CDCLSolver(cnf)
        
        solver._make_decision("p", True)
        solver._make_decision("q", True)
        solver._make_decision("r", True)
        solver.implication_graph["q"].decision_level = 1
        
        level = solver._backjump(learned_clause)
        assert level == 1
    
    def test_analyze_conflict_recursive_case(self):
        cnf = CNFFormula([])
        solver = CDCLSolver(cnf)
        
        solver._make_decision("p", True)
        solver._make_decision("q", True) 
        solver._make_decision("r", True)
        
        reason_p = Clause([P_NEG, Q, R])
        reason_q = Clause([Q_NEG, R])
        
        solver.implication_graph["p"].reason = reason_p
        solver.implication_graph["q"].reason = reason_q
        
        conflict_clause = Clause([P_NEG, Q_NEG])
        
        result = solver._analyze_conflict(conflict_clause)
        assert len(result.literals) >= 1
        
    def test_analyze_conflict_duplicate_literals(self):
        cnf = CNFFormula([])
        solver = CDCLSolver(cnf)
        
        solver._make_decision("p", True)
        solver._make_decision("q", True)
        
        reason_p = Clause([P, Q])
        solver.implication_graph["p"].reason = reason_p
        
        conflict_clause = Clause([P, Q])
        
        result = solver._analyze_conflict(conflict_clause)
        assert len(result.literals) >= 1
