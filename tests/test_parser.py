import pytest

from src.parser import tokenize, Parser, parse
from src.logic_ast import Variable, Not, And, Or, Implies, Biconditional

class TestTokenize:
    
    def test_single_variable(self):
        assert tokenize("p") == ["p"]
        assert tokenize("A") == ["A"]
    
    def test_basic_operators(self):
        assert tokenize("¬p") == ["¬", "p"]
        assert tokenize("p ∧ q") == ["p", "∧", "q"]
        assert tokenize("p ∨ q") == ["p", "∨", "q"]
        assert tokenize("p → q") == ["p", "→", "q"]
        assert tokenize("p ↔ q") == ["p", "↔", "q"]

    def test_text_operators(self):
        assert tokenize("not p") == ["not", "p"]
        assert tokenize("p and q") == ["p", "and", "q"]
        assert tokenize("p or q") == ["p", "or", "q"]
        assert tokenize("p -> q") == ["p", "->", "q"]
        assert tokenize("p <-> q") == ["p", "<->", "q"]
    
    def test_parentheses(self):
        assert tokenize("(p ∧ q)") == ["(", "p", "∧", "q", ")"]
        assert tokenize("¬(p ∨ q)") == ["¬", "(", "p", "∨", "q", ")"]
    
    def test_spaces(self):
        assert tokenize("p∧q") == ["p", "∧", "q"]
        assert tokenize("  p ∧ q  ") == ["p", "∧", "q"]
    
    def test_empty_string(self):
        assert tokenize("") == []
    
    def test_invalid_characters(self):
        with pytest.raises(ValueError, match="Invalid character"):
            tokenize("p & q")

        with pytest.raises(ValueError, match="Invalid character"):
            tokenize("p%q")


