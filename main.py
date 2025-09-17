import time
import os
from typing import List, Tuple
from src.dimacs_parser import parse_dimacs_file
from src.solver import CDCLSolver, DPLLSolver, DecisionResult

ResultData = Tuple[str, DecisionResult, float, DecisionResult, float, int, int]

def solve_file(file_path: str) -> Tuple[DecisionResult, float, DecisionResult, float, int, int]:
    cnf_formula = parse_dimacs_file(file_path)
    
    variables = {literal.variable for clause in cnf_formula.clauses 
                 for literal in clause.literals}
    
    cdcl_solver = CDCLSolver(cnf_formula)
    start_time = time.time()
    cdcl_result = cdcl_solver.solve()
    cdcl_time = time.time() - start_time
    
    dpll_solver = DPLLSolver(cnf_formula)
    start_time = time.time()
    dpll_result = dpll_solver.solve()
    dpll_time = time.time() - start_time
    
    return cdcl_result, cdcl_time, dpll_result, dpll_time, len(cnf_formula.clauses), len(variables)

def generate_test_files(type: str, start: int, end: int) -> List[str]:
    if type == 'sat':
        return [f"satlib/{type}/uf75-0{i}.cnf" for i in range(start, end + 1)]
    return [f"satlib/{type}/uuf75-0{i}.cnf" for i in range(start, end + 1)]


def print_header() -> None:
    print(f"{'File':<15} {'CDCL':<10} {'Time':<8} {'DPLL':<10} {'Time':<8}")
    print("-" * 51)

def print_result_line(filename: str, cdcl_result: DecisionResult, cdcl_time: float,
                     dpll_result: DecisionResult, dpll_time: float) -> None:
    cdcl_str = "SAT" if cdcl_result == DecisionResult.SAT else "UNSAT"
    dpll_str = "SAT" if dpll_result == DecisionResult.SAT else "UNSAT"
    print(f"{filename:<15} {cdcl_str:<10} {cdcl_time:<8.4f} {dpll_str:<10} {dpll_time:<8.4f}")

def print_error_line(filename: str) -> None:
    print(f"{filename:<15} {'ERROR':<10} {'N/A':<8} {'ERROR':<10} {'N/A':<8}")

def solve_benchmark(test_files: List[str]) -> List[ResultData]:
    results: List[ResultData] = []
    total_cdcl_time = 0.0
    total_dpll_time = 0.0
    
    for file_path in test_files:
        filename = os.path.basename(file_path)
        
        try:
            cdcl_result, cdcl_time, dpll_result, dpll_time, num_clauses, num_variables = solve_file(file_path)
            print_result_line(filename, cdcl_result, cdcl_time, dpll_result, dpll_time)
            
            total_cdcl_time += cdcl_time
            total_dpll_time += dpll_time
            results.append((filename, cdcl_result, cdcl_time, dpll_result, dpll_time, num_clauses, num_variables))
            
        except FileNotFoundError:
            print_error_line(filename)
        except Exception:
            print_error_line(filename)
    
    print("-" * 51)
    print(f"{'TOTAL':<15} {'':<10} {total_cdcl_time:<8.4f} {'':<10} {total_dpll_time:<8.4f}")
    return results

if __name__ == "__main__":
    n_formulas = 10
    
    print("=== SAT Files ===")
    test_files = generate_test_files('sat', 1, n_formulas)
    print_header()
    sat_results = solve_benchmark(test_files)
    
    print("\n=== UNSAT Files ===")
    test_files = generate_test_files('unsat', 1, n_formulas)
    print_header()
    unsat_results = solve_benchmark(test_files)
    
    total_cdcl = sum(r[2] for r in sat_results + unsat_results)
    total_dpll = sum(r[4] for r in sat_results + unsat_results)
    print("\n=== OVERALL TOTALS ===")
    print(f"CDCL: {total_cdcl:.4f}s")
    print(f"DPLL: {total_dpll:.4f}s")
    print(f"Difference: {total_dpll - total_cdcl:.4f}s ({((total_dpll/total_cdcl-1)*100):.1f}% slower)" if total_cdcl > 0 else "")
