from src.logic_ast import Formula, Variable, Not, And, Or, Implies, Biconditional


def to_nnf(formula: Formula) -> Formula:
    without_implications = eliminate_implications(formula)
    nnf_formula = push_negations_inward(without_implications)
    return nnf_formula


def eliminate_implications(formula: Formula) -> Formula:
    pass


def push_negations_inward(formula: Formula) -> Formula:
    pass