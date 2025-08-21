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