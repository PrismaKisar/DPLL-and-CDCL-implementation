# SAT Solver Implementation: DPLL & CDCL

## Project Overview
This project implements **DPLL (Davis-Putnam-Logemann-Loveland)** and **CDCL (Conflict-Driven Clause Learning)** algorithms from scratch for solving the Boolean Satisfiability Problem (SAT). The implementation includes complete pre-processing pipelines to transform logical formulas into the required normal forms (NNF, CNF) while preserving equisatisfiability.

## Implementation Scope
The project covers three main components: **pre-processing** (parsing propositional formulas and converting to CNF via Tseytin transformation), **DPLL algorithm** (unit propagation, pure literal elimination, chronological backtracking), and **CDCL enhancement** (conflict analysis with 1UIP, clause learning, non-chronological backtracking, restart strategies). This demonstrates the evolution from classical SAT solving to modern industrial-strength algorithms used in formal verification and automated reasoning.

## Academic Integrity
This project was completed in accordance with academic integrity policies. All implementations are original work based on standard algorithms from the literature, with appropriate citations for theoretical foundations and algorithmic descriptions.

## License
This project is for educational purposes as part of the Mathematical Logic course curriculum.

## Contact
- **Author**: Alessandro Sarchi
- **Email**: alessandro.sarchi@gmail.com
- **Course**: Mathematical Logic
- **Institution**: University of Milan