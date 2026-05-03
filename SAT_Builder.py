import subprocess
import re

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
            
                self.clauses.append(Clause(variables=[
                    -self.label_to_variable[y],
                    self.label_to_variable[x]
                ],xor=True))
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
            
                self.clauses.append(Clause(variables=[
                    -self.label_to_variable[y],
                    self.label_to_variable[x]
                ],xor=True))
                self.clauses.append(Clause(variables=[
                    self.label_to_variable[y],
                    -self.label_to_variable[x]
                ],xor=True))

        self.current_state = [f"x_{self.current_state_number}_{i}" for i in range(0, 128)]
        
    def add_subcell(self):
        PBI_INV = [7, 2, 5, 0, 3, 6, 1, 4, 15, 10, 13, 8, 11, 14, 9, 12, 23, 18, 21, 16, 19, 22, 17, 20, 31, 26, 29, 24, 27, 30, 25, 28, 36, 35, 34, 37, 32, 39, 38, 33, 44, 43, 42, 45, 40, 47, 46, 41, 52, 51, 50, 53, 48, 55, 54, 49, 60, 59, 58, 61, 56, 63, 62, 57, 69, 64, 71, 70, 65, 68, 67, 66, 77, 72, 79, 78, 73, 76, 75, 74, 85, 80, 87, 86, 81, 84, 83, 82, 93, 88, 95, 94, 89, 92, 91, 90, 102, 101, 96, 99, 98, 97, 100, 103, 110, 109, 104, 107, 106, 105, 108, 111, 118, 117, 112, 115, 114, 113, 116, 119, 126, 125, 120, 123, 122, 121, 124, 127]        
        PBI = [7, 2, 5, 0, 3, 6, 1, 4, 15, 10, 13, 8, 11, 14, 9, 12, 23, 18, 21, 16, 19, 22, 17, 20, 31, 26, 29, 24, 27, 30, 25, 28, 34, 33, 36, 39, 38, 37, 32, 35, 42, 41, 44, 47, 46, 45, 40, 43, 50, 49, 52, 55, 54, 53, 48, 51, 58, 57, 60, 63, 62, 61, 56, 59, 69, 68, 71, 66, 65, 64, 67, 70, 77, 76, 79, 74, 73, 72, 75, 78, 85, 84, 87, 82, 81, 80, 83, 86, 93, 92, 95, 90, 89, 88, 91, 94, 96, 103, 102, 97, 100, 99, 98, 101, 104, 111, 110, 105, 108, 107, 106, 109, 112, 119, 118, 113, 116, 115, 114, 117, 120, 127, 126, 121, 124, 123, 122, 125]

        #Forward Bit-Permutation
        self.new_state()
        for i in range(0, 128):
            y = f"x_{self.current_state_number}_{i}"
            x = f"x_{self.current_state_number-1}_{PBI[i]}"
            self.clauses.append(Clause(variables=[
                    -self.label_to_variable[y],
                    self.label_to_variable[x]
                ],xor=True))
            self.clauses.append(Clause(variables=[
                    self.label_to_variable[y],
                    -self.label_to_variable[x]
                ],xor=True))

        self.current_state = [f"x_{self.current_state_number}_{i}" for i in range(0, 128)]

        # ToDo: SBox
        # m=32 sboxes in parallel

        #Backward Bit-Permutation
        self.new_state()
        for i in range(0, 128):
            y = f"x_{self.current_state_number}_{i}"
            x = f"x_{self.current_state_number-1}_{PBI_INV[i]}"
            self.clauses.append(Clause(variables=[
                    -self.label_to_variable[y],
                    self.label_to_variable[x]
                ],xor=True))
            self.clauses.append(Clause(variables=[
                    self.label_to_variable[y],
                    -self.label_to_variable[x]
                ],xor=True))

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
                self.clauses.append(Clause(variables=[
                    -self.label_to_variable[y_0],
                    self.label_to_variable[x_1],
                    self.label_to_variable[x_2],
                    self.label_to_variable[x_3],
                ], xor=True))

                # Row = 1
                self.clauses.append(Clause(variables=[
                    self.label_to_variable[y_1],
                    -self.label_to_variable[x_0],
                    self.label_to_variable[x_2],
                    self.label_to_variable[x_3],
                ], xor=True))
                self.clauses.append(Clause(variables=[
                    -self.label_to_variable[y_1],
                    self.label_to_variable[x_0],
                    self.label_to_variable[x_2],
                    self.label_to_variable[x_3],
                ], xor=True))

                # Row = 2
                self.clauses.append(Clause(variables=[
                    self.label_to_variable[y_2],
                    -self.label_to_variable[x_0],
                    self.label_to_variable[x_1],
                    self.label_to_variable[x_3],
                ], xor=True))
                self.clauses.append(Clause(variables=[
                    -self.label_to_variable[y_2],
                    self.label_to_variable[x_0],
                    self.label_to_variable[x_1],
                    self.label_to_variable[x_3],
                ], xor=True))

                # Row = 3
                self.clauses.append(Clause(variables=[
                    self.label_to_variable[y_3],
                    -self.label_to_variable[x_0],
                    self.label_to_variable[x_1],
                    self.label_to_variable[x_2],
                ], xor=True))
                self.clauses.append(Clause(variables=[
                    -self.label_to_variable[y_3],
                    self.label_to_variable[x_0],
                    self.label_to_variable[x_1],
                    self.label_to_variable[x_2],
                ], xor=True))

                
        
        self.current_state = [f"x_{self.current_state_number}_{i}" for i in range(0, 128)]

    def add_sbox(self):
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
                


