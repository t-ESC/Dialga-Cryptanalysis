import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from SAT_Builder import SAT_Builder
from Result_Parser import Result_Parser
from pycryptosat import Solver
import pandas as pd
from tqdm import tqdm
import argparse
import sqlite3

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

    sat, _ = s.solve()
    return sat

def find_maximum_differentials_for_input_diff(input_diff:int, first_round:int, number_of_rounds:int, backwards:bool = False, threads:int = 16) -> int:
    low = 1
    upper = 128

    while low + 1 < upper:
        mid = (low+upper) // 2
        if solve_SAT_problem(input_diff, first_round, mid, number_of_rounds, backwards, threads):
            upper = mid
        else:
            low = mid
    
    return upper
    

def permbits(input:int):
    PBI = [4, 1, 6, 3, 0, 5, 2, 7, 9, 14, 15, 8, 13, 10, 11, 12, 18, 19, 20, 17, 22, 23, 16, 21, 31, 28, 25, 26, 27, 24, 29, 30, 36, 33, 38, 35, 32, 37, 34, 39, 41, 46, 47, 40, 45, 42, 43, 44, 50, 51, 52, 49, 54, 55, 48, 53, 63, 60, 57, 58, 59, 56, 61, 62, 68, 65, 70, 67, 64, 69, 66, 71, 73, 78, 79, 72, 77, 74, 75, 76, 82, 83, 84, 81, 86, 87, 80, 85, 95, 92, 89, 90, 91, 88, 93, 94, 100, 97, 102, 99, 96, 101, 98, 103, 105, 110, 111, 104, 109, 106, 107, 108, 114, 115, 116, 113, 118, 119, 112, 117, 127, 124, 121, 122, 123, 120, 125, 126]
    assert input >= 0x00000000000000000000000000000000
    assert input <= 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF 
    output = 0
    for i in range(128):
        bit_value = (input >> (127-PBI[i])) & 0b1
        output |= bit_value << (127-i)
    return output

def permbits_inv(input: int):
    PBI_INV = [4, 1, 6, 3, 0, 5, 2, 7, 11, 8, 13, 14, 15, 12, 9, 10, 22, 19, 16, 17, 18, 23, 20, 21, 29, 26, 27, 28, 25, 30, 31, 24, 36, 33, 38, 35, 32, 37, 34, 39, 43, 40, 45, 46, 47, 44, 41, 42, 54, 51, 48, 49, 50, 55, 52, 53, 61, 58, 59, 60, 57, 62, 63, 56, 68, 65, 70, 67, 64, 69, 66, 71, 75, 72, 77, 78, 79, 76, 73, 74, 86, 83, 80, 81, 82, 87, 84, 85, 93, 90, 91, 92, 89, 94, 95, 88, 100, 97, 102, 99, 96, 101, 98, 103, 107, 104, 109, 110, 111, 108, 105, 106, 118, 115, 112, 113, 114, 119, 116, 117, 125, 122, 123, 124, 121, 126, 127, 120]
    assert input >= 0x00000000000000000000000000000000
    assert input <= 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF 
    output = 0
    for i in range(128):
        bit_value = (input >> (127-PBI_INV[i])) & 0b1
        output |= bit_value << (127-i)
    return output

def perm_bytes(input: int, round: int):
    PI = [[7, 0, 13, 10, 5, 2, 15, 8, 4, 3, 14, 9, 6, 1, 12, 11],
          [13, 0, 10, 7, 11, 6, 12, 1, 2, 15, 5, 8, 4, 9, 3, 14],
          [7, 13, 10, 0, 6, 12, 11, 1, 5, 15, 8, 2, 4, 14, 9, 3],
          [13, 8, 6, 3, 14, 11, 5, 0, 12, 9, 7, 2, 15, 10, 4, 1]]
    assert input >= 0x00000000000000000000000000000000
    assert input <= 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    as_bytes = bytearray(input.to_bytes(16, byteorder='big'))
    result = bytearray(16)
    for i in range(16):
        result[i] = as_bytes[PI[round][i]]
    return int.from_bytes(result, 'big')


