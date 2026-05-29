import subprocess
import re
import itertools

class Clause:
    def __init__(self, variables=None, xor=False):
        self.variables = [] if variables is None else list(variables)
        self.xor = xor

    def append(self, variable:int):
        self.variables.append(variable)

    def __str__(self):
        string = ""
        if self.xor:
            string += "(x "
        else:
            string += "( "

        for variable in self.variables:
            string += f"{variable} "
        
        string += ")"
        return string
    
    def __repr__(self):
        return str(self)

class SAT_Builder:
    def __init__(self, start_value:int):
        """
        start_value: int Big Endian representation
        """
        self.next_variable = 1
        self.label_to_variable = {}
        self.variable_to_label = {}
        self.clauses: list(Clause) = []
        self.current_state = []
        self.current_state_number = 0
        self.round_number = 0
        self.auxilary_variables = []
        self.start_state(start_value)
        

    def add_variable(self, label:str):
        if label in self.label_to_variable:
            raise ValueError(f"Label {label} is already in use")

        self.label_to_variable[label] = self.next_variable
        self.variable_to_label[self.next_variable] = label
        self.next_variable += 1

    def start_state(self, value: int):

        assert value >= 0x00000000000000000000000000000000
        assert value <= 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

        value_bits = [(value >> i) & 1 for i in range(127, -1, -1)] # Working with in BigEndian

        if value == 0: # if no input diff is given
            clause = Clause()
            for i in range(128):
                label = f"x_{self.current_state_number}_{i}"
                self.add_variable(label)
                self.current_state.append(label)
                clause.append(self.label_to_variable[label])
            self.clauses.append(clause)

        else:
            for i in range(0, 128):
                label = f"x_{self.current_state_number}_{i}"
                self.add_variable(label)
                self.current_state.append(label)

                clause = Clause()
                match(value_bits[i]):
                    case 0:
                        clause.append(-self.label_to_variable[label])
                    case 1:
                        clause.append(self.label_to_variable[label])
                self.clauses.append(clause)
            
        assert len(self.current_state) == 128

    def to_cnf(self, filename: str):
        with open(f"{filename}", "w") as file:
            for clause in self.clauses:
                if clause.xor:
                    file.write("x")
                for variable in clause.variables:
                    file.write(f"{variable} ")
                file.write("0\n")
                
    def new_state(self):
        self.current_state_number += 1
        for i in range(0, 128):
            label = f"x_{self.current_state_number}_{i}"
            self.add_variable(label)
            self.current_state.append(label)

    def print_clause(self, clause:Clause):
        print_string = ""
        if clause.xor:
            print_string += "x"
        print_string += "( "
        
        for var in clause.variables:
            if var < 0:
                print_string += "¬"
            print_string += f"{self.variable_to_label[abs(var)]} "
        

        print_string += ")"
        print(print_string)

    def add_round(self, r:int):
        self.add_subcell()
        self.add_permutation(r)
        self.add_matrix_mul()

    def add_round_inv(self, r:int):
        self.add_matrix_mul()
        self.add_permutation_rev(r)
        self.add_subcell()

    def add_permutation(self, r:int):
        PI = [
            [7, 0, 13, 10, 5, 2, 15, 8, 4, 3, 14, 9, 6, 1, 12, 11],
            [13, 0, 10, 7, 11, 6, 12, 1, 2, 15, 5, 8, 4, 9, 3, 14],
            [7, 13, 10, 0, 6, 12, 11, 1, 5, 15, 8, 2, 4, 14, 9, 3],
            [13, 8, 6, 3, 14, 11, 5, 0, 12, 9, 7, 2, 15, 10, 4, 1],
        ]

        self.new_state()

        for i in range(0, 16):
            for j in range(0, 8):
                y = f"x_{self.current_state_number}_{(i*8)+j}"
                x = f"x_{self.current_state_number - 1}_{(PI[r][i] * 8)+j}"
            
                # self.clauses.append(Clause(variables=[
                #     -self.label_to_variable[y],
                #     self.label_to_variable[x]
                # ],xor=True))
                self.clauses.append(Clause(variables=[
                    self.label_to_variable[y],
                    -self.label_to_variable[x]
                ],xor=True))

        self.current_state = [f"x_{self.current_state_number}_{i}" for i in range(0, 128)] 
        
    def add_permutation_rev(self, r:int):
        PI_INV = [
            [1, 13, 5, 9, 8, 4, 12, 0, 7, 11, 3, 15, 14, 2, 10, 6],
            [1, 7, 8, 14, 12, 10, 5, 3, 11, 13, 2, 4, 6, 0, 15, 9],
            [3, 7, 11, 15, 12, 8, 4, 0, 10, 14, 2, 6, 5, 1, 13, 9],
            [7, 15, 11, 3, 14, 6, 2, 10, 1, 9, 13, 5, 8, 0, 4, 12],
        ]

        self.new_state()

        for i in range(0, 16):
            for j in range(0, 8):
                y = f"x_{self.current_state_number}_{(i*8)+j}"
                x = f"x_{self.current_state_number - 1}_{(PI_INV[r][i] * 8)+j}"
            
                # self.clauses.append(Clause(variables=[
                #     -self.label_to_variable[y],
                #     self.label_to_variable[x]
                # ],xor=True))
                self.clauses.append(Clause(variables=[
                    self.label_to_variable[y],
                    -self.label_to_variable[x]
                ],xor=True))

        self.current_state = [f"x_{self.current_state_number}_{i}" for i in range(0, 128)]
        
    def add_subcell(self):
        # PBI = [7, 2, 5, 0, 3, 6, 1, 4, 15, 10, 13, 8, 11, 14, 9, 12, 23, 18, 21, 16, 19, 22, 17, 20, 31, 26, 29, 24, 27, 30, 25, 28, 36, 35, 34, 37, 32, 39, 38, 33, 44, 43, 42, 45, 40, 47, 46, 41, 52, 51, 50, 53, 48, 55, 54, 49, 60, 59, 58, 61, 56, 63, 62, 57, 69, 64, 71, 70, 65, 68, 67, 66, 77, 72, 79, 78, 73, 76, 75, 74, 85, 80, 87, 86, 81, 84, 83, 82, 93, 88, 95, 94, 89, 92, 91, 90, 102, 101, 96, 99, 98, 97, 100, 103, 110, 109, 104, 107, 106, 105, 108, 111, 118, 117, 112, 115, 114, 113, 116, 119, 126, 125, 120, 123, 122, 121, 124, 127]        
        PBI = [4, 1, 6, 3, 0, 5, 2, 7, 9, 14, 15, 8, 13, 10, 11, 12, 18, 19, 20, 17, 22, 23, 16, 21, 31, 28, 25, 26, 27, 24, 29, 30, 36, 33, 38, 35, 32, 37, 34, 39, 41, 46, 47, 40, 45, 42, 43, 44, 50, 51, 52, 49, 54, 55, 48, 53, 63, 60, 57, 58, 59, 56, 61, 62, 68, 65, 70, 67, 64, 69, 66, 71, 73, 78, 79, 72, 77, 74, 75, 76, 82, 83, 84, 81, 86, 87, 80, 85, 95, 92, 89, 90, 91, 88, 93, 94, 100, 97, 102, 99, 96, 101, 98, 103, 105, 110, 111, 104, 109, 106, 107, 108, 114, 115, 116, 113, 118, 119, 112, 117, 127, 124, 121, 122, 123, 120, 125, 126]
        PBI_INV = [4, 1, 6, 3, 0, 5, 2, 7, 11, 8, 13, 14, 15, 12, 9, 10, 22, 19, 16, 17, 18, 23, 20, 21, 29, 26, 27, 28, 25, 30, 31, 24, 36, 33, 38, 35, 32, 37, 34, 39, 43, 40, 45, 46, 47, 44, 41, 42, 54, 51, 48, 49, 50, 55, 52, 53, 61, 58, 59, 60, 57, 62, 63, 56, 68, 65, 70, 67, 64, 69, 66, 71, 75, 72, 77, 78, 79, 76, 73, 74, 86, 83, 80, 81, 82, 87, 84, 85, 93, 90, 91, 92, 89, 94, 95, 88, 100, 97, 102, 99, 96, 101, 98, 103, 107, 104, 109, 110, 111, 108, 105, 106, 118, 115, 112, 113, 114, 119, 116, 117, 125, 122, 123, 124, 121, 126, 127, 120]
        #Forward Bit-Permutation
        self.new_state()
        for i in range(0, 128):
            y = f"x_{self.current_state_number}_{i}"
            x = f"x_{self.current_state_number-1}_{PBI[i]}"
            self.clauses.append(Clause(variables=[
                    -self.label_to_variable[y],
                    self.label_to_variable[x]
                ],xor=True))
            # self.clauses.append(Clause(variables=[
            #         self.label_to_variable[y],
            #         -self.label_to_variable[x]
            #     ],xor=True))

        self.current_state = [f"x_{self.current_state_number}_{i}" for i in range(0, 128)]

        self._add_sbox()

        #Backward Bit-Permutation
        self.new_state()
        for i in range(0, 128):
            y = f"x_{self.current_state_number}_{i}"
            x = f"x_{self.current_state_number-1}_{PBI_INV[i]}"
            self.clauses.append(Clause(variables=[
                    -self.label_to_variable[y],
                    self.label_to_variable[x]
                ],xor=True))
            # self.clauses.append(Clause(variables=[
            #         self.label_to_variable[y],
            #         -self.label_to_variable[x]
            #     ],xor=True))

        self.current_state = [f"x_{self.current_state_number}_{i}" for i in range(0, 128)]

    def add_matrix_mul(self):
        self.new_state()

        for col in range(4):
            for i in range(8):
                y_0 = f"x_{self.current_state_number}_{(4*col)*8 + i}"
                y_1 = f"x_{self.current_state_number}_{(4*col + 1)*8 + i}"
                y_2 = f"x_{self.current_state_number}_{(4*col + 2)*8 + i}"
                y_3 = f"x_{self.current_state_number}_{(4*col + 3)*8 + i}"

                x_0 = f"x_{self.current_state_number -1}_{(4*col)*8 + i}"
                x_1 = f"x_{self.current_state_number -1}_{(4*col + 1)*8 + i}"
                x_2 = f"x_{self.current_state_number -1}_{(4*col + 2)*8 + i}"
                x_3 = f"x_{self.current_state_number -1}_{(4*col + 3)*8 + i}"

                # Row = 0
                self.clauses.append(Clause(variables=[
                    self.label_to_variable[y_0],
                    -self.label_to_variable[x_1],
                    self.label_to_variable[x_2],
                    self.label_to_variable[x_3],
                ], xor=True))
                # self.clauses.append(Clause(variables=[
                #     -self.label_to_variable[y_0],
                #     self.label_to_variable[x_1],
                #     self.label_to_variable[x_2],
                #     self.label_to_variable[x_3],
                # ], xor=True))

                # Row = 1
                self.clauses.append(Clause(variables=[
                    self.label_to_variable[y_1],
                    -self.label_to_variable[x_0],
                    self.label_to_variable[x_2],
                    self.label_to_variable[x_3],
                ], xor=True))
                # self.clauses.append(Clause(variables=[
                #     -self.label_to_variable[y_1],
                #     self.label_to_variable[x_0],
                #     self.label_to_variable[x_2],
                #     self.label_to_variable[x_3],
                # ], xor=True))

                # Row = 2
                self.clauses.append(Clause(variables=[
                    self.label_to_variable[y_2],
                    -self.label_to_variable[x_0],
                    self.label_to_variable[x_1],
                    self.label_to_variable[x_3],
                ], xor=True))
                # self.clauses.append(Clause(variables=[
                #     -self.label_to_variable[y_2],
                #     self.label_to_variable[x_0],
                #     self.label_to_variable[x_1],
                #     self.label_to_variable[x_3],
                # ], xor=True))

                # Row = 3
                self.clauses.append(Clause(variables=[
                    self.label_to_variable[y_3],
                    -self.label_to_variable[x_0],
                    self.label_to_variable[x_1],
                    self.label_to_variable[x_2],
                ], xor=True))
                # self.clauses.append(Clause(variables=[
                #     -self.label_to_variable[y_3],
                #     self.label_to_variable[x_0],
                #     self.label_to_variable[x_1],
                #     self.label_to_variable[x_2],
                # ], xor=True))

                
        
        self.current_state = [f"x_{self.current_state_number}_{i}" for i in range(0, 128)]

    def _add_sbox(self):
        DDT = [
            [16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 2, 4, 0, 2, 2, 2, 0, 2, 0, 0, 0, 0, 0, 2, 0],
            [0, 4, 0, 0, 4, 0, 0, 0, 0, 4, 0, 0, 4, 0, 0, 0],
            [0, 0, 0, 0, 2, 0, 4, 2, 2, 2, 0, 0, 0, 2, 0, 2],
            [0, 2, 4, 2, 2, 2, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0],
            [0, 2, 0, 0, 2, 0, 0, 4, 0, 2, 4, 0, 2, 0, 0, 0],
            [0, 2, 0, 4, 0, 0, 0, 2, 2, 0, 0, 0, 2, 2, 0, 2],
            [0, 0, 0, 2, 0, 4, 2, 0, 0, 0, 0, 2, 0, 4, 2, 0],
            [0, 2, 0, 2, 2, 0, 2, 0, 0, 2, 0, 2, 2, 0, 2, 0],
            [0, 0, 4, 2, 0, 2, 0, 0, 2, 2, 0, 2, 2, 0, 0, 0],
            [0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 4, 0, 0, 4, 0, 4],
            [0, 0, 0, 0, 2, 0, 0, 2, 2, 2, 0, 4, 0, 2, 0, 2],
            [0, 0, 4, 0, 0, 2, 2, 0, 2, 2, 0, 0, 2, 0, 2, 0],
            [0, 0, 0, 2, 0, 0, 2, 4, 0, 0, 4, 2, 0, 0, 2, 0],
            [0, 2, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 2, 2, 4, 2],
            [0, 0, 0, 2, 0, 0, 2, 0, 0, 0, 4, 2, 0, 0, 2, 4],
        ]

        self.new_state()
        for m in range(0, 32):
            for i in range(3):
                self.add_variable(f"p_{self.current_state_number}_{m}_{i}")
            for input_diff in range(16):
                input_bits = [(input_diff >> i) & 1 for i in range(3, -1, -1)]
                for output_diff in range(16):
                    output_bits = [(output_diff >> i) & 1 for i in range(3, -1, -1)]
                    DDT_count = DDT[input_diff][output_diff]
                    match(DDT_count):
                        case 0:
                            clause = Clause()
                            for i in range(4):
                                match(input_bits[i]):
                                    case 0:
                                        clause.append(self.label_to_variable[f"x_{self.current_state_number - 1}_{4*m + i}"])
                                    case 1:
                                        clause.append(-self.label_to_variable[f"x_{self.current_state_number - 1}_{4*m + i}"])

                            for i in range(4):
                                match(output_bits[i]):
                                    case 0:
                                        clause.append(self.label_to_variable[f"x_{self.current_state_number}_{4*m + i}"])
                                    case 1:
                                        clause.append(-self.label_to_variable[f"x_{self.current_state_number}_{4*m + i}"])
                            
                            self.clauses.append(clause)
                        
                        case 2:
                            for p in range(pow(2, 3)):
                                clause = Clause()
                                p_bits = [(p >> i) & 1 for i in range(3)]
                                if p_bits == [1, 1, 1]:
                                    continue
                                
                                for i in range(4):
                                    match(input_bits[i]):
                                        case 0:
                                            clause.append(self.label_to_variable[f"x_{self.current_state_number - 1}_{4*m + i}"])
                                        case 1:
                                            clause.append(-self.label_to_variable[f"x_{self.current_state_number - 1}_{4*m + i}"])

                                for i in range(4):
                                    match(output_bits[i]):
                                        case 0:
                                            clause.append(self.label_to_variable[f"x_{self.current_state_number}_{4*m + i}"])
                                        case 1:
                                            clause.append(-self.label_to_variable[f"x_{self.current_state_number}_{4*m + i}"])

                                for i in range(3):
                                    match(p_bits[i]):
                                        case 0:
                                            clause.append(self.label_to_variable[f"p_{self.current_state_number}_{m}_{i}"])
                                        case 1:
                                            clause.append(-self.label_to_variable[f"p_{self.current_state_number}_{m}_{i}"])

                                self.clauses.append(clause)


                        case 4:
                            for p in range(pow(2, 3)):
                                clause = Clause()
                                p_bits = [(p >> i) & 1 for i in range(3)]
                                if p_bits == [0, 1, 1]:
                                    continue
                                
                                for i in range(4):
                                    match(input_bits[i]):
                                        case 0:
                                            clause.append(self.label_to_variable[f"x_{self.current_state_number - 1}_{4*m + i}"])
                                        case 1:
                                            clause.append(-self.label_to_variable[f"x_{self.current_state_number - 1}_{4*m + i}"])

                                for i in range(4):
                                    match(output_bits[i]):
                                        case 0:
                                            clause.append(self.label_to_variable[f"x_{self.current_state_number}_{4*m + i}"])
                                        case 1:
                                            clause.append(-self.label_to_variable[f"x_{self.current_state_number}_{4*m + i}"])

                                for i in range(3):
                                    match(p_bits[i]):
                                        case 0:
                                            clause.append(self.label_to_variable[f"p_{self.current_state_number}_{m}_{i}"])
                                        case 1:
                                            clause.append(-self.label_to_variable[f"p_{self.current_state_number}_{m}_{i}"])

                                self.clauses.append(clause)

                        case 16:
                            for p in range(pow(2, 3)):
                                clause = Clause()
                                p_bits = [(p >> i) & 1 for i in range(3)]
                                if p_bits == [0, 0, 0]:
                                    continue
                                
                                for i in range(4):
                                    match(input_bits[i]):
                                        case 0:
                                            clause.append(self.label_to_variable[f"x_{self.current_state_number - 1}_{4*m + i}"])
                                        case 1:
                                            clause.append(-self.label_to_variable[f"x_{self.current_state_number - 1}_{4*m + i}"])

                                for i in range(4):
                                    match(output_bits[i]):
                                        case 0:
                                            clause.append(self.label_to_variable[f"x_{self.current_state_number}_{4*m + i}"])
                                        case 1:
                                            clause.append(-self.label_to_variable[f"x_{self.current_state_number}_{4*m + i}"])

                                for i in range(3):
                                    match(p_bits[i]):
                                        case 0:
                                            clause.append(self.label_to_variable[f"p_{self.current_state_number}_{m}_{i}"])
                                        case 1:
                                            clause.append(-self.label_to_variable[f"p_{self.current_state_number}_{m}_{i}"])

                                self.clauses.append(clause)
                
        self.current_state = [f"x_{self.current_state_number}_{i}" for i in range(0, 128)]


    def add_probability_constraint(self, k_bound:int = 4):
        # my (x1, ... xn) I need to find all probability variables
        p_is = []
        for i in range(self.current_state_number + 1):
            if self.label_to_variable.get(f"p_{i}_0_0"):
                for m in range(32):
                    for p in range(3):
                        p_is.append(f"p_{i}_{m}_{p}")

        X = [self.label_to_variable[var] for var in p_is]

        # add auxilary variables
        S = []
        for x in range(len(p_is)-1):
            s_k = []
            for k in range(k_bound):
                variable = f"s_{self.current_state_number}_{x}_{k}"
                self.add_variable(variable)
                s_k.append(self.label_to_variable[variable])
            S.append(s_k)

        self.auxilary_variables += list(itertools.chain.from_iterable(S))

        self.clauses.append(Clause([-X[0], S[0][0]]))

        for j in range(1, k_bound):
            self.clauses.append(Clause([-S[0][j]]))

        for i in range(1, len(X)-1):
            self.clauses.append(Clause([-X[i], S[i][0]]))
            self.clauses.append(Clause([-S[i-1][1], S[i][1]]))
            for j in range(1, k_bound):
                self.clauses.append(Clause([-X[i], -S[i-1][j-1], S[i][j]]))
                self.clauses.append(Clause([-S[i-1][j], S[i][j]]))
            self.clauses.append(Clause([-X[i], -S[i][k_bound-1]]))
        
        self.clauses.append(Clause([-X[len(X)-1], -S[len(X)-2][k_bound-1]]))