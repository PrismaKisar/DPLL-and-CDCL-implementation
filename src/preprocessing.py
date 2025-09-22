from typing import Type, Callable
from src.logic_ast import Formula, Variable, Not, And, Or, Implies, Biconditional, Literal, Clause, CNFFormula


def to_nnf(formula: Formula) -> Formula:
    """
    Convert a logical formula to Negation Normal Form (NNF).

    Args:
        formula: The input logical formula

    Returns:
        The formula in NNF where negations are pushed to literals only

    Raises:
        ValueError: If the transformation fails
    """
    try:
        without_implications = eliminate_implications(formula)
        nnf_formula = push_negations_inward(without_implications)
        return nnf_formula
    except Exception as e:
        raise ValueError(f"Failed to convert to NNF: {e}") from e


def eliminate_implications(formula: Formula) -> Formula:
    """
    Eliminate implications and biconditionals from a logical formula.

    Transforms:
    - A → B becomes ¬A ∨ B
    - A ↔ B becomes (¬A ∨ B) ∧ (¬B ∨ A)
    """

    transformation_map = {
        Variable: _eliminate_implications_variable,
        Not: _eliminate_implications_not,
        And: _eliminate_implications_and,
        Or: _eliminate_implications_or,
        Implies: _eliminate_implications_implies,
        Biconditional: _eliminate_implications_biconditional,
    }

    return _apply_transformation(formula, transformation_map, "eliminate_implications")


def push_negations_inward(formula: Formula) -> Formula:
    """
    Push negations inward using De Morgan's laws.

    Transforms:
    - ¬¬A becomes A
    - ¬(A ∧ B) becomes ¬A ∨ ¬B
    - ¬(A ∨ B) becomes ¬A ∧ ¬B
    """

    transformation_map = {
        Variable: _push_negations_variable,
        Not: _push_negations_not,
        And: _push_negations_and,
        Or: _push_negations_or,
    }

    return _apply_transformation(formula, transformation_map, "push_negations_inward")


def distribute_or_over_and(formula: Formula) -> Formula:
    """
    Distribute OR over AND operations to achieve CNF structure.

    Transforms:
    - A ∨ (B ∧ C) becomes (A ∨ B) ∧ (A ∨ C)
    - (A ∧ B) ∨ C becomes (A ∨ C) ∧ (B ∨ C)
    """

    transformation_map = {
        Variable: _distribute_variable,
        Not: _distribute_not,
        And: _distribute_and,
        Or: _distribute_or,
    }

    return _apply_transformation(formula, transformation_map, "distribute_or_over_and")


def to_cnf(formula: Formula) -> CNFFormula:
    """
    Convert a logical formula to Conjunctive Normal Form (CNF).

    Args:
        formula: The input logical formula

    Returns:
        The formula in CNF format as a CNFFormula object

    Raises:
        ValueError: If the transformation fails
    """
    try:
        nnf_formula = to_nnf(formula)
        cnf_formula = distribute_or_over_and(nnf_formula)
        return formula_to_cnf_format(cnf_formula)
    except Exception as e:
        raise ValueError(f"Failed to convert to CNF: {e}") from e


def formula_to_cnf_format(formula: Formula) -> CNFFormula:
    """Convert a formula in CNF structure to CNFFormula object."""
    if _is_literal(formula):
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
        raise ValueError(f"Expected CNF formula, got {type(formula).__name__}")


def extract_literals_from_or(formula: Formula) -> list[Literal]:
    """
    Extract all literals from an OR formula using iterative approach.

    This prevents stack overflow for deeply nested OR formulas by using
    an explicit stack instead of recursion.
    """
    literals = []
    stack = [formula]

    while stack:
        current = stack.pop()

        if _is_literal(current):
            literals.append(formula_to_literal(current))
        elif isinstance(current, Or):
            # Add right first, then left (LIFO order for natural left-to-right processing)
            stack.append(current.right)
            stack.append(current.left)
        else:
            raise ValueError(f"Expected OR of literals, got {type(current).__name__}")

    return literals


def formula_to_literal(formula: Formula) -> Literal:
    """Convert a variable or negated variable to a Literal object."""
    if isinstance(formula, Variable):
        return Literal(formula.name, negated=False)
    elif isinstance(formula, Not) and isinstance(formula.operand, Variable):
        return Literal(formula.operand.name, negated=True)
    else:
        raise ValueError(f"Cannot convert {type(formula).__name__} to Literal")


# Private helper functions for transformation patterns

def _validate_formula_input(formula: Formula) -> None:
    """Validate that input is a Formula instance."""
    if not isinstance(formula, Formula):
        raise ValueError(f"Expected Formula instance, got {type(formula).__name__}")


