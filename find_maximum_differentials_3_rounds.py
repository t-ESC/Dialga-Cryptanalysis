from SAT_Builder import SAT_Builder
from Result_Parser import Result_Parser
from pycryptosat import Solver
import pandas as pd
from tqdm import tqdm

# pd.DataFrame([{"Input_diff": "0x1", "Round0": 1, "Round1": 2, "Round3": 3}])

def solve_SAT_problem(SAT_problem: SAT_Builder) -> bool:
    s = Solver(verbose = 0, threads = 4)
    for clause in SAT_problem.clauses:
        if clause.xor:
            s.add_xor_clause([abs(var) for var in clause.variables], False)
        else:
            s.add_clause(clause.variables)

    sat, _ = s.solve()
    return sat

def find_maximum_differentials_for_input_diff(input_diff:int):
    probabilities = [0, 0, 0, 0]
    for first_round in range(4):
        sat = False
        prob = 26
        while not sat:
            builder = SAT_Builder(input_diff)
            ## Rounds to be tested
            builder.add_round(first_round)
            builder.add_round((first_round + 1) % 4)
            builder.add_round((first_round + 2) % 4)
            builder.add_probability_constraint(prob)

            if solve_SAT_problem(builder):
                sat = True
            else:
                prob += 1
        
        probabilities[first_round] = prob
    
    return probabilities





def main():
    data = []
    for value in tqdm(range(1, 16)):
        for place in tqdm(range(32), leave=False):
            input_diff = value << place*4
            probabilities = find_maximum_differentials_for_input_diff(input_diff)
            data.append(
                {
                    "Input_diff": f"{input_diff:032x}", 
                    "Round0": probabilities[0], 
                    "Round1": probabilities[1], 
                    "Round2": probabilities[2], 
                    "Round3": probabilities[3]
                    })
        

    pd.DataFrame(data).to_csv("output/1_round_differentials")
if __name__ == "__main__":
    main()
