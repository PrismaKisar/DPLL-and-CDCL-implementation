import pytest

from src.preprocessing import eliminate_implications, push_negations_inward, to_nnf, to_cnf, distribute_or_over_and
from src.logic_ast import Variable, Not, And, Or, Implies, Biconditional


class TestEliminateImplications:
    
    def test_variable_unchanged(self):
        p = Variable("p")
        result = eliminate_implications(p)
        assert isinstance(result, Variable)
        assert result.name == "p"
    
    def test_simple_implication(self):
        p = Variable("p")
        q = Variable("q")
        impl = Implies(p, q)
        result = eliminate_implications(impl)
        assert isinstance(result, Or)
        assert isinstance(result.left, Not)
        assert isinstance(result.left.operand, Variable)
        assert result.left.operand.name == "p"
        assert isinstance(result.right, Variable)
        assert result.right.name == "q"
    
    def test_biconditional(self):
        p = Variable("p")
        q = Variable("q")
        bicon = Biconditional(p, q)
        result = eliminate_implications(bicon)
        assert isinstance(result, And)
        assert isinstance(result.left, Or)
        assert isinstance(result.right, Or)
    
    def test_and_unchanged(self):
        p = Variable("p")
        q = Variable("q")
        and_formula = And(p, q)
        result = eliminate_implications(and_formula)
        assert isinstance(result, And)
        assert isinstance(result.left, Variable)
        assert result.left.name == "p"
        assert isinstance(result.right, Variable)
        assert result.right.name == "q"
    
    def test_or_unchanged(self):
        p = Variable("p")
        q = Variable("q")
        or_formula = Or(p, q)
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
        p = Variable("p")
        result = push_negations_inward(p)
        assert isinstance(result, Variable)
        assert result.name == "p"
    
    def test_double_negation(self):
        p = Variable("p")
        double_neg = Not(Not(p))
        result = push_negations_inward(double_neg)
        assert isinstance(result, Variable)
        assert result.name == "p"
    
    def test_negated_and(self):
        p = Variable("p")
        q = Variable("q")
        negated_and = Not(And(p, q))
        result = push_negations_inward(negated_and)
        assert isinstance(result, Or)
        assert isinstance(result.left, Not)
        assert isinstance(result.right, Not)
        assert isinstance(result.left.operand, Variable)
        assert result.left.operand.name == "p"
        assert isinstance(result.right.operand, Variable)
        assert result.right.operand.name == "q"
    
    def test_negated_or(self):
        p = Variable("p")
        q = Variable("q")
        negated_or = Not(Or(p, q))
        result = push_negations_inward(negated_or)
        assert isinstance(result, And)
        assert isinstance(result.left, Not)
        assert isinstance(result.right, Not)
        assert isinstance(result.left.operand, Variable)
        assert result.left.operand.name == "p"
        assert isinstance(result.right.operand, Variable)
        assert result.right.operand.name == "q"
    
    def test_and_unchanged(self):
        p = Variable("p")
        q = Variable("q")
        and_formula = And(p, q)
        result = push_negations_inward(and_formula)
        assert isinstance(result, And)
        assert isinstance(result.left, Variable)
        assert result.left.name == "p"
        assert isinstance(result.right, Variable)
        assert result.right.name == "q"
    
    def test_or_unchanged(self):
        p = Variable("p")
        q = Variable("q")
        or_formula = Or(p, q)
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
        p = Variable("p")
        result = to_nnf(p)
        assert isinstance(result, Variable)
        assert result.name == "p"
    
    def test_implication_to_nnf(self):
        p = Variable("p")
        q = Variable("q")
        impl = Implies(p, q)
        result = to_nnf(impl)
        assert isinstance(result, Or)
        assert isinstance(result.left, Not)
        assert isinstance(result.left.operand, Variable)
        assert result.left.operand.name == "p"
        assert isinstance(result.right, Variable)
        assert result.right.name == "q"
    
    def test_complex_formula_to_nnf(self):
        p = Variable("p")
        q = Variable("q")
        r = Variable("r")
        formula = Not(Implies(And(p, q), r))
        result = to_nnf(formula)
        assert isinstance(result, And)
        assert isinstance(result.left, And)
        assert isinstance(result.right, Not)
        assert isinstance(result.right.operand, Variable)
        assert result.right.operand.name == "r"


class TestDistributeOrOverAnd:
    
    def test_variable_unchanged(self):
        p = Variable("p")
        result = distribute_or_over_and(p)
        assert isinstance(result, Variable)
        assert result.name == "p"
    
    def test_simple_or(self):
        p = Variable("p")
        q = Variable("q")
        or_formula = Or(p, q)
        result = distribute_or_over_and(or_formula)
        assert isinstance(result, Or)
        assert isinstance(result.left, Variable)
        assert result.left.name == "p"
        assert isinstance(result.right, Variable)
        assert result.right.name == "q"
    
    def test_distribute_or_over_and_right(self):
        p = Variable("p")
        q = Variable("q")
        r = Variable("r")
        formula = Or(p, And(q, r))
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
        p = Variable("p")
        q = Variable("q")
        r = Variable("r")
        formula = Or(And(p, q), r)
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
        p = Variable("p")
        result = to_cnf(p)
        assert isinstance(result, Variable)
        assert result.name == "p"
    
    def test_simple_implication_to_cnf(self):
        p = Variable("p")
        q = Variable("q")
        impl = Implies(p, q)
        result = to_cnf(impl)
        assert isinstance(result, Or)
        assert isinstance(result.left, Not)
        assert isinstance(result.left.operand, Variable)
        assert result.left.operand.name == "p"
        assert isinstance(result.right, Variable)
        assert result.right.name == "q"
    
    def test_complex_formula_to_cnf(self):
        p = Variable("p")
        q = Variable("q")
        r = Variable("r")
        formula = Or(p, And(q, r))
        result = to_cnf(formula)
        assert isinstance(result, And)
        assert isinstance(result.left, Or)
        assert isinstance(result.right, Or)