def _apply_transformation(formula: Formula, transformation_map: dict[Type, callable], operation_name: str) -> Formula:
    """Apply transformation using the provided mapping."""
    formula_type = type(formula)
    if formula_type not in transformation_map:
        raise ValueError(f"Unknown formula type: {formula_type.__name__}")

    return transformation_map[formula_type](formula)


def _is_literal(formula: Formula) -> bool:
    """Check if formula is a literal (variable or negated variable)."""
    return isinstance(formula, Variable) or (isinstance(formula, Not) and isinstance(formula.operand, Variable))


def _transform_binary_operator(formula: Formula,
                              left_transform_func: Callable[[Formula], Formula],
                              right_transform_func: Callable[[Formula], Formula],
                              operator_class: Type[Formula]) -> Formula:
    """
    Generic helper to transform binary operators (And, Or) by applying
    transformation functions to left and right operands.

    Args:
        formula: Binary formula with left and right attributes
        left_transform_func: Function to apply to left operand
        right_transform_func: Function to apply to right operand
        operator_class: Class constructor for the result (And, Or, etc.)

    Returns:
        New formula instance with transformed operands
    """
    return operator_class(
        left_transform_func(formula.left),
        right_transform_func(formula.right)
    )


# Transformation functions for eliminate_implications

def _eliminate_implications_variable(formula: Variable) -> Formula:
    return formula


def _eliminate_implications_not(formula: Not) -> Formula:
    return Not(eliminate_implications(formula.operand))


def _eliminate_implications_and(formula: And) -> Formula:
    return _transform_binary_operator(formula, eliminate_implications, eliminate_implications, And)


def _eliminate_implications_or(formula: Or) -> Formula:
    return _transform_binary_operator(formula, eliminate_implications, eliminate_implications, Or)


def _eliminate_implications_implies(formula: Implies) -> Formula:
    return Or(
        Not(eliminate_implications(formula.left)),
        eliminate_implications(formula.right)
    )


def _eliminate_implications_biconditional(formula: Biconditional) -> Formula:
    left = eliminate_implications(formula.left)
    right = eliminate_implications(formula.right)
    return And(
        Or(Not(left), right),
        Or(Not(right), left)
    )


# Transformation functions for push_negations_inward

def _push_negations_variable(formula: Variable) -> Formula:
    return formula


def _push_negations_not(formula: Not) -> Formula:
    operand = formula.operand

    if isinstance(operand, Variable):
        return formula
    elif isinstance(operand, Not):
        # Double negation elimination
        return push_negations_inward(operand.operand)
    elif isinstance(operand, And):
        return _apply_de_morgan_to_and(operand)
    elif isinstance(operand, Or):
        return _apply_de_morgan_to_or(operand)
    else:
        raise ValueError(f"Unexpected formula under negation: {type(operand).__name__}")


def _apply_de_morgan_to_and(operand: And) -> Formula:
    """Apply De Morgan's law to AND: ¬(A ∧ B) = ¬A ∨ ¬B"""
    return Or(
        push_negations_inward(Not(operand.left)),
        push_negations_inward(Not(operand.right))
    )


def _apply_de_morgan_to_or(operand: Or) -> Formula:
    """Apply De Morgan's law to OR: ¬(A ∨ B) = ¬A ∧ ¬B"""
    return And(
        push_negations_inward(Not(operand.left)),
        push_negations_inward(Not(operand.right))
    )


def _push_negations_and(formula: And) -> Formula:
    return _transform_binary_operator(formula, push_negations_inward, push_negations_inward, And)


def _push_negations_or(formula: Or) -> Formula:
    return _transform_binary_operator(formula, push_negations_inward, push_negations_inward, Or)


# Transformation functions for distribute_or_over_and

def _distribute_variable(formula: Variable) -> Formula:
    return formula


def _distribute_not(formula: Not) -> Formula:
    return Not(distribute_or_over_and(formula.operand))


def _distribute_and(formula: And) -> Formula:
    return _transform_binary_operator(formula, distribute_or_over_and, distribute_or_over_and, And)


def _distribute_or(formula: Or) -> Formula:
    left = distribute_or_over_and(formula.left)
    right = distribute_or_over_and(formula.right)

    # Apply distributive law: A ∨ (B ∧ C) = (A ∨ B) ∧ (A ∨ C)
    if isinstance(right, And):
        return _distribute_left_over_and(left, right)
    elif isinstance(left, And):
        return _distribute_right_over_and(left, right)
    else:
        return Or(left, right)


