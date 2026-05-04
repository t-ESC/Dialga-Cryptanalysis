from SAT_Builder import SAT_Builder
from Result_Parser import Result_Parser
import subprocess
from pycryptosat import Solver

MAX_SOLS = 4000

def main():
    # 0xff000000000000000000000000000000 for reference
    # builder = SAT_Builder(0xaa00000000aa00000000aa00000000aa)
    builder = SAT_Builder(0x000000000000000000000000000004)
    
    builder.add_subcell()
    builder.add_permutation(0)
    builder.add_matrix_mul()
    builder.add_subcell()
    builder.add_permutation(1)
    builder.add_matrix_mul()
    
    filename = "assertion.cnf"
    builder.to_cnf(filename)

    s = Solver()
    for clause in builder.clauses:
        if clause.xor:
            s.add_xor_clause([abs(var) for var in clause.variables], False)
        else:
            s.add_clause(clause.variables)

    solutions = [] # to find all solutions, add disallow previous solution: add it inverted to clauses
    while True:
        sat, solution = s.solve()
        if not sat:
            break

        solutions.append(solution)
        clause = []
        for var in range(1, len(solution)):
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

    # print(builder.clauses)
    # filename = "assertion.cnf"
    # builder.to_cnf(filename)

    # output = subprocess.run([
    #     "/home/theo/Thesis/SAT/cryptominisat5", 
    #     "--maxsol", "20",
    #     "--verbstat", "0", 
    #     filename], capture_output=True)
    # # print(output)
    # parser = Result_Parser(
    #     output.stdout.decode("utf-8"), 
    #     builder.label_to_variable, 
    #     builder.variable_to_label
    #     )

    # parser.parse()




if __name__ == "__main__":
    main()