class TestParser:
    
    def test_parser_init(self):
        tokens = ["p", "∧", "q"]
        parser = Parser(tokens)
        assert parser.tokens == tokens
        assert parser.position == 0
    
    def test_peek(self):
        parser = Parser(["p", "∧", "q"])
        assert parser.peek() == "p"
        assert parser.position == 0
    
    def test_peek_at_end(self):
        parser = Parser(["p"])
        parser.position = 1
        assert parser.peek() is None
    
    def test_consume(self):
        parser = Parser(["p", "∧", "q"])
        assert parser.consume() == "p"
        assert parser.position == 1
        assert parser.consume() == "∧"
        assert parser.position == 2
    
    def test_consume_at_end(self):
        parser = Parser(["p"])
        parser.consume()
        with pytest.raises(ValueError, match="Unexpected end of formula"):
            parser.consume()
    
    def test_parse_primary_variable(self):
        parser = Parser(["p"])
        result = parser.parse_primary()
        assert isinstance(result, Variable)
        assert result.name == "p"
    
    def test_parse_primary_parentheses(self):
        parser = Parser(["(", "p", ")"])
        result = parser.parse_primary()
        assert isinstance(result, Variable)
        assert result.name == "p"
    
    def test_parse_primary_missing_closing_paren(self):
        parser = Parser(["(", "p"])
        with pytest.raises(ValueError, match="Expected closing parenthesis"):
            parser.parse_primary()
    
    def test_parse_primary_unexpected_token(self):
        parser = Parser(["∧"])
        with pytest.raises(ValueError, match="Unexpected token"):
            parser.parse_primary()
    
    def test_parse_not_variable(self):
        parser = Parser(["¬", "p"])
        result = parser.parse_not()
        assert isinstance(result, Not)
        assert isinstance(result.operand, Variable)
        assert result.operand.name == "p"
    
    def test_parse_not_double_negation(self):
        parser = Parser(["¬", "¬", "p"])
        result = parser.parse_not()
        assert isinstance(result, Not)
        assert isinstance(result.operand, Not)
        assert isinstance(result.operand.operand, Variable)
        assert result.operand.operand.name == "p"
    
    def test_parse_not_without_negation(self):
        parser = Parser(["p"])
        result = parser.parse_not()
        assert isinstance(result, Variable)
        assert result.name == "p"
    
    def test_parse_and_simple(self):
        parser = Parser(["p", "∧", "q"])
        result = parser.parse_and()
        assert isinstance(result, And)
        assert isinstance(result.left, Variable)
        assert result.left.name == "p"
        assert isinstance(result.right, Variable)
        assert result.right.name == "q"
    
    def test_parse_and_multiple(self):
        parser = Parser(["p", "∧", "q", "∧", "r"])
        result = parser.parse_and()
        assert isinstance(result, And)
        assert isinstance(result.left, And)
        assert isinstance(result.left.left, Variable)
        assert result.left.left.name == "p"
        assert isinstance(result.left.right, Variable)
        assert result.left.right.name == "q"
        assert isinstance(result.right, Variable)
        assert result.right.name == "r"
    
    def test_parse_and_with_negation(self):
        parser = Parser(["¬", "p", "∧", "q"])
        result = parser.parse_and()
        assert isinstance(result, And)
        assert isinstance(result.left, Not)
        assert isinstance(result.left.operand, Variable)
        assert result.left.operand.name == "p"
        assert isinstance(result.right, Variable)
        assert result.right.name == "q"
    
    def test_parse_and_without_and(self):
        parser = Parser(["p"])
        result = parser.parse_and()
        assert isinstance(result, Variable)
        assert result.name == "p"
    
    def test_parse_or_simple(self):
        parser = Parser(["p", "∨", "q"])
        result = parser.parse_or()
        assert isinstance(result, Or)
        assert isinstance(result.left, Variable)
        assert result.left.name == "p"
        assert isinstance(result.right, Variable)
        assert result.right.name == "q"
    
    def test_parse_or_multiple(self):
        parser = Parser(["p", "∨", "q", "∨", "r"])
        result = parser.parse_or()
        assert isinstance(result, Or)
        assert isinstance(result.left, Or)
        assert isinstance(result.left.left, Variable)
        assert result.left.left.name == "p"
        assert isinstance(result.left.right, Variable)
        assert result.left.right.name == "q"
        assert isinstance(result.right, Variable)
        assert result.right.name == "r"
    
    def test_parse_or_with_and(self):
        parser = Parser(["p", "∧", "q", "∨", "r"])
        result = parser.parse_or()
        assert isinstance(result, Or)
        assert isinstance(result.left, And)
        assert isinstance(result.left.left, Variable)
        assert result.left.left.name == "p"
        assert isinstance(result.left.right, Variable)
        assert result.left.right.name == "q"
        assert isinstance(result.right, Variable)
        assert result.right.name == "r"
    
    def test_parse_or_without_or(self):
        parser = Parser(["p"])
        result = parser.parse_or()
        assert isinstance(result, Variable)
        assert result.name == "p"
    
    def test_parse_implication_simple(self):
        parser = Parser(["p", "→", "q"])
        result = parser.parse_implication()
        assert isinstance(result, Implies)
        assert isinstance(result.left, Variable)
        assert result.left.name == "p"
        assert isinstance(result.right, Variable)
        assert result.right.name == "q"
    
    def test_parse_implication_right_associative(self):
        parser = Parser(["p", "→", "q", "→", "r"])
        result = parser.parse_implication()
        assert isinstance(result, Implies)
        assert isinstance(result.left, Variable)
        assert result.left.name == "p"
        assert isinstance(result.right, Implies)
        assert isinstance(result.right.left, Variable)
        assert result.right.left.name == "q"
        assert isinstance(result.right.right, Variable)
        assert result.right.right.name == "r"
    
    def test_parse_implication_with_or(self):
        parser = Parser(["p", "∨", "q", "→", "r"])
        result = parser.parse_implication()
        assert isinstance(result, Implies)
        assert isinstance(result.left, Or)
        assert isinstance(result.left.left, Variable)
        assert result.left.left.name == "p"
        assert isinstance(result.left.right, Variable)
        assert result.left.right.name == "q"
        assert isinstance(result.right, Variable)
        assert result.right.name == "r"
    
    def test_parse_implication_without_implies(self):
        parser = Parser(["p"])
        result = parser.parse_implication()
        assert isinstance(result, Variable)
        assert result.name == "p"
    
    def test_parse_biconditional_simple(self):
        parser = Parser(["p", "↔", "q"])
        result = parser.parse_biconditional()
        assert isinstance(result, Biconditional)
        assert isinstance(result.left, Variable)
        assert result.left.name == "p"
        assert isinstance(result.right, Variable)
        assert result.right.name == "q"
    
    def test_parse_biconditional_multiple(self):
        parser = Parser(["p", "↔", "q", "↔", "r"])
        result = parser.parse_biconditional()
        assert isinstance(result, Biconditional)
        assert isinstance(result.left, Biconditional)
        assert isinstance(result.left.left, Variable)
        assert result.left.left.name == "p"
        assert isinstance(result.left.right, Variable)
        assert result.left.right.name == "q"
        assert isinstance(result.right, Variable)
        assert result.right.name == "r"
    
    def test_parse_biconditional_with_implication(self):
        parser = Parser(["p", "→", "q", "↔", "r"])
        result = parser.parse_biconditional()
        assert isinstance(result, Biconditional)
        assert isinstance(result.left, Implies)
        assert isinstance(result.left.left, Variable)
        assert result.left.left.name == "p"
        assert isinstance(result.left.right, Variable)
        assert result.left.right.name == "q"
        assert isinstance(result.right, Variable)
        assert result.right.name == "r"
    
    def test_parse_biconditional_without_biconditional(self):
        parser = Parser(["p"])
        result = parser.parse_biconditional()
        assert isinstance(result, Variable)
        assert result.name == "p"