def _distribute_left_over_and(left_operand: Formula, right_and: And) -> Formula:
    """Distribute left operand over AND: A ∨ (B ∧ C) = (A ∨ B) ∧ (A ∨ C)"""
    return And(
        distribute_or_over_and(Or(left_operand, right_and.left)),
        distribute_or_over_and(Or(left_operand, right_and.right))
    )


def _distribute_right_over_and(left_and: And, right_operand: Formula) -> Formula:
    """Distribute right operand over AND: (A ∧ B) ∨ C = (A ∨ C) ∧ (B ∨ C)"""
    return And(
        distribute_or_over_and(Or(left_and.left, right_operand)),
        distribute_or_over_and(Or(left_and.right, right_operand))
    )


def to_cnf_tseytin(formula: Formula) -> CNFFormula:
    """
    Convert a formula to CNF using Tseytin transformation.

    Process:
    1. Assign auxiliary variables z_n to each subformula
    2. Create biconditionals z_n ↔ subformula
    3. Convert each biconditional to CNF using to_nnf + distribution
    4. Combine all CNF clauses + assertion of main variable

    Args:
        formula: Input logical formula

    Returns:
        CNF formula with auxiliary variables z_n
    """
    try:
        # First eliminate implications
        nnf_formula = to_nnf(formula)

        # Apply Tseytin transformation
        transformer = TseytinTransformer()
        main_var, biconditionals = transformer.extract_biconditionals(nnf_formula)

        # Convert each biconditional to CNF and collect all clauses
        all_clauses = []
        for biconditional in biconditionals:
            biconditional_cnf = to_cnf(biconditional)
            all_clauses.extend(biconditional_cnf.clauses)

        # Add assertion that main formula is true
        main_clause = Clause([Literal(main_var, negated=False)])
        all_clauses.append(main_clause)

        return CNFFormula(all_clauses)

    except Exception as e:
        raise ValueError(f"Failed to convert to CNF using Tseytin: {e}") from e


class TseytinTransformer:
    """
    Tseytin transformation that creates biconditionals for subformulas.

    This follows the standard approach:
    1. Assign z_n variables to complex subformulas
    2. Generate biconditionals z_n ↔ subformula
    3. Let the existing CNF converter handle the biconditionals
    """

    def __init__(self):
        self.z_counter = 0
        self.biconditionals = []

    def _fresh_z_variable(self) -> str:
        """Generate fresh auxiliary variable z_n."""
        self.z_counter += 1
        return f"z_{self.z_counter}"

    def extract_biconditionals(self, formula: Formula) -> tuple[str, list[Biconditional]]:
        """
        Extract biconditionals from formula using Tseytin transformation.

        Args:
            formula: Formula in NNF (no implications, negations pushed to literals)

        Returns:
            Tuple of (main_variable, list_of_biconditionals)
        """
        self.z_counter = 0
        self.biconditionals = []

        main_var = self._process_formula(formula)

        return main_var, self.biconditionals

    def _process_formula(self, formula: Formula) -> str:
        """
        Process formula recursively, assigning z variables to complex subformulas.

        Returns:
            Variable name representing this formula
        """
        if isinstance(formula, Variable):
            return formula.name

        elif isinstance(formula, Not):
            if isinstance(formula.operand, Variable):
                # ¬p stays as is - handled by literal representation
                return formula.operand.name  # Will be negated at call site
            else:
                raise ValueError("Formula should be in NNF - negations only on variables")

        elif isinstance(formula, (And, Or)):
            # Complex subformula - assign z variable
            z_var = self._fresh_z_variable()

            # Process children first
            if isinstance(formula, And):
                left_var = self._process_formula(formula.left)
                right_var = self._process_formula(formula.right)
                # Create new formula with variable references
                processed_formula = And(
                    self._var_or_negated_var(formula.left, left_var),
                    self._var_or_negated_var(formula.right, right_var)
                )
            else:  # Or
                left_var = self._process_formula(formula.left)
                right_var = self._process_formula(formula.right)
                processed_formula = Or(
                    self._var_or_negated_var(formula.left, left_var),
                    self._var_or_negated_var(formula.right, right_var)
                )

            # Create biconditional z_var ↔ processed_formula
            biconditional = Biconditional(Variable(z_var), processed_formula)
            self.biconditionals.append(biconditional)
            return z_var

        else:
            raise ValueError(f"Unexpected formula type in NNF: {type(formula).__name__}")

    def _var_or_negated_var(self, original_formula: Formula, var_name: str) -> Formula:
        """
        Convert back to Variable or Not(Variable) based on original formula.
        """
        if isinstance(original_formula, Not):
            return Not(Variable(var_name))
        else:
            return Variable(var_name)