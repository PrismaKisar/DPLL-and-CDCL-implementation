import pytest

from src.preprocessing import eliminate_implications, push_negations_inward, to_nnf, to_cnf, to_cnf_tseytin, distribute_or_over_and, formula_to_cnf_format, extract_literals_from_or, formula_to_literal
from src.logic_ast import Variable, Not, And, Or, Implies, Biconditional, CNFFormula
from src.solver import DPLLSolver, DecisionResult


P = Variable("p")
Q = Variable("q")
R = Variable("r")


class TestEliminateImplications:
    
    def test_variable_unchanged(self):
        result = eliminate_implications(P)
        assert isinstance(result, Variable)
        assert result.name == "p"
    
    def test_simple_implication(self):
        impl = Implies(P, Q)
        result = eliminate_implications(impl)
        assert isinstance(result, Or)
        assert isinstance(result.left, Not)
        assert isinstance(result.left.operand, Variable)
        assert result.left.operand.name == "p"
        assert isinstance(result.right, Variable)
        assert result.right.name == "q"
    
    def test_biconditional(self):
        bicon = Biconditional(P, Q)
        result = eliminate_implications(bicon)
        assert isinstance(result, And)
        assert isinstance(result.left, Or)
        assert isinstance(result.right, Or)
    
    def test_and_unchanged(self):
        and_formula = And(P, Q)
        result = eliminate_implications(and_formula)
        assert isinstance(result, And)
        assert isinstance(result.left, Variable)
        assert result.left.name == "p"
        assert isinstance(result.right, Variable)
        assert result.right.name == "q"
    
    def test_or_unchanged(self):
        or_formula = Or(P, Q)
        result = eliminate_implications(or_formula)
        assert isinstance(result, Or)
        assert isinstance(result.left, Variable)
        assert result.left.name == "p"
        assert isinstance(result.right, Variable)
        assert result.right.name == "q"
    
    def test_unknown_formula_type_error(self):
        class UnknownFormula:
            pass
        
        unknown = UnknownFormula()
        with pytest.raises(ValueError, match="Unknown formula type"):
            eliminate_implications(unknown)  # type: ignore


class TestPushNegationsInward:
    
    def test_variable_unchanged(self):
        result = push_negations_inward(P)
        assert isinstance(result, Variable)
        assert result.name == "p"
    
    def test_double_negation(self):
        double_neg = Not(Not(P))
        result = push_negations_inward(double_neg)
        assert isinstance(result, Variable)
        assert result.name == "p"
    
    def test_negated_and(self):
        negated_and = Not(And(P, Q))
        result = push_negations_inward(negated_and)
        assert isinstance(result, Or)
        assert isinstance(result.left, Not)
        assert isinstance(result.right, Not)
        assert isinstance(result.left.operand, Variable)
        assert result.left.operand.name == "p"
        assert isinstance(result.right.operand, Variable)
        assert result.right.operand.name == "q"
    
    def test_negated_or(self):
        negated_or = Not(Or(P, Q))
        result = push_negations_inward(negated_or)
        assert isinstance(result, And)
        assert isinstance(result.left, Not)
        assert isinstance(result.right, Not)
        assert isinstance(result.left.operand, Variable)
        assert result.left.operand.name == "p"
        assert isinstance(result.right.operand, Variable)
        assert result.right.operand.name == "q"
    
    def test_and_unchanged(self):
        and_formula = And(P, Q)
        result = push_negations_inward(and_formula)
        assert isinstance(result, And)
        assert isinstance(result.left, Variable)
        assert result.left.name == "p"
        assert isinstance(result.right, Variable)
        assert result.right.name == "q"
    
    def test_or_unchanged(self):
        or_formula = Or(P, Q)
        result = push_negations_inward(or_formula)
        assert isinstance(result, Or)
        assert isinstance(result.left, Variable)
        assert result.left.name == "p"
        assert isinstance(result.right, Variable)
        assert result.right.name == "q"
    
    def test_negation_of_unknown_formula_error(self):
        class UnknownFormula:
            pass
        
        unknown = UnknownFormula()
        negated_unknown = Not(unknown)  # type: ignore
        with pytest.raises(ValueError, match="Unexpected formula under negation"):
            push_negations_inward(negated_unknown)
    
    def test_unknown_formula_type_error(self):
        class UnknownFormula:
            pass
        
        unknown = UnknownFormula()
        with pytest.raises(ValueError, match="Unknown formula type"):
            push_negations_inward(unknown)  # type: ignore


