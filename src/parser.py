from src.logic_ast import Formula, Variable, Not, And, Or, Implies, Biconditional


def tokenize(formula: str) -> list[str]:
    tokens: list[str] = []
    i = 0

    while i < len(formula):
        char = formula[i]

        if char.isspace():
            i += 1
            continue
        elif char in "¬∧∨→↔()":
            tokens.append(char)
            i += 1
        elif char.isalpha():
            token = ""
            while i < len(formula) and (formula[i].isalpha() or formula[i].isdigit()):
                token += formula[i]
                i += 1
            tokens.append(token)
        elif char == '-' and i + 1 < len(formula) and formula[i + 1] == '>':
            tokens.append('->')
            i += 2
        elif char == '<' and i + 2 < len(formula) and formula[i + 1:i + 3] == '->':
            tokens.append('<->')
            i += 3
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
        left = self.parse_implication()

        while self.peek() in ["↔", "<->"]:
            self.consume()
            right = self.parse_implication()
            left = Biconditional(left, right)

        return left
    
    def parse_implication(self) -> Formula:
        left = self.parse_or()

        if self.peek() in ["→", "->"]:
            self.consume()
            right = self.parse_implication()
            return Implies(left, right)

        return left
    
    def parse_or(self) -> Formula:
        left = self.parse_and()

        while self.peek() in ["∨", "or"]:
            self.consume()
            right = self.parse_and()
            left = Or(left, right)

        return left
    
    def parse_and(self) -> Formula:
        left = self.parse_not()

        while self.peek() in ["∧", "and"]:
            self.consume()
            right = self.parse_not()
            left = And(left, right)

        return left
    
    def parse_not(self) -> Formula:
        if self.peek() in ["¬", "not"]:
            self.consume()
            operand = self.parse_not()
            return Not(operand)

        return self.parse_primary()
    
    def parse_primary(self) -> Formula:
        token = self.peek()
        
        if token == "(":
            self.consume()
            formula = self.parse_biconditional()
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