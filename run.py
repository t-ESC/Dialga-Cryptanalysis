from SAT_Builder import SAT_Builder
from Result_Parser import Result_Parser
import subprocess
from pycryptosat import Solver

MAX_SOLS = 5

def main():
    # 0xff000000000000000000000000000000 for reference
    # builder = SAT_Builder(0xaa00000000aa00000000aa00000000aa)
    builder = SAT_Builder(0x2)

    builder.add_round_inv(0)
    builder.add_round_inv(3)
    builder.add_round_inv(2)
    builder.add_round_inv(1)
    # builder.add_round(0)
    builder.add_probability_constraint(65)
    
    filename = "assertion.cnf"
    builder.to_cnf(filename)

    s = Solver(verbose=0, threads=16)
    for clause in builder.clauses:
        if clause.xor:
            s.add_xor_clause([abs(var) for var in clause.variables], False)
        else:
            s.add_clause(clause.variables)

    solutions = [] # to find all solutions, add disallow previous solution: add it inverted to clauses
    while True:
        sat, solution = s.solve()
        if not sat:
            print("UnSAT")
            break
        else:
            print("Solution found")

        solutions.append(solution)
        clause = []
        for var in range(1, len(solution)):
            if var in builder.auxilary_variables: #  Ignore auxilary variables in solutions
                continue
            if solution[var]:
                clause.append(-var)
            else:
                clause.append(var)
        
        s.add_clause(clause)

        if len(solutions) >= MAX_SOLS:
            break

    parser = Result_Parser(
        solutions,
        builder.label_to_variable,
        builder.variable_to_label
    )

    parser.parse()




if __name__ == "__main__":
    main()