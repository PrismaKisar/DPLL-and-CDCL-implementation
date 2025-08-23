from typing import List
from src.logic_ast import CNFFormula, Clause, Literal


def parse_dimacs_file(file_path: str) -> CNFFormula:
    with open(file_path, 'r') as f:
        return parse_dimacs_string(f.read())


def parse_dimacs_string(dimacs_content: str) -> CNFFormula:
    lines = dimacs_content.strip().split('\n')
    
    num_variables = 0
    num_clauses = 0
    clauses: List[Clause] = []
    
    for line in lines:
        line = line.strip()
        
        if not line or line.startswith('c') or line == '%':
            continue
            
        if line.startswith('p cnf'):
            parts = line.split()
            if len(parts) != 4:
                raise ValueError(f"Invalid DIMACS header: {line}")
            num_variables = int(parts[2])
            num_clauses = int(parts[3])
            continue
        
        if line == '0':
            continue
            
        literals_str = line.split()
        if not literals_str or literals_str[-1] != '0':
            raise ValueError(f"Clause must end with 0: {line}")
        
        literals: List[Literal] = []
        for lit_str in literals_str[:-1]:
            lit_num = int(lit_str)
            if lit_num == 0:
                break
            
            if abs(lit_num) > num_variables:
                raise ValueError(f"Variable {abs(lit_num)} exceeds declared variables {num_variables}")
            
            variable_name = f"x{abs(lit_num)}"
            is_negated = lit_num < 0
            literals.append(Literal(variable_name, negated=is_negated))
        
        if literals:
            clauses.append(Clause(literals))
    
    if len(clauses) != num_clauses:
        raise ValueError(f"Expected {num_clauses} clauses, found {len(clauses)}")
    
    return CNFFormula(clauses)