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
