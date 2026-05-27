import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from SAT_Builder import SAT_Builder
from Result_Parser import Result_Parser
from pycryptosat import Solver
import pandas as pd
from tqdm import tqdm

# pd.DataFrame([{"Input_diff": "0x1", "Round0": 1, "Round1": 2, "Round3": 3}])

def solve_SAT_problem(input_diff:int, first_round:int, probability:int) -> bool:
    builder = SAT_Builder(input_diff)
    ## Rounds to be tested
    builder.add_round_inv(3-first_round)
    builder.add_round_inv(3-(first_round + 1) % 4)
    builder.add_round_inv(3-(first_round + 2) % 4)
    builder.add_round_inv(3-(first_round + 3) % 4)
    builder.add_probability_constraint(probability)

    s = Solver(verbose = 0, threads = 16)
    for clause in builder.clauses:
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
        rough_prob = 50
        while not sat:
            if solve_SAT_problem(input_diff, first_round, rough_prob):
                sat = True
                break
            else:
                rough_prob += 10
                if rough_prob > 80:
                    break
        
        if rough_prob > 80:
            probabilities[first_round] = -rough_prob
            continue
        else:
            probabilities[first_round] = rough_prob

        for i in range(10):
            prob = (rough_prob - 10) + 1
            if solve_SAT_problem(input_diff, first_round, prob+i):
                probabilities[first_round] = prob+i
                break
    
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
                    "Round3": probabilities[0], 
                    "Round2": probabilities[1], 
                    "Round1": probabilities[2], 
                    "Round0": probabilities[3]
                    })
            break
        break
            
    
    os.makedirs("output", exist_ok=True)
    pd.DataFrame(data).to_csv("output/4_round_reverse_differentials")
if __name__ == "__main__":
    main()
