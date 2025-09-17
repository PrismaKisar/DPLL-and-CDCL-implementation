from src.logic_ast import Formula, Variable, Not, And, Or, Implies, Biconditional, Literal, Clause, CNFFormula


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


def formula_to_cnf_format(formula: Formula) -> CNFFormula:
    if isinstance(formula, Variable) or (isinstance(formula, Not) and isinstance(formula.operand, Variable)):
        literal = formula_to_literal(formula)
        clause = Clause([literal])
        return CNFFormula([clause])
    
    elif isinstance(formula, Or):
        literals = extract_literals_from_or(formula)
        clause = Clause(literals)
        return CNFFormula([clause])
    
    elif isinstance(formula, And):
        left_cnf = formula_to_cnf_format(formula.left)
        right_cnf = formula_to_cnf_format(formula.right)
        return CNFFormula(left_cnf.clauses + right_cnf.clauses)
    
    else:
        raise ValueError(f"Expected CNF formula, got {type(formula)}")


def extract_literals_from_or(formula: Formula) -> list[Literal]:
    if isinstance(formula, Variable) or (isinstance(formula, Not) and isinstance(formula.operand, Variable)):
        return [formula_to_literal(formula)]
    elif isinstance(formula, Or):
        left_literals = extract_literals_from_or(formula.left)
        right_literals = extract_literals_from_or(formula.right)
        return left_literals + right_literals
    else:
        raise ValueError(f"Expected OR of literals, got {type(formula)}")


def formula_to_literal(formula: Formula) -> Literal:
    if isinstance(formula, Variable):
        return Literal(formula.name, negated=False)
    elif isinstance(formula, Not) and isinstance(formula.operand, Variable):
        return Literal(formula.operand.name, negated=True)
    else:
        raise ValueError(f"Cannot convert {type(formula)} to Literal")


def to_cnf(formula: Formula) -> CNFFormula:
    nnf_formula = to_nnf(formula)
    cnf_formula = distribute_or_over_and(nnf_formula)
    return formula_to_cnf_format(cnf_formula)


def distribute_or_over_and(formula: Formula) -> Formula:
    if isinstance(formula, Variable):
        return formula
    
    elif isinstance(formula, Not):
        return Not(distribute_or_over_and(formula.operand))
    
    elif isinstance(formula, And):
        return And(
            distribute_or_over_and(formula.left),
            distribute_or_over_and(formula.right)
        )
    
    elif isinstance(formula, Or):
        left = distribute_or_over_and(formula.left)
        right = distribute_or_over_and(formula.right)
        
        if isinstance(right, And):
            return And(
                distribute_or_over_and(Or(left, right.left)),
                distribute_or_over_and(Or(left, right.right))
            )
        
        elif isinstance(left, And):
            return And(
                distribute_or_over_and(Or(left.left, right)),
                distribute_or_over_and(Or(left.right, right))
            )
        
        else:
            return Or(left, right)
    
    else:
        raise ValueError(f"Unknown formula type: {type(formula)}")