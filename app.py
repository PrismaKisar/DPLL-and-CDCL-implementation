from flask import Flask, render_template, request, jsonify
from src.parser import parse
from src.preprocessing import to_cnf
from src.solver import DPLLSolver, CDCLSolver, DecisionResult
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve():
    try:
        formula_str = request.json.get('formula', '').strip()
        if not formula_str:
            return jsonify({'error': 'Please enter a formula'})

        formula = parse(formula_str)
        cnf_formula = to_cnf(formula)

        dpll_solver = DPLLSolver(cnf_formula)
        start_time = time.time()
        dpll_result = dpll_solver.solve()
        dpll_time = time.time() - start_time

        cdcl_solver = CDCLSolver(cnf_formula)
        start_time = time.time()
        cdcl_result = cdcl_solver.solve()
        cdcl_time = time.time() - start_time

        variables = {literal.variable for clause in cnf_formula.clauses
                     for literal in clause.literals}

        dpll_assignment = None
        if dpll_result == DecisionResult.SAT:
            dpll_assignment = {var: dpll_solver.assignment.get(var, False) for var in variables}

        cdcl_assignment = None
        if cdcl_result == DecisionResult.SAT:
            cdcl_assignment = {var: cdcl_solver.assignment.get(var, False) for var in variables}

        return jsonify({
            'original_formula': str(formula),
            'cnf_formula': str(cnf_formula),
            'dpll_result': dpll_result.value,
            'dpll_time': round(dpll_time * 1000, 2),
            'cdcl_result': cdcl_result.value,
            'cdcl_time': round(cdcl_time * 1000, 2),
            'dpll_assignment': dpll_assignment,
            'cdcl_assignment': cdcl_assignment
        })

    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)