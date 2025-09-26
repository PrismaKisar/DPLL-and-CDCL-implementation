import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify
from src.parser import parse
from src.preprocessing import to_cnf_tseytin, to_cnf, ensure_3cnf, is_3cnf
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

        # Check if user wants Tseytin transformation
        apply_tseytin = request.json.get('apply_tseytin', False)  # Default False (checkbox unchecked)

        if apply_tseytin:
            cnf_formula = to_cnf_tseytin(formula)
            conversion_method = "Tseytin"
        else:
            cnf_formula = to_cnf(formula)
            conversion_method = "Classic CNF"

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
            'cdcl_assignment': cdcl_assignment,
            'is_dimacs': False,
            'conversion_method': conversion_method,
            'apply_tseytin': apply_tseytin
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
            original_cnf_formula = parse_dimacs_file(temp_file_path)

            # Check if user wants 3-CNF conversion
            apply_3cnf = request.form.get('apply_3cnf', 'false').lower() == 'true'

            if apply_3cnf:
                is_already_3cnf = is_3cnf(original_cnf_formula)
                cnf_formula = ensure_3cnf(original_cnf_formula) if not is_already_3cnf else original_cnf_formula
                was_converted = not is_already_3cnf
            else:
                cnf_formula = original_cnf_formula
                was_converted = False

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
                'original_formula': str(original_cnf_formula),
                'cnf_formula': str(cnf_formula),
                'dpll_result': dpll_result.value,
                'dpll_time': format_time(dpll_time),
                'cdcl_result': cdcl_result.value,
                'cdcl_time': format_time(cdcl_time),
                'dpll_assignment': dpll_assignment,
                'cdcl_assignment': cdcl_assignment,
                'is_dimacs': True,
                'filename': file.filename,
                'apply_3cnf': apply_3cnf,
                'was_converted_to_3cnf': was_converted,
                'original_clauses_count': len(original_cnf_formula.clauses),
                'final_clauses_count': len(cnf_formula.clauses)
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
    import socket

    def find_free_port(preferred_ports=[5000, 8080, 8000, 3000]):
        """Find a free port, trying preferred ports first, then scanning a range."""
        # Try preferred ports first
        for port in preferred_ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind(('0.0.0.0', port))
                    return port
            except OSError:
                continue

        # If preferred ports are taken, scan a wider range
        for port in range(8080, 8200):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind(('0.0.0.0', port))
                    return port
            except OSError:
                continue
        return None

    # Determine port with better error handling
    if os.environ.get('PORT'):
        try:
            port = int(os.environ.get('PORT'))
            print(f"Using environment PORT: {port}")
        except ValueError:
            print("Invalid PORT environment variable, finding free port...")
            port = find_free_port()
    else:
        port = find_free_port()

    if port is None:
        print("No free port found in range 5000, 8000-8199")
        print("Please close other applications using these ports or set a specific PORT environment variable")
        sys.exit(1)

    print(f"Starting Flask server on port {port}")
    print(f"Open your browser to: http://127.0.0.1:{port}")

    if os.environ.get('RENDER_EXTERNAL_URL'):
        ping_thread = threading.Thread(target=ping_self, daemon=True)
        ping_thread.start()

    app.run(host='0.0.0.0', port=port, debug=False)