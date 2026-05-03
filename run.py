from SAT_Builder import SAT_Builder
from Result_Parser import Result_Parser
import subprocess
from pycryptosat import Solver

def main():
    # 0xff000000000000000000000000000000 for reference
    # builder = SAT_Builder(0xaa000000aa000000aa000000aa000000)
    builder = SAT_Builder(0xaa00000000aa00000000aa00000000aa)
    builder.add_subcell()
    
    filename = "assertion.cnf"
    builder.to_cnf(filename)

    s = Solver()
    for clause in builder.clauses:
        if clause.xor:
            s.add_xor_clause([abs(var) for var in clause.variables], False)
        else:
            s.add_clause(clause.variables)

    sat, solution = s.solve()

    parser = Result_Parser(
        solution,
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