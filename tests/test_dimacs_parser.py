import pytest
import tempfile
import os

from src.dimacs_parser import parse_dimacs_string, parse_dimacs_file


class TestParseDimacsString:
    
    def test_simple_formula(self):
        dimacs_content = """c Simple test formula
p cnf 2 2
1 -2 0
-1 2 0"""
        
        cnf = parse_dimacs_string(dimacs_content)
        
        assert len(cnf.clauses) == 2
        
        clause1 = cnf.clauses[0]
        assert len(clause1.literals) == 2
        assert clause1.literals[0].variable == "x1"
        assert clause1.literals[0].negated == False
        assert clause1.literals[1].variable == "x2"
        assert clause1.literals[1].negated == True
        
        clause2 = cnf.clauses[1]
        assert len(clause2.literals) == 2
        assert clause2.literals[0].variable == "x1"
        assert clause2.literals[0].negated == True
        assert clause2.literals[1].variable == "x2"
        assert clause2.literals[1].negated == False
    
    def test_single_variable_clause(self):
        dimacs_content = """p cnf 1 1
1 0"""
        
        cnf = parse_dimacs_string(dimacs_content)
        
        assert len(cnf.clauses) == 1
        clause = cnf.clauses[0]
        assert len(clause.literals) == 1
        assert clause.literals[0].variable == "x1"
        assert clause.literals[0].negated == False
    
    def test_empty_formula(self):
        dimacs_content = """p cnf 0 0"""
        
        cnf = parse_dimacs_string(dimacs_content)
        
        assert len(cnf.clauses) == 0
    
    def test_comments_ignored(self):
        dimacs_content = """c This is a comment
c Another comment
p cnf 1 1
c Comment in the middle
1 0
c Final comment"""
        
        cnf = parse_dimacs_string(dimacs_content)
        
        assert len(cnf.clauses) == 1
        assert cnf.clauses[0].literals[0].variable == "x1"
    
    def test_empty_lines_ignored(self):
        dimacs_content = """
p cnf 1 1

1 0

"""
        
        cnf = parse_dimacs_string(dimacs_content)
        
        assert len(cnf.clauses) == 1
        assert cnf.clauses[0].literals[0].variable == "x1"
    
    def test_three_sat_problem(self):
        dimacs_content = """p cnf 3 3
1 2 3 0
-1 -2 3 0
1 -2 -3 0"""
        
        cnf = parse_dimacs_string(dimacs_content)
        
        assert len(cnf.clauses) == 3
        
        clause1 = cnf.clauses[0]
        assert len(clause1.literals) == 3
        assert all(not lit.negated for lit in clause1.literals)
        
        clause2 = cnf.clauses[1]
        assert clause2.literals[0].negated == True
        assert clause2.literals[1].negated == True
        assert clause2.literals[2].negated == False
    
    def test_invalid_header_format(self):
        dimacs_content = """p cnf 2"""
        
        with pytest.raises(ValueError, match="Invalid DIMACS header"):
            parse_dimacs_string(dimacs_content)
    
    def test_clause_without_zero_terminator(self):
        dimacs_content = """p cnf 2 1
1 -2"""
        
        with pytest.raises(ValueError, match="Clause must end with 0"):
            parse_dimacs_string(dimacs_content)
    
    def test_variable_exceeds_declared_count(self):
        dimacs_content = """p cnf 2 1
3 0"""
        
        with pytest.raises(ValueError, match="Variable 3 exceeds declared variables 2"):
            parse_dimacs_string(dimacs_content)
    
    def test_clause_count_mismatch(self):
        dimacs_content = """p cnf 2 2
1 -2 0"""
        
        with pytest.raises(ValueError, match="Expected 2 clauses, found 1"):
            parse_dimacs_string(dimacs_content)
    
    def test_negative_variable_parsing(self):
        dimacs_content = """p cnf 1 1
-1 0"""
        
        cnf = parse_dimacs_string(dimacs_content)
        
        literal = cnf.clauses[0].literals[0]
        assert literal.variable == "x1"
        assert literal.negated == True
    
    def test_large_formula(self):
        dimacs_content = """p cnf 5 4
1 2 -3 4 -5 0
-1 3 0
2 -4 5 0
-2 -3 4 0"""
        
        cnf = parse_dimacs_string(dimacs_content)
        
        assert len(cnf.clauses) == 4
        assert len(cnf.clauses[0].literals) == 5
        assert len(cnf.clauses[1].literals) == 2
        assert len(cnf.clauses[2].literals) == 3
        assert len(cnf.clauses[3].literals) == 3
    
    def test_zero_in_middle_breaks_clause(self):
        dimacs_content = """p cnf 3 1
1 0 2 3 0"""
        
        cnf = parse_dimacs_string(dimacs_content)
        
        assert len(cnf.clauses) == 1
        assert len(cnf.clauses[0].literals) == 1
        assert cnf.clauses[0].literals[0].variable == "x1"


class TestParseDimacsFile:
    
    def test_parse_file(self):
        dimacs_content = """c Test file
p cnf 2 1
1 -2 0"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.cnf') as f:
            f.write(dimacs_content)
            temp_file = f.name
        
        try:
            cnf = parse_dimacs_file(temp_file)
            
            assert len(cnf.clauses) == 1
            assert len(cnf.clauses[0].literals) == 2
            assert cnf.clauses[0].literals[0].variable == "x1"
            assert cnf.clauses[0].literals[1].variable == "x2"
            assert cnf.clauses[0].literals[1].negated == True
            
        finally:
            os.unlink(temp_file)