from src.logic_ast import Formula, Variable, Not, And, Or


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
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None
    
    def consume(self) -> str:
        if self.position >= len(self.tokens):
            raise ValueError("Unexpected end of formula")
        token = self.tokens[self.position]
        self.position += 1
        return token
    
    def parse_biconditional(self) -> Formula:
        pass
    
    def parse_implication(self) -> Formula:
        pass
    
    def parse_or(self) -> Formula:
        left = self.parse_and()
        
        while self.peek() == "∨":
            self.consume()
            right = self.parse_and()
            left = Or(left, right)
        
        return left
    
    def parse_and(self) -> Formula:
        left = self.parse_not()
        
        while self.peek() == "∧":
            self.consume()
            right = self.parse_not()
            left = And(left, right)
        
        return left
    
    def parse_not(self) -> Formula:
        if self.peek() == "¬":
            self.consume()
            operand = self.parse_not()
            return Not(operand)
        
        return self.parse_primary()
    
    def parse_primary(self) -> Formula:
        token = self.peek()
        
        if token == "(":
            self.consume()
            formula = self.parse_primary()
            if self.peek() != ")":
                raise ValueError("Expected closing parenthesis")
            self.consume()
            return formula
        
        elif token and token.isalpha():
            self.consume()
            return Variable(token)
        
        else:
            raise ValueError(f"Unexpected token: {token}")


def parse(formula: str) -> Formula:
    tokens = tokenize(formula)
    parser = Parser(tokens)
    return parser.parse_biconditional()