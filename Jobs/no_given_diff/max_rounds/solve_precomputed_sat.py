import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from SAT_Builder import SAT_Builder
from Result_Parser import Result_Parser
from pycryptosat import Solver
import pandas as pd
from tqdm import tqdm
import argparse
import os
import subprocess

def main(threads:int = 16, first_round:int = 0, backwards:bool = False):
    os.makedirs("output", exist_ok=True)
    
    with open("output/output.out", "a") as file:
        lower = 8
        upper = 15

        while lower < upper:
            mid = (upper + lower + 1) // 2
            file.write(f"Running {mid}_rounds_{first_round}{'_back' if backwards else ''}\n")
            file.flush()
            process = subprocess.run([f'./cryptominisat5', "-s", "0", "-t", f"{threads}", f"SAT_problems/{mid}_rounds_{first_round}{'_back' if backwards else ''}.cnf",])
            match process.returncode:
                case 10:
                    lower = mid
                    file.write("sat\n")
                    file.flush()
                case 20:
                    upper = mid - 1
                    file.write("usat\n")
                    file.flush()
                case _:
                    raise Exception()
            
        


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Find_max_number_of_rounds"
    )
    parser.add_argument("--threads", "-t", type=int, default=16)
    parser.add_argument("--first_round", "-f", type=int, default=0)
    args = parser.parse_args()
    main(args.threads, args.first_round)