class TestToNNF:
    
    def test_simple_variable(self):
        result = to_nnf(P)
        assert isinstance(result, Variable)
        assert result.name == "p"
    
    def test_implication_to_nnf(self):
        impl = Implies(P, Q)
        result = to_nnf(impl)
        assert isinstance(result, Or)
        assert isinstance(result.left, Not)
        assert isinstance(result.left.operand, Variable)
        assert result.left.operand.name == "p"
        assert isinstance(result.right, Variable)
        assert result.right.name == "q"
    
    def test_complex_formula_to_nnf(self):
        formula = Not(Implies(And(P, Q), R))
        result = to_nnf(formula)
        assert isinstance(result, And)
        assert isinstance(result.left, And)
        assert isinstance(result.right, Not)
        assert isinstance(result.right.operand, Variable)
        assert result.right.operand.name == "r"


class TestDistributeOrOverAnd:
    
    def test_variable_unchanged(self):
        result = distribute_or_over_and(P)
        assert isinstance(result, Variable)
        assert result.name == "p"
    
    def test_simple_or(self):
        or_formula = Or(P, Q)
        result = distribute_or_over_and(or_formula)
        assert isinstance(result, Or)
        assert isinstance(result.left, Variable)
        assert result.left.name == "p"
        assert isinstance(result.right, Variable)
        assert result.right.name == "q"
    
    def test_distribute_or_over_and_right(self):
        formula = Or(P, And(Q, R))
        result = distribute_or_over_and(formula)
        assert isinstance(result, And)
        assert isinstance(result.left, Or)
        assert isinstance(result.right, Or)
        assert isinstance(result.left.left, Variable)
        assert result.left.left.name == "p"
        assert isinstance(result.left.right, Variable)
        assert result.left.right.name == "q"
        assert isinstance(result.right.left, Variable)
        assert result.right.left.name == "p"
        assert isinstance(result.right.right, Variable)
        assert result.right.right.name == "r"
    
    def test_distribute_or_over_and_left(self):
        formula = Or(And(P, Q), R)
        result = distribute_or_over_and(formula)
        assert isinstance(result, And)
        assert isinstance(result.left, Or)
        assert isinstance(result.right, Or)
    
    def test_unknown_formula_type_error(self):
        class UnknownFormula:
            pass
        
        unknown = UnknownFormula()
        with pytest.raises(ValueError, match="Unknown formula type"):
            distribute_or_over_and(unknown)  # type: ignore


class TestToCNF:
    
    def test_simple_variable(self):
        result = to_cnf(P)
        assert isinstance(result, CNFFormula)
        assert len(result.clauses) == 1
        assert len(result.clauses[0].literals) == 1
        assert result.clauses[0].literals[0].variable == "p"
        assert result.clauses[0].literals[0].negated == False
    
    def test_simple_implication_to_cnf(self):
        impl = Implies(P, Q)
        result = to_cnf(impl)
        assert isinstance(result, CNFFormula)
        assert len(result.clauses) == 1
        assert len(result.clauses[0].literals) == 2
        literals = result.clauses[0].literals
        assert literals[0].variable == "p" and literals[0].negated == True
        assert literals[1].variable == "q" and literals[1].negated == False
    
    def test_complex_formula_to_cnf(self):
        formula = Or(P, And(Q, R))
        result = to_cnf(formula)
        assert isinstance(result, CNFFormula)
        assert len(result.clauses) == 2
        assert len(result.clauses[0].literals) == 2
        assert len(result.clauses[1].literals) == 2


class TestFormulaToCnfFormat:
    
    def test_invalid_formula_type_error(self):
        impl = Implies(P, Q)
        with pytest.raises(ValueError, match="Expected CNF formula, got"):
            formula_to_cnf_format(impl)


class TestExtractLiteralsFromOr:
    
    def test_invalid_formula_type_error(self):
        and_formula = And(P, Q)
        with pytest.raises(ValueError, match="Expected OR of literals, got"):
            extract_literals_from_or(and_formula)


class TestFormulaToLiteral:

    def test_invalid_formula_type_error(self):
        and_formula = And(P, Q)
        with pytest.raises(ValueError, match="Cannot convert"):
            formula_to_literal(and_formula)


