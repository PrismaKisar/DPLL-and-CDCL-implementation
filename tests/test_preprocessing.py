import pytest

from src.preprocessing import eliminate_implications, push_negations_inward, to_nnf
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