def perm_bytes_inv(input:int, round: int):
    PI_INV = [[1, 13, 5, 9, 8, 4, 12, 0, 7, 11, 3, 15, 14, 2, 10, 6],
              [1, 7, 8, 14, 12, 10, 5, 3, 11, 13, 2, 4, 6, 0, 15, 9],
              [3, 7, 11, 15, 12, 8, 4, 0, 10, 14, 2, 6, 5, 1, 13, 9],
              [7, 15, 11, 3, 14, 6, 2, 10, 1, 9, 13, 5, 8, 0, 4, 12]]
    assert input >= 0x00000000000000000000000000000000
    assert input <= 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    as_bytes = bytearray(input.to_bytes(16, byteorder='big'))
    result = bytearray(16)
    for i in range(16):
        result[i] = as_bytes[PI_INV[round][i]]
    return int.from_bytes(result, 'big')

def matrix_mul(input: int):
    assert input >= 0x00000000000000000000000000000000
    assert input <= 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    as_bytes = input.to_bytes(16, byteorder='big')
    result = bytearray(16)
    for i in range(4):
        for j in range(4):
            result[4*i+j] = as_bytes[4*i+(j+1)%4] ^ as_bytes[4*i+(j+2)%4] ^ as_bytes[4*i+(j+3)%4]
    return int.from_bytes(result, 'big')


def main(
        number_of_rounds:int, 
        backwards:bool = False, 
        threads:int = 16, 
        opt_f:bool = False,
        opt_b:bool = False,
        job_name:str = "current",
        start:int = 0,
        capacity:int = 480):

    assert opt_f != opt_b
    con = sqlite3.connect(f"{number_of_rounds}_round_differentials_{"b" if backwards else "f"}{"_p" if opt_f else ""}.db", autocommit=True)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS state (key text unique, value int);")
    cur.execute(f"INSERT OR IGNORE INTO state (key) VALUES ('{job_name}');")
    cur.execute("CREATE TABLE IF NOT EXISTS probabilities(i INTEGER PRIMARY KEY, input_diff text unique, round0 int, round1 int, round2 int, round3 int);")


    work_items = [value << place*4 for value in range(1,16) for place in range(32)][start:start+capacity]
    cur.execute(f"SELECT value from state where key = '{job_name}';")
    row = cur.fetchone()
    # print(row)
    # print(start)
    # print(start+capacity)
    cache = row[0]-1 if row[0] else 0
    if cache > len(work_items):
        cache = 0

    for idx, current_item in tqdm(enumerate(work_items[cache:])):
        print(idx)
        cur.execute(f"UPDATE state SET value = {cache + idx} where key = '{job_name}';")
        for first_round in tqdm(range(4), leave=False):
            if opt_f and not opt_b:
                input_diff = permbits_inv(current_item)
            elif opt_b and not opt_f:
                input_diff = matrix_mul(perm_bytes(permbits_inv(current_item), (3-first_round)%4))
            else:
                input_diff = current_item
            cur.execute(f"INSERT OR IGNORE INTO probabilities (input_diff) VALUES ('0x{input_diff:032x}');")
            prob = find_maximum_differentials_for_input_diff(input_diff, first_round, number_of_rounds, backwards, threads)
            cur.execute(f"UPDATE probabilities SET round{first_round} = {prob} WHERE input_diff = '0x{input_diff:032x}';")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Find_maximum_differentials"
    )
    parser.add_argument("number_of_rounds", type=int)
    parser.add_argument("--backwards", "-b", action='store_true')
    parser.add_argument("--threads", "-t", type=int, default=1)
    parser.add_argument("--optimized_forward", "-of", action='store_true')
    parser.add_argument("--optimized_backward", "-ob", action='store_true')
    parser.add_argument("--job_name", type=str)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--capacity", type=int, default=480)
    args = parser.parse_args()
    main(args.number_of_rounds, args.backwards, args.threads, args.optimized_forward, args.optimized_backward, args.job_name, args.start, args.capacity)
