from src.logic_ast import Formula, Variable, Not, And, Or, Implies, Biconditional


def to_nnf(formula: Formula) -> Formula:
    without_implications = eliminate_implications(formula)
    nnf_formula = push_negations_inward(without_implications)
    return nnf_formula


def eliminate_implications(formula: Formula) -> Formula:
    if isinstance(formula, Variable):
        return formula
    
    elif isinstance(formula, Not):
        return Not(eliminate_implications(formula.operand))
    
    elif isinstance(formula, And):
        return And(
            eliminate_implications(formula.left),
            eliminate_implications(formula.right)
        )
    
    elif isinstance(formula, Or):
        return Or(
            eliminate_implications(formula.left),
            eliminate_implications(formula.right)
        )
    
    elif isinstance(formula, Implies):
        return Or(
            Not(eliminate_implications(formula.left)),
            eliminate_implications(formula.right)
        )
    
    elif isinstance(formula, Biconditional):
        left = eliminate_implications(formula.left)
        right = eliminate_implications(formula.right)
        return And(
            Or(Not(left), right),
            Or(Not(right), left)
        )
    
    else:
        raise ValueError(f"Unknown formula type: {type(formula)}")


def push_negations_inward(formula: Formula) -> Formula:
    if isinstance(formula, Variable):
        return formula
    
    elif isinstance(formula, Not):
        if isinstance(formula.operand, Variable):
            return formula
        
        elif isinstance(formula.operand, Not):
            return push_negations_inward(formula.operand.operand)
        
        elif isinstance(formula.operand, And):
            return Or(
                push_negations_inward(Not(formula.operand.left)),
                push_negations_inward(Not(formula.operand.right))
            )
        
        elif isinstance(formula.operand, Or):
            return And(
                push_negations_inward(Not(formula.operand.left)),
                push_negations_inward(Not(formula.operand.right))
            )
        
        else:
            raise ValueError(f"Unexpected formula under negation: {type(formula.operand)}")
    
    elif isinstance(formula, And):
        return And(
            push_negations_inward(formula.left),
            push_negations_inward(formula.right)
        )
    
    elif isinstance(formula, Or):
        return Or(
            push_negations_inward(formula.left),
            push_negations_inward(formula.right)
        )
    
    else:
        raise ValueError(f"Unknown formula type: {type(formula)}")


def to_cnf(formula: Formula) -> Formula:
    nnf_formula = to_nnf(formula)
    cnf_formula = distribute_or_over_and(nnf_formula)
    return cnf_formula


def distribute_or_over_and(formula: Formula) -> Formula:
    pass