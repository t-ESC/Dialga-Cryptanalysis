import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from SAT_Builder import SAT_Builder
from Result_Parser import Result_Parser
from pycryptosat import Solver
import pandas as pd
from tqdm import tqdm
import argparse

# pd.DataFrame([{"Input_diff": "0x1", "Round0": 1, "Round1": 2, "Round3": 3}])

def solve_SAT_problem(input_diff:int, first_round:int, probability:int, number_of_rounds:int, backwards:bool = False, threads:int = 16) -> bool:
    builder = SAT_Builder(input_diff)
    ## Rounds to be tested
    if not backwards:
        for i in range(number_of_rounds):
            builder.add_round((first_round + i) % 4)
    else:
        for i in range(number_of_rounds):
            builder.add_round_inv(3-(first_round + i) % 4)

    builder.add_probability_constraint(probability)

    s = Solver(verbose = 0, threads = threads)
    for clause in builder.clauses:
        if clause.xor:
            s.add_xor_clause([abs(var) for var in clause.variables], False)
        else:
            s.add_clause(clause.variables)

    print(f"Solving problem: Round{first_round}, P = {probability}, N = {number_of_rounds}, backwards = {backwards}")
    sat, _ = s.solve()
    print("solvable" if sat else "unsolvable")
    return sat

def find_max_round_number(backwards:bool = False, threads:int = 16, probability:int = 128):
    max_rounds = [1, 1, 1, 1]
    
    for first_round in tqdm(range(4)):
        lower = 1
        upper = 6
        while lower < upper:
            mid = (upper + lower + 1) // 2
            if solve_SAT_problem(input_diff=0, first_round=first_round, probability=probability, number_of_rounds=mid, backwards=backwards, threads=threads):
                lower = mid
            else:
                upper = mid -1

        max_rounds[first_round] = lower

    return max_rounds

def main(backwards:bool = False, threads:int = 16, probability:int = 128):
    os.makedirs("output", exist_ok=True)
    df = pd.DataFrame()
    max_rounds = find_max_round_number(backwards=backwards, threads=threads, probability=probability)
    backwards = "f" if not backwards else "b"
    df[f"{backwards}"] = max_rounds
    df.to_csv(f"output/max_rounds_{backwards}.csv")
    

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Find_max_number_of_rounds"
    )
    parser.add_argument("--backwards", "-b", action='store_true')
    parser.add_argument("--threads", "-t", type=int, default=16)
    parser.add_argument("--max_prob", "-p", type=int, default=128)
    args = parser.parse_args()
    main(args.backwards, args.threads, args.max_prob)
