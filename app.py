import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify
from src.parser import parse
from src.preprocessing import to_cnf_tseytin
from src.solver import DPLLSolver, CDCLSolver, DecisionResult
from src.dimacs_parser import parse_dimacs_file
import tempfile
import time
import threading
import requests
from datetime import datetime

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
        cnf_formula = to_cnf_tseytin(formula)

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

        def format_time(time_seconds):
            if time_seconds >= 1.0:
                return f"{time_seconds:.2f}s"
            else:
                return f"{time_seconds * 1000:.2f}ms"

        return jsonify({
            'original_formula': str(formula),
            'cnf_formula': str(cnf_formula),
            'dpll_result': dpll_result.value,
            'dpll_time': format_time(dpll_time),
            'cdcl_result': cdcl_result.value,
            'cdcl_time': format_time(cdcl_time),
            'dpll_assignment': dpll_assignment,
            'cdcl_assignment': cdcl_assignment
        })

    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'})

@app.route('/solve_dimacs', methods=['POST'])
def solve_dimacs():
    try:
        if 'dimacs_file' not in request.files:
            return jsonify({'error': 'No file uploaded'})

        file = request.files['dimacs_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'})

        with tempfile.NamedTemporaryFile(mode='w+', suffix='.cnf', delete=False) as temp_file:
            file_content = file.read().decode('utf-8')
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        try:
            cnf_formula = parse_dimacs_file(temp_file_path)

            variables = {literal.variable for clause in cnf_formula.clauses
                        for literal in clause.literals}

            dpll_solver = DPLLSolver(cnf_formula)
            start_time = time.time()
            dpll_result = dpll_solver.solve()
            dpll_time = time.time() - start_time

            cdcl_solver = CDCLSolver(cnf_formula)
            start_time = time.time()
            cdcl_result = cdcl_solver.solve()
            cdcl_time = time.time() - start_time

            dpll_assignment = None
            if dpll_result == DecisionResult.SAT:
                dpll_assignment = {var: dpll_solver.assignment.get(var, False) for var in variables}

            cdcl_assignment = None
            if cdcl_result == DecisionResult.SAT:
                cdcl_assignment = {var: cdcl_solver.assignment.get(var, False) for var in variables}

            def format_time(time_seconds):
                if time_seconds >= 1.0:
                    return f"{time_seconds:.2f}s"
                else:
                    return f"{time_seconds * 1000:.2f}ms"

            return jsonify({
                'original_formula': f"DIMACS file: {file.filename}",
                'cnf_formula': str(cnf_formula),
                'dpll_result': dpll_result.value,
                'dpll_time': format_time(dpll_time),
                'cdcl_result': cdcl_result.value,
                'cdcl_time': format_time(cdcl_time),
                'dpll_assignment': dpll_assignment,
                'cdcl_assignment': cdcl_assignment
            })

        finally:
            os.unlink(temp_file_path)

    except Exception as e:
        return jsonify({'error': f'Error processing DIMACS file: {str(e)}'})

@app.route('/keep-alive')
def keep_alive():
    return jsonify({'status': 'alive', 'timestamp': datetime.now().isoformat()})

def ping_self():
    url = os.environ.get('RENDER_EXTERNAL_URL', 'https://dpll-and-cdcl-implementation.onrender.com') + '/keep-alive'
    while True:
        try:
            time.sleep(600)
            requests.get(url, timeout=10)
            print(f"Keep-alive ping sent at {datetime.now()}")
        except Exception as e:
            print(f"Keep-alive ping failed: {e}")

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))

    if os.environ.get('RENDER_EXTERNAL_URL'):
        ping_thread = threading.Thread(target=ping_self, daemon=True)
        ping_thread.start()

    app.run(host='0.0.0.0', port=port, debug=False)