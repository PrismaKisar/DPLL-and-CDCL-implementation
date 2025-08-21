from src.logic_ast import Formula


def tokenize(formula: str) -> list[str]:
    tokens: list[str] = []
    
    for char in formula:
        if char.isalpha() or char in "¬∧∨→↔()":
            tokens.append(char)
        elif char.isspace():
            continue
        else:
            raise ValueError(f"Invalid character '{char}' in formula")
    
    return tokens


class Parser:
    def __init__(self, tokens: list[str]):
        self.tokens = tokens
        self.position = 0
    
    def peek(self) -> str | None:
        pass
    
    def consume(self) -> str:
        pass
    
    def parse_biconditional(self) -> Formula:
        pass
    
    def parse_implication(self) -> Formula:
        pass
    
    def parse_or(self) -> Formula:
        pass
    
    def parse_and(self) -> Formula:
        pass
    
    def parse_not(self) -> Formula:
        pass
    
    def parse_primary(self) -> Formula:
        pass