class TestParse:

    def test_parse_simple_variable(self):
        result = parse("p")
        assert isinstance(result, Variable)
        assert result.name == "p"

    def test_parse_negation(self):
        result = parse("¬p")
        assert isinstance(result, Not)
        assert isinstance(result.operand, Variable)
        assert result.operand.name == "p"

    def test_parse_text_negation(self):
        result = parse("not p")
        assert isinstance(result, Not)
        assert isinstance(result.operand, Variable)
        assert result.operand.name == "p"

    def test_parse_text_and(self):
        result = parse("p and q")
        assert isinstance(result, And)
        assert isinstance(result.left, Variable)
        assert result.left.name == "p"
        assert isinstance(result.right, Variable)
        assert result.right.name == "q"

    def test_parse_text_or(self):
        result = parse("p or q")
        assert isinstance(result, Or)
        assert isinstance(result.left, Variable)
        assert result.left.name == "p"
        assert isinstance(result.right, Variable)
        assert result.right.name == "q"

    def test_parse_text_implication(self):
        result = parse("p -> q")
        assert isinstance(result, Implies)
        assert isinstance(result.left, Variable)
        assert result.left.name == "p"
        assert isinstance(result.right, Variable)
        assert result.right.name == "q"

    def test_parse_text_biconditional(self):
        result = parse("p <-> q")
        assert isinstance(result, Biconditional)
        assert isinstance(result.left, Variable)
        assert result.left.name == "p"
        assert isinstance(result.right, Variable)
        assert result.right.name == "q"

    def test_parse_complex_formula(self):
        result = parse("(p ∧ q) → (¬r ∨ s)")
        assert isinstance(result, Implies)
        assert isinstance(result.left, And)
        assert isinstance(result.right, Or)
        assert isinstance(result.right.left, Not)

    def test_parse_complex_text_formula(self):
        result = parse("(p and q) -> (not r or s)")
        assert isinstance(result, Implies)
        assert isinstance(result.left, And)
        assert isinstance(result.right, Or)
        assert isinstance(result.right.left, Not)

    def test_parse_precedence(self):
        result = parse("p ∨ q ∧ r")
        assert isinstance(result, Or)
        assert isinstance(result.left, Variable)
        assert result.left.name == "p"
        assert isinstance(result.right, And)
        assert isinstance(result.right.left, Variable)
        assert result.right.left.name == "q"
        assert isinstance(result.right.right, Variable)
        assert result.right.right.name == "r"
    
    def test_parse_negation_with_parentheses(self):
        result = parse("¬(p ∧ q)")
        assert isinstance(result, Not)
        assert isinstance(result.operand, And)
        assert isinstance(result.operand.left, Variable)
        assert result.operand.left.name == "p"
        assert isinstance(result.operand.right, Variable)
        assert result.operand.right.name == "q"
    
    def test_parse_complex_implication_chain(self):
        result = parse("p → q → r ∧ s")
        assert isinstance(result, Implies)
        assert isinstance(result.left, Variable)
        assert result.left.name == "p"
        assert isinstance(result.right, Implies)
        assert isinstance(result.right.left, Variable)
        assert result.right.left.name == "q"
        assert isinstance(result.right.right, And)
        assert isinstance(result.right.right.left, Variable)
        assert result.right.right.left.name == "r"
        assert isinstance(result.right.right.right, Variable)
        assert result.right.right.right.name == "s"
    
    def test_parse_nested_biconditional_with_negation(self):
        result = parse("¬p ↔ (q ∨ r) → ¬s")
        assert isinstance(result, Biconditional)
        assert isinstance(result.left, Not)
        assert isinstance(result.left.operand, Variable)
        assert result.left.operand.name == "p"
        assert isinstance(result.right, Implies)
        assert isinstance(result.right.left, Or)
        assert isinstance(result.right.left.left, Variable)
        assert result.right.left.left.name == "q"
        assert isinstance(result.right.left.right, Variable)
        assert result.right.left.right.name == "r"
        assert isinstance(result.right.right, Not)
        assert isinstance(result.right.right.operand, Variable)
        assert result.right.right.operand.name == "s"