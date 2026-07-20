import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from SAT_Builder import SAT_Builder
from Result_Parser import Result_Parser
from pycryptosat import Solver
import pandas as pd
from tqdm import tqdm
import argparse

def build_SAT_problem(path:str, input_diff:int, first_round:int, probability:int, number_of_rounds:int, backwards:bool = False):
    builder = SAT_Builder(input_diff)

    if not backwards:
        for i in range(number_of_rounds):
            builder.add_round((first_round + i) % 4)
    else:
        for i in range(number_of_rounds):
            builder.add_round_inv(3-(first_round + i) % 4)

    builder.add_probability_constraint(probability)

    builder.to_cnf(filename=path)
        

def main():
    folder = "SAT_problems"
    os.makedirs(folder, exist_ok=True)
    for number_of_rounds in tqdm(range(8, 16)):
        for first_round in tqdm(range(4), leave=False):
            filename = f"{number_of_rounds}_rounds_{first_round}.cnf"
            build_SAT_problem(
                path=f"{folder}/{filename}", 
                input_diff=0, 
                first_round=first_round,
                probability=128,
                number_of_rounds=number_of_rounds,
                backwards=False)
            
            filename = f"{number_of_rounds}_rounds_{first_round}_back.cnf"
            build_SAT_problem(
                path=f"{folder}/{filename}", 
                input_diff=0, 
                first_round=first_round,
                probability=128,
                number_of_rounds=number_of_rounds,
                backwards=True)

if __name__ == "__main__":
    main()