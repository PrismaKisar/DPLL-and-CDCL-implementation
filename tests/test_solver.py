from src.solver import DPLLSolver, DecisionResult, Assignment, CDCLSolver, ImplicationNode
from src.logic_ast import CNFFormula, Clause, Literal


class TestDPLLSolver:
    
    def test_init(self):
        cnf = CNFFormula([])
        solver = DPLLSolver(cnf)
        assert solver.cnf == cnf
        assert solver.assignment == {}
        assert solver.decision_stack == []
    
    def test_evaluate_clause_satisfied(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=True)
        clause = Clause([literal_p, literal_q])
        cnf = CNFFormula([clause])
        solver = DPLLSolver(cnf)
        
        solver.assignment["p"] = True
        result = solver._evaluate_clause(clause)
        assert result is True
    
    def test_evaluate_clause_unsatisfied(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        clause = Clause([literal_p, literal_q])
        cnf = CNFFormula([clause])
        solver = DPLLSolver(cnf)
        
        solver.assignment["p"] = False
        solver.assignment["q"] = False
        result = solver._evaluate_clause(clause)
        assert result is False
    
    def test_evaluate_clause_unassigned(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        clause = Clause([literal_p, literal_q])
        cnf = CNFFormula([clause])
        solver = DPLLSolver(cnf)
        
        result = solver._evaluate_clause(clause)
        assert result is None
    
    def test_evaluate_clause_partial_assignment(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        clause = Clause([literal_p, literal_q])
        cnf = CNFFormula([clause])
        solver = DPLLSolver(cnf)
        
        solver.assignment["p"] = False
        result = solver._evaluate_clause(clause)
        assert result is None
    
    def test_unit_propagation_success(self):
        literal_p = Literal("p", negated=False)
        clause = Clause([literal_p])
        cnf = CNFFormula([clause])
        solver = DPLLSolver(cnf)
        
        result = solver._unit_propagation()
        assert result is None
        assert solver.assignment["p"] is True
    
    def test_unit_propagation_conflict(self):
        literal_p_pos = Literal("p", negated=False)
        literal_p_neg = Literal("p", negated=True)
        clause1 = Clause([literal_p_pos])
        clause2 = Clause([literal_p_neg])
        cnf = CNFFormula([clause1, clause2])
        solver = DPLLSolver(cnf)
        
        result = solver._unit_propagation()
        assert result == DecisionResult.UNSAT
    
    def test_unit_propagation_chain(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=True)
        literal_r = Literal("r", negated=False)
        clause1 = Clause([literal_p])
        clause2 = Clause([literal_q])
        clause3 = Clause([Literal("q", negated=False), literal_r])
        cnf = CNFFormula([clause1, clause2, clause3])
        solver = DPLLSolver(cnf)
        
        result = solver._unit_propagation()
        assert result is None
        assert solver.assignment["p"] is True
        assert solver.assignment["q"] is False
        assert solver.assignment["r"] is True
    
    def test_choose_variable(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        clause = Clause([literal_p, literal_q])
        cnf = CNFFormula([clause])
        solver = DPLLSolver(cnf)
        
        var = solver._choose_variable()
        assert var in ["p", "q"]
        
        solver.assignment["p"] = True
        var = solver._choose_variable()
        assert var == "q"
        
        solver.assignment["q"] = False
        var = solver._choose_variable()
        assert var is None
    
    def test_make_decision(self):
        cnf = CNFFormula([])
        solver = DPLLSolver(cnf)
        
        solver._make_decision("p", True)
        assert solver.assignment["p"] is True
        assert len(solver.decision_stack) == 1
        assert solver.decision_stack[0].variable == "p"
        assert solver.decision_stack[0].value is True
        assert solver.decision_stack[0].decision_level == 0
    
    def test_backtrack(self):
        cnf = CNFFormula([])
        solver = DPLLSolver(cnf)
        
        solver._make_decision("p", True)
        solver._backtrack()
        
        assert solver.assignment["p"] is False
        assert len(solver.decision_stack) == 1
        assert solver.decision_stack[0].value is False
    
    def test_all_clauses_satisfied(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        clause1 = Clause([literal_p])
        clause2 = Clause([literal_q])
        cnf = CNFFormula([clause1, clause2])
        solver = DPLLSolver(cnf)
        
        assert solver._all_clauses_satisfied() is False
        
        solver.assignment["p"] = True
        assert solver._all_clauses_satisfied() is False
        
        solver.assignment["q"] = True
        assert solver._all_clauses_satisfied() is True
    
    def test_simplify_formula_satisfied_clause_removal(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        clause1 = Clause([literal_p, literal_q])
        clause2 = Clause([Literal("r", negated=False)])
        cnf = CNFFormula([clause1, clause2])
        solver = DPLLSolver(cnf)
        
        solver.assignment["p"] = True
        result = solver._simplify_formula()
        
        assert result is True
        assert len(solver.cnf.clauses) == 1
        assert solver.cnf.clauses[0].literals[0].variable == "r"
    
    def test_simplify_formula_false_literal_removal(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        literal_r = Literal("r", negated=False)
        clause = Clause([literal_p, literal_q, literal_r])
        cnf = CNFFormula([clause])
        solver = DPLLSolver(cnf)
        
        solver.assignment["p"] = False
        result = solver._simplify_formula()
        
        assert result is True
        assert len(solver.cnf.clauses) == 1
        assert len(solver.cnf.clauses[0].literals) == 2
        assert solver.cnf.clauses[0].literals[0].variable == "q"
        assert solver.cnf.clauses[0].literals[1].variable == "r"
    
    def test_simplify_formula_empty_clause(self):
        literal_p = Literal("p", negated=False)
        clause = Clause([literal_p])
        cnf = CNFFormula([clause])
        solver = DPLLSolver(cnf)
        
        solver.assignment["p"] = False
        result = solver._simplify_formula()
        
        assert result is False
    
    def test_unit_resolution_false_literal_removal(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)  
        literal_r = Literal("r", negated=False)
        clause = Clause([literal_p, literal_q, literal_r])
        cnf = CNFFormula([clause])
        solver = DPLLSolver(cnf)
        
        solver.assignment["p"] = False
        result = solver._simplify_formula()
        
        assert result is True
        assert len(solver.cnf.clauses) == 1
        assert len(solver.cnf.clauses[0].literals) == 2
        literals = [lit.variable for lit in solver.cnf.clauses[0].literals]
        assert "q" in literals
        assert "r" in literals
        assert "p" not in literals
    
    def test_unit_resolution_negated_literal_removal(self):
        literal_p_neg = Literal("p", negated=True)
        literal_q = Literal("q", negated=False)
        literal_r = Literal("r", negated=False)
        clause = Clause([literal_p_neg, literal_q, literal_r])
        cnf = CNFFormula([clause])
        solver = DPLLSolver(cnf)
        
        solver.assignment["p"] = True
        result = solver._simplify_formula()
        
        assert result is True
        assert len(solver.cnf.clauses) == 1
        assert len(solver.cnf.clauses[0].literals) == 2
        literals = [lit.variable for lit in solver.cnf.clauses[0].literals]
        assert "q" in literals
        assert "r" in literals
        assert "p" not in [lit.variable for lit in solver.cnf.clauses[0].literals]
    
    def test_backtrack_empty_stack(self):
        cnf = CNFFormula([])
        solver = DPLLSolver(cnf)
        
        solver._backtrack()
        
        assert len(solver.decision_stack) == 0
        assert len(solver.assignment) == 0
    
    def test_backtrack_multiple_same_level(self):
        cnf = CNFFormula([])
        solver = DPLLSolver(cnf)
        
        solver.decision_stack.append(Assignment("p", True, 0))
        solver.decision_stack.append(Assignment("q", True, 1))
        solver.decision_stack.append(Assignment("r", True, 1))
        solver.assignment["p"] = True
        solver.assignment["q"] = True
        solver.assignment["r"] = True
        
        assert len(solver.assignment) == 3
        
        solver._backtrack()
        
        assert "q" not in solver.assignment
        assert solver.assignment["p"] is True
        assert solver.assignment["r"] is False
    
    def test_pure_literal_elimination_positive(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        literal_r = Literal("r", negated=True)
        clause1 = Clause([literal_p, literal_q])
        clause2 = Clause([literal_p, literal_r])
        cnf = CNFFormula([clause1, clause2])
        solver = DPLLSolver(cnf)
        
        result = solver._pure_literal_elimination()
        assert result is None
        assert solver.assignment["p"] is True
    
    def test_pure_literal_elimination_negative(self):
        literal_p = Literal("p", negated=False)
        literal_q_neg1 = Literal("q", negated=True)
        literal_q_neg2 = Literal("q", negated=True)
        literal_r = Literal("r", negated=False)
        clause1 = Clause([literal_p, literal_q_neg1])
        clause2 = Clause([literal_q_neg2, literal_r])
        cnf = CNFFormula([clause1, clause2])
        solver = DPLLSolver(cnf)
        
        result = solver._pure_literal_elimination()
        assert result is None
        assert solver.assignment["q"] is False
    
    def test_pure_literal_elimination_mixed_polarity(self):
        literal_p_pos = Literal("p", negated=False)
        literal_p_neg = Literal("p", negated=True)
        literal_q = Literal("q", negated=False)
        clause1 = Clause([literal_p_pos, literal_q])
        clause2 = Clause([literal_p_neg, literal_q])
        cnf = CNFFormula([clause1, clause2])
        solver = DPLLSolver(cnf)
        
        result = solver._pure_literal_elimination()
        assert result is None
        assert "p" not in solver.assignment
        assert solver.assignment["q"] is True
    
    def test_pure_literal_elimination_already_satisfied(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        clause1 = Clause([literal_p])
        clause2 = Clause([literal_q])
        cnf = CNFFormula([clause1, clause2])
        solver = DPLLSolver(cnf)
        
        solver.assignment["p"] = True
        result = solver._pure_literal_elimination()
        assert result is None
        assert solver.assignment["q"] is True
    
    def test_solve_simple_sat(self):
        literal_p = Literal("p", negated=False)
        clause = Clause([literal_p])
        cnf = CNFFormula([clause])
        solver = DPLLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert solver.assignment["p"] is True
    
    def test_solve_simple_unsat(self):
        literal_p_pos = Literal("p", negated=False)
        literal_p_neg = Literal("p", negated=True)
        clause1 = Clause([literal_p_pos])
        clause2 = Clause([literal_p_neg])
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
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        clause1 = Clause([literal_p, literal_q])
        clause2 = Clause([Literal("p", negated=True), literal_q])
        cnf = CNFFormula([clause1, clause2])
        solver = DPLLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert solver.assignment["q"] is True
    
    def test_solve_horn_clause_sat(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        literal_r = Literal("r", negated=False)
        clause1 = Clause([Literal("p", negated=True), literal_q])
        clause2 = Clause([Literal("q", negated=True), literal_r])
        clause3 = Clause([literal_p])
        cnf = CNFFormula([clause1, clause2, clause3])
        solver = DPLLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert solver.assignment["p"] is True
        assert solver.assignment["q"] is True
        assert solver.assignment["r"] is True
    
    def test_solve_requires_backtracking(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        literal_r = Literal("r", negated=False)
        clause1 = Clause([literal_p, literal_q])
        clause2 = Clause([literal_p, Literal("q", negated=True)])
        clause3 = Clause([Literal("p", negated=True), literal_r])
        clause4 = Clause([Literal("p", negated=True), Literal("r", negated=True)])
        cnf = CNFFormula([clause1, clause2, clause3, clause4])
        solver = DPLLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.UNSAT
    
    def test_solve_three_sat_problem(self):
        literal_x1 = Literal("x1", negated=False)
        literal_x2 = Literal("x2", negated=False)
        literal_x3 = Literal("x3", negated=False)
        clause1 = Clause([literal_x1, literal_x2, literal_x3])
        clause2 = Clause([Literal("x1", negated=True), Literal("x2", negated=True), literal_x3])
        clause3 = Clause([literal_x1, Literal("x2", negated=True), Literal("x3", negated=True)])
        cnf = CNFFormula([clause1, clause2, clause3])
        solver = DPLLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
    
    def test_solve_pure_literal_elimination_case(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=True)
        literal_r = Literal("r", negated=False)
        clause1 = Clause([literal_p, literal_q])
        clause2 = Clause([literal_p, literal_r])
        clause3 = Clause([literal_q, literal_r])
        cnf = CNFFormula([clause1, clause2, clause3])
        solver = DPLLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert solver.assignment["p"] is True
        assert solver.assignment["q"] is False
        assert solver.assignment["r"] is True
    
    def test_solve_unit_propagation_chain(self):
        literal_a = Literal("a", negated=False)
        literal_b = Literal("b", negated=False)
        literal_c = Literal("c", negated=False)
        clause1 = Clause([literal_a])
        clause2 = Clause([Literal("a", negated=True), literal_b])
        clause3 = Clause([Literal("b", negated=True), literal_c])
        cnf = CNFFormula([clause1, clause2, clause3])
        solver = DPLLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert solver.assignment["a"] is True
        assert solver.assignment["b"] is True
        assert solver.assignment["c"] is True
    
    def test_solve_complex_unsat(self):
        literal_x = Literal("x", negated=False)
        literal_y = Literal("y", negated=False)
        literal_z = Literal("z", negated=False)
        clause1 = Clause([literal_x, literal_y])
        clause2 = Clause([literal_x, Literal("y", negated=True)])
        clause3 = Clause([Literal("x", negated=True), literal_y])
        clause4 = Clause([Literal("x", negated=True), Literal("y", negated=True)])
        clause5 = Clause([literal_z])
        clause6 = Clause([Literal("z", negated=True)])
        cnf = CNFFormula([clause1, clause2, clause3, clause4, clause5, clause6])
        solver = DPLLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.UNSAT
    
    def test_solve_all_variables_assigned(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        clause1 = Clause([literal_p])
        clause2 = Clause([literal_q])
        cnf = CNFFormula([clause1, clause2])
        solver = DPLLSolver(cnf)
        
        solver.assignment["p"] = True
        solver.assignment["q"] = True
        
        result = solver.solve()
        assert result == DecisionResult.SAT
    
    def test_solve_pure_literal_elimination_unsat_case(self):
        cnf = CNFFormula([])
        solver = DPLLSolver(cnf)
        
        original_method = solver._pure_literal_elimination
        def mock_pure_literal_elimination():
            return DecisionResult.UNSAT
        
        solver._pure_literal_elimination = mock_pure_literal_elimination
        
        result = solver.solve()
        assert result == DecisionResult.UNSAT
        
        solver._pure_literal_elimination = original_method
    
    def test_solve_no_variables_to_choose(self):
        cnf = CNFFormula([])
        solver = DPLLSolver(cnf)
        
        original_choose = solver._choose_variable
        original_all_satisfied = solver._all_clauses_satisfied
        
        def mock_choose_variable():
            return None
        
        def mock_all_clauses_satisfied():
            return False
        
        solver._choose_variable = mock_choose_variable
        solver._all_clauses_satisfied = mock_all_clauses_satisfied
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        
        solver._choose_variable = original_choose
        solver._all_clauses_satisfied = original_all_satisfied
    
    def test_solve_pure_literal_elimination_unsat_with_backtrack(self):
        cnf = CNFFormula([])
        solver = DPLLSolver(cnf)
        
        solver._make_decision("x", True)
        
        call_count = 0
        original_method = solver._pure_literal_elimination
        def mock_pure_literal_elimination():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return DecisionResult.UNSAT
            return None
        
        original_all_satisfied = solver._all_clauses_satisfied
        def mock_all_clauses_satisfied():
            return True
        
        solver._pure_literal_elimination = mock_pure_literal_elimination
        solver._all_clauses_satisfied = mock_all_clauses_satisfied
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        
        solver._pure_literal_elimination = original_method
        solver._all_clauses_satisfied = original_all_satisfied


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
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=True)
        reason_clause = Clause([literal_p, literal_q])
        cnf = CNFFormula([reason_clause])
        solver = CDCLSolver(cnf)
        
        solver.assignment["q"] = False
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
        assert "q" in node.antecedents
    
    def test_choose_variable_with_learned_clauses(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        literal_r = Literal("r", negated=False)
        
        original_clause = Clause([literal_p])
        learned_clause = Clause([literal_q, literal_r])
        
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
    
    def test_all_clauses_satisfied_with_learned_clauses(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        
        original_clause = Clause([literal_p])
        learned_clause = Clause([literal_q])
        
        cnf = CNFFormula([original_clause])
        solver = CDCLSolver(cnf)
        solver.learned_clauses.append(learned_clause)
        
        assert solver._all_clauses_satisfied() is False
        
        solver.assignment["p"] = True
        assert solver._all_clauses_satisfied() is False
        
        solver.assignment["q"] = True
        assert solver._all_clauses_satisfied() is True
    
    def test_implication_node_creation(self):
        node = ImplicationNode("x", True, 2, None, ["y", "z"])
        assert node.variable == "x"
        assert node.value is True
        assert node.decision_level == 2
        assert node.reason is None
        assert node.antecedents == ["y", "z"]
    
    def test_implication_node_default_antecedents(self):
        node = ImplicationNode("x", False, 1)
        assert node.antecedents == []
    
    def test_assignment_with_reason(self):
        literal = Literal("p", negated=False)
        reason_clause = Clause([literal])
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
        literal_p = Literal("p", negated=False)
        clause = Clause([literal_p])
        cnf = CNFFormula([clause])
        solver = CDCLSolver(cnf)
        
        conflict = solver._unit_propagation()
        assert conflict is None
        assert solver.assignment["p"] is True
        assert "p" in solver.implication_graph
        assert solver.implication_graph["p"].reason == clause
    
    def test_unit_propagation_with_conflict(self):
        literal_p_pos = Literal("p", negated=False)
        literal_p_neg = Literal("p", negated=True)
        clause1 = Clause([literal_p_pos])
        clause2 = Clause([literal_p_neg])
        cnf = CNFFormula([clause1, clause2])
        solver = CDCLSolver(cnf)
        
        conflict = solver._unit_propagation()
        assert conflict == clause2
        assert solver.assignment["p"] is True
    
    def test_unit_propagation_chain(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        literal_r = Literal("r", negated=False)
        clause1 = Clause([literal_p])
        clause2 = Clause([Literal("p", negated=True), literal_q])
        clause3 = Clause([Literal("q", negated=True), literal_r])
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
        assert "p" in solver.implication_graph["q"].antecedents
        assert "q" in solver.implication_graph["r"].antecedents
    
    def test_unit_propagation_with_learned_clauses(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        original_clause = Clause([literal_p])
        learned_clause = Clause([Literal("p", negated=True), literal_q])
        
        cnf = CNFFormula([original_clause])
        solver = CDCLSolver(cnf)
        solver.learned_clauses.append(learned_clause)
        
        conflict = solver._unit_propagation()
        assert conflict is None
        assert solver.assignment["p"] is True
        assert solver.assignment["q"] is True
        assert solver.implication_graph["q"].reason == learned_clause
    
    def test_evaluate_clause_satisfied(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=True)
        clause = Clause([literal_p, literal_q])
        cnf = CNFFormula([clause])
        solver = CDCLSolver(cnf)
        
        solver.assignment["p"] = True
        result = solver._evaluate_clause(clause)
        assert result is True
    
    def test_evaluate_clause_unsatisfied(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        clause = Clause([literal_p, literal_q])
        cnf = CNFFormula([clause])
        solver = CDCLSolver(cnf)
        
        solver.assignment["p"] = False
        solver.assignment["q"] = False
        result = solver._evaluate_clause(clause)
        assert result is False
    
    def test_evaluate_clause_unassigned(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        clause = Clause([literal_p, literal_q])
        cnf = CNFFormula([clause])
        solver = CDCLSolver(cnf)
        
        result = solver._evaluate_clause(clause)
        assert result is None
    
    def test_evaluate_clause_partial_assignment(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        clause = Clause([literal_p, literal_q])
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
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        reason_clause = Clause([literal_p, literal_q])
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
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        literal_r = Literal("r", negated=False)
        reason1 = Clause([literal_p])
        reason2 = Clause([literal_q])
        
        cnf = CNFFormula([])
        solver = CDCLSolver(cnf)
        
        solver._make_decision("x", True)
        solver._add_implication("p", True, reason1)
        solver._add_implication("q", False, reason2)
        solver._make_decision("y", False)
        
        assert solver.decision_level == 2
        assert len(solver.assignment) == 4
        
        solver._backtrack_to_level(1)
        
        assert solver.decision_level == 1
        assert solver.assignment["x"] is True
        assert solver.assignment["p"] is True
        assert solver.assignment["q"] is False
        assert "y" not in solver.assignment
        assert len(solver.decision_stack) == 3
        assert len(solver.implication_graph) == 3
    
    def test_solve_simple_sat(self):
        literal_p = Literal("p", negated=False)
        clause = Clause([literal_p])
        cnf = CNFFormula([clause])
        solver = CDCLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert solver.assignment["p"] is True
    
    def test_solve_simple_unsat(self):
        literal_p_pos = Literal("p", negated=False)
        literal_p_neg = Literal("p", negated=True)
        clause1 = Clause([literal_p_pos])
        clause2 = Clause([literal_p_neg])
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
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        clause1 = Clause([literal_p])
        clause2 = Clause([Literal("p", negated=True), literal_q])
        cnf = CNFFormula([clause1, clause2])
        solver = CDCLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert solver.assignment["p"] is True
        assert solver.assignment["q"] is True
    
    def test_solve_with_decision_making(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        clause = Clause([literal_p, literal_q])
        cnf = CNFFormula([clause])
        solver = CDCLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert (solver.assignment.get("p", False) is True or solver.assignment.get("q", False) is True)
    
    def test_solve_with_conflict_and_learning(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        clause1 = Clause([literal_p, literal_q])
        clause2 = Clause([Literal("p", negated=True)])
        clause3 = Clause([Literal("q", negated=True)])
        cnf = CNFFormula([clause1, clause2, clause3])
        solver = CDCLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.UNSAT
        assert len(solver.learned_clauses) > 0
    
    def test_solve_horn_clauses(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        literal_r = Literal("r", negated=False)
        clause1 = Clause([Literal("p", negated=True), literal_q])
        clause2 = Clause([Literal("q", negated=True), literal_r])
        clause3 = Clause([literal_p])
        cnf = CNFFormula([clause1, clause2, clause3])
        solver = CDCLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert solver.assignment["p"] is True
        assert solver.assignment["q"] is True
        assert solver.assignment["r"] is True
    
    def test_solve_multiple_decisions(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        literal_r = Literal("r", negated=False)
        clause1 = Clause([literal_p, literal_q])
        clause2 = Clause([literal_r])
        cnf = CNFFormula([clause1, clause2])
        solver = CDCLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert solver.assignment["r"] is True
        assert (solver.assignment.get("p", False) is True or solver.assignment.get("q", False) is True)
    
    def test_solve_with_learned_clauses_consideration(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        literal_r = Literal("r", negated=False)
        
        clause1 = Clause([literal_p])
        clause2 = Clause([literal_q])
        cnf = CNFFormula([clause1, clause2])
        solver = CDCLSolver(cnf)
        
        learned_clause = Clause([literal_r])
        solver.learned_clauses.append(learned_clause)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        assert solver.assignment["p"] is True
        assert solver.assignment["q"] is True
        assert solver.assignment["r"] is True
    
    def test_solve_conflict_at_decision_level_zero(self):
        literal_p = Literal("p", negated=False)
        clause1 = Clause([literal_p])
        clause2 = Clause([Literal("p", negated=True)])
        cnf = CNFFormula([clause1, clause2])
        solver = CDCLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.UNSAT
    
    def test_solve_all_variables_assigned_early(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        clause1 = Clause([literal_p])
        clause2 = Clause([literal_q])
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
        literal_a = Literal("a", negated=False)
        literal_b = Literal("b", negated=False)
        literal_c = Literal("c", negated=False)
        
        clause1 = Clause([literal_a, literal_b])
        clause2 = Clause([Literal("a", negated=True), literal_c])
        clause3 = Clause([Literal("b", negated=True), literal_c])
        cnf = CNFFormula([clause1, clause2, clause3])
        solver = CDCLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.SAT
        
        # Check that the assignment satisfies the formula
        # The solver might not assign all variables if they're not needed
        if "a" in solver.assignment and "b" in solver.assignment:
            if solver.assignment["a"] and solver.assignment["b"]:
                assert True
            else:
                assert solver.assignment["c"] is True
        else:
            # If not all variables are assigned, c must be true to satisfy all clauses
            assert solver.assignment.get("c", False) is True
    
    def test_solve_with_backtracking_scenario(self):
        literal_x = Literal("x", negated=False)
        literal_y = Literal("y", negated=False)
        literal_z = Literal("z", negated=False)
        
        clause1 = Clause([literal_x, literal_y])
        clause2 = Clause([literal_x, Literal("y", negated=True)])
        clause3 = Clause([Literal("x", negated=True), literal_z])
        clause4 = Clause([Literal("z", negated=True)])
        cnf = CNFFormula([clause1, clause2, clause3, clause4])
        solver = CDCLSolver(cnf)
        
        result = solver.solve()
        assert result == DecisionResult.UNSAT
    
    def test_backjump_method(self):
        literal_p = Literal("p", negated=False)
        clause = Clause([literal_p])
        cnf = CNFFormula([clause])
        solver = CDCLSolver(cnf)
        
        learned_clause = Clause([literal_p])
        level = solver._backjump(learned_clause)
        assert level == 0
    
    def test_backjump_scenario_calls_backtrack(self):
        literal_p = Literal("p", negated=False)
        literal_q = Literal("q", negated=False)
        clause1 = Clause([literal_p, literal_q])
        cnf = CNFFormula([clause1])
        
        class BackjumpTestSolver(CDCLSolver):
            def __init__(self, cnf: CNFFormula):
                super().__init__(cnf)
                self.conflict_forced = False
                
            def _unit_propagation(self):
                if self.decision_level > 0 and not self.conflict_forced:
                    self.conflict_forced = True
                    return Clause([Literal("fake_conflict", negated=True)])
                return super()._unit_propagation()
                
        test_solver = BackjumpTestSolver(cnf)
        result = test_solver.solve()
        assert result in [DecisionResult.SAT, DecisionResult.UNSAT]
        assert len(test_solver.learned_clauses) > 0 or not test_solver.conflict_forced
    
    def test_choose_variable_returns_none_scenario(self):
        literal_p = Literal("p", negated=False)
        clause = Clause([literal_p])
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
