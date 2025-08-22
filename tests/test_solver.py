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