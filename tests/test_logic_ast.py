import pytest

from src.logic_ast import Formula, Variable, Not, And, Or, Implies, Biconditional


class TestVariable:
    
    def test_variable_creation(self):
        var = Variable("p")
        assert var.name == "p"
        assert isinstance(var, Formula)
    
    def test_variable_str(self):
        assert str(Variable("p")) == "p"
        assert str(Variable("x")) == "x"


class TestNot:
    
    def test_not_with_variable(self):
        var = Variable("p")
        not_var = Not(var)
        assert not_var.operand == var
        assert isinstance(not_var, Formula)
    
    def test_not_str_with_variable(self):
        var = Variable("p")
        not_var = Not(var)
        assert str(not_var) == "¬p"
    
    def test_not_str_with_complex_formula(self):
        and_formula = And(Variable("p"), Variable("q"))
        not_and = Not(and_formula)
        assert str(not_and) == "¬(p ∧ q)"


class TestAnd:
    
    def test_and_with_variables(self):
        var_p = Variable("p")
        var_q = Variable("q")
        and_formula = And(var_p, var_q)
        assert and_formula.left == var_p
        assert and_formula.right == var_q
        assert isinstance(and_formula, Formula)
    
    def test_and_str_with_variables(self):
        and_formula = And(Variable("p"), Variable("q"))
        assert str(and_formula) == "p ∧ q"
    
    def test_and_str_with_nested_formulas(self):
        or_formula = Or(Variable("q"), Variable("r"))
        and_formula = And(Variable("p"), or_formula)
        assert str(and_formula) == "p ∧ (q ∨ r)"


class TestOr:
    
    def test_or_with_variables(self):
        var_p = Variable("p")
        var_q = Variable("q")
        or_formula = Or(var_p, var_q)
        assert or_formula.left == var_p
        assert or_formula.right == var_q
        assert isinstance(or_formula, Formula)
    
    def test_or_str_with_variables(self):
        or_formula = Or(Variable("p"), Variable("q"))
        assert str(or_formula) == "p ∨ q"
    
    def test_or_str_with_nested_formulas(self):
        and_formula = And(Variable("q"), Variable("r"))
        or_formula = Or(Variable("p"), and_formula)
        assert str(or_formula) == "p ∨ (q ∧ r)"


class TestImplies:
    
    def test_implies_with_variables(self):
        var_p = Variable("p")
        var_q = Variable("q")
        implies_formula = Implies(var_p, var_q)
        assert implies_formula.left == var_p
        assert implies_formula.right == var_q
        assert isinstance(implies_formula, Formula)
    
    def test_implies_str_with_variables(self):
        implies_formula = Implies(Variable("p"), Variable("q"))
        assert str(implies_formula) == "p → q"


class TestBiconditional:
    
    def test_biconditional_with_variables(self):
        var_p = Variable("p")
        var_q = Variable("q")
        bicon_formula = Biconditional(var_p, var_q)
        assert bicon_formula.left == var_p
        assert bicon_formula.right == var_q
        assert isinstance(bicon_formula, Formula)
    
    def test_biconditional_str_with_variables(self):
        bicon_formula = Biconditional(Variable("p"), Variable("q"))
        assert str(bicon_formula) == "p ↔ q"


class TestComplexFormulas:
    
    def test_complex_nested_formula(self):
        # (p ∧ q) → (¬r ∨ s)
        left_part = And(Variable("p"), Variable("q"))
        right_part = Or(Not(Variable("r")), Variable("s"))
        complex_formula = Implies(left_part, right_part)
        
        assert str(complex_formula) == "(p ∧ q) → (¬r ∨ s)"