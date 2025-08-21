import pytest

from src.parser import tokenize

class TestParser:
    
    def test_single_variable(self):
        assert tokenize("p") == ["p"]
        assert tokenize("A") == ["A"]
    
    def test_basic_operators(self):
        assert tokenize("¬p") == ["¬", "p"]
        assert tokenize("p ∧ q") == ["p", "∧", "q"]
        assert tokenize("p ∨ q") == ["p", "∨", "q"]
        assert tokenize("p → q") == ["p", "→", "q"]
        assert tokenize("p ↔ q") == ["p", "↔", "q"]
    
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
            tokenize("p1")