class TestTseytinTransformation:
    """Comprehensive tests for Tseytin transformation with z_n variables."""

    def test_single_variable(self):
        """Test: Single variable should work correctly."""
        formula = P
        cnf = to_cnf_tseytin(formula)
        assert len(cnf.clauses) == 1
        # Should just be the variable itself
        assert any("p" in str(clause) for clause in cnf.clauses)

    def test_simple_conjunction(self):
        """Test: p ∧ q should create z_1 ↔ (p ∧ q) + assertion z_1."""
        formula = And(P, Q)
        cnf = to_cnf_tseytin(formula)

        # Should have clauses for the biconditional + assertion
        assert len(cnf.clauses) >= 3

        # Check that z_1 variables are used
        cnf_str = str(cnf)
        assert "z_1" in cnf_str

        # Verify satisfiability
        solver = DPLLSolver(cnf)
        result = solver.solve()
        assert result == DecisionResult.SAT

    def test_simple_disjunction(self):
        """Test: p ∨ q should create z_1 ↔ (p ∨ q) + assertion z_1."""
        formula = Or(P, Q)
        cnf = to_cnf_tseytin(formula)

        assert len(cnf.clauses) >= 3
        assert "z_1" in str(cnf)

        solver = DPLLSolver(cnf)
        result = solver.solve()
        assert result == DecisionResult.SAT

    def test_nested_formula(self):
        """Test: (p ∧ q) ∨ r should create multiple z variables."""
        formula = Or(And(P, Q), R)
        cnf = to_cnf_tseytin(formula)

        # Should have multiple z variables
        cnf_str = str(cnf)
        assert "z_1" in cnf_str
        assert "z_2" in cnf_str

        # Verify satisfiability
        solver = DPLLSolver(cnf)
        result = solver.solve()
        assert result == DecisionResult.SAT

    def test_complex_formula(self):
        """Test: (p ∧ q) ∨ (r ∧ s) should handle multiple subformulas."""
        S = Variable("s")
        formula = Or(And(P, Q), And(R, S))
        cnf = to_cnf_tseytin(formula)

        # Should create z variables for each subformula
        cnf_str = str(cnf)
        assert "z_1" in cnf_str
        assert "z_2" in cnf_str
        assert "z_3" in cnf_str

        # Test satisfiability
        solver = DPLLSolver(cnf)
        result = solver.solve()
        assert result == DecisionResult.SAT

    def test_implication_handling(self):
        """Test: p → q should be converted correctly through NNF first."""
        formula = Implies(P, Q)
        cnf = to_cnf_tseytin(formula)

        # Should work without errors
        assert len(cnf.clauses) > 0

        # Verify satisfiability
        solver = DPLLSolver(cnf)
        result = solver.solve()
        assert result == DecisionResult.SAT

    def test_biconditional_handling(self):
        """Test: p ↔ q should be converted correctly."""
        formula = Biconditional(P, Q)
        cnf = to_cnf_tseytin(formula)

        assert len(cnf.clauses) > 0

        solver = DPLLSolver(cnf)
        result = solver.solve()
        assert result == DecisionResult.SAT

    def test_negation_handling(self):
        """Test: ¬(p ∧ q) should be handled via NNF conversion."""
        formula = Not(And(P, Q))
        cnf = to_cnf_tseytin(formula)

        assert len(cnf.clauses) > 0

        solver = DPLLSolver(cnf)
        result = solver.solve()
        assert result == DecisionResult.SAT

    def test_satisfiability_equivalence_sat(self):
        """Test: Tseytin and classical should agree on SAT formulas."""
        formula = Or(P, Q)

        classical_cnf = to_cnf(formula)
        tseytin_cnf = to_cnf_tseytin(formula)

        classical_solver = DPLLSolver(classical_cnf)
        tseytin_solver = DPLLSolver(tseytin_cnf)

        classical_result = classical_solver.solve()
        tseytin_result = tseytin_solver.solve()

        assert classical_result == tseytin_result == DecisionResult.SAT

    def test_satisfiability_equivalence_unsat(self):
        """Test: Tseytin and classical should agree on UNSAT formulas."""
        # Create unsatisfiable formula: p ∧ ¬p
        formula = And(P, Not(P))

        classical_cnf = to_cnf(formula)
        tseytin_cnf = to_cnf_tseytin(formula)

        classical_solver = DPLLSolver(classical_cnf)
        tseytin_solver = DPLLSolver(tseytin_cnf)

        classical_result = classical_solver.solve()
        tseytin_result = tseytin_solver.solve()

        assert classical_result == tseytin_result == DecisionResult.UNSAT

    def test_complex_nested_formula(self):
        """Test: Deeply nested formula should work correctly."""
        T = Variable("t")
        U = Variable("u")

        # ((p ∧ q) ∨ r) ∧ ((s ∨ t) ∧ u)
        formula = And(
            Or(And(P, Q), R),
            And(Or(Variable("s"), T), U)
        )

        cnf = to_cnf_tseytin(formula)

        # Should have multiple z variables
        cnf_str = str(cnf)
        assert "z_" in cnf_str

        # Should be satisfiable
        solver = DPLLSolver(cnf)
        result = solver.solve()
        assert result == DecisionResult.SAT

    def test_z_variable_naming(self):
        """Test: Variables should be named z_1, z_2, z_3, etc."""
        formula = Or(And(P, Q), And(R, Variable("s")))
        cnf = to_cnf_tseytin(formula)

        cnf_str = str(cnf)
        # Should use z_n naming convention
        assert "z_1" in cnf_str
        assert "z_2" in cnf_str
        assert "z_3" in cnf_str
        # Should not use aux_ or other naming
        assert "aux_" not in cnf_str