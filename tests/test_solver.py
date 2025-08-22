import pytest

from src.solver import DPLLSolver, DecisionResult, Assignment
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
        # Test: p=False, clausola (p ∨ q ∨ r) -> diventa (q ∨ r)
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
        # Test: p=True, clausola (¬p ∨ q ∨ r) -> diventa (q ∨ r)
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
        
        # Testa backtrack con stack vuoto (riga 81)
        solver._backtrack()
        
        assert len(solver.decision_stack) == 0
        assert len(solver.assignment) == 0
    
    def test_backtrack_multiple_same_level(self):
        cnf = CNFFormula([])
        solver = DPLLSolver(cnf)
        
        # Simula decisioni a livelli diversi + multiple allo stesso livello  
        solver.decision_stack.append(Assignment("p", True, 0))
        solver.decision_stack.append(Assignment("q", True, 1))
        solver.decision_stack.append(Assignment("r", True, 1))  # True per attivare il caso opposto
        solver.assignment["p"] = True
        solver.assignment["q"] = True
        solver.assignment["r"] = True
        
        # Verifica stato iniziale
        assert len(solver.assignment) == 3
        
        # Backtrack dovrebbe rimuovere r e q (stesso livello), poi aggiungere r=False (righe 88-89)
        solver._backtrack()
        
        # Verifica che il while loop ha rimosso q (stesso livello di r)
        assert "q" not in solver.assignment  # Rimosso dal while loop (righe 88-89)
        assert solver.assignment["p"] is True  # p rimane (livello diverso)
        assert solver.assignment["r"] is False  # Nuovo valore opposto