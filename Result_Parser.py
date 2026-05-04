import re

# result = """v 1 -2 3 -4 5 -6 7 -8 -9 -10 -11 -12 -13 -14 -15 -16 -17 -18 -19 -20 -21 -22 -23 
#             v -24 -25 -26 -27 -28 -29 -30 -31 -32 -33 -34 -35 -36 -37 -38 -39 -40 41 -42 43 
#             v -44 45 -46 47 -48 -49 -50 -51 -52 -53 -54 -55 -56 -57 -58 -59 -60 -61 -62 -63 
#             v -64 -65 -66 -67 -68 -69 -70 -71 -72 -73 -74 -75 -76 -77 -78 -79 -80 81 -82 83 
#             v -84 85 -86 87 -88 -89 -90 -91 -92 -93 -94 -95 -96 -97 -98 -99 -100 -101 -102 
#             v -103 -104 -105 -106 -107 -108 -109 -110 -111 -112 -113 -114 -115 -116 -117 
#             v -118 -119 -120 121 -122 123 -124 125 -126 127 -128 -129 -130 -131 -132 -133 
#             v -134 -135 -136 137 -138 139 -140 141 -142 143 -144 145 -146 147 -148 149 -150 
#             v 151 -152 153 -154 155 -156 157 -158 159 -160 161 -162 163 -164 165 -166 167 
#             v -168 -169 -170 -171 -172 -173 -174 -175 -176 177 -178 179 -180 181 -182 183 
#             v -184 185 -186 187 -188 189 -190 191 -192 193 -194 195 -196 197 -198 199 -200 
#             v 201 -202 203 -204 205 -206 207 -208 -209 -210 -211 -212 -213 -214 -215 -216 
#             v 217 -218 219 -220 221 -222 223 -224 225 -226 227 -228 229 -230 231 -232 233 
#             v -234 235 -236 237 -238 239 -240 241 -242 243 -244 245 -246 247 -248 -249 -250 
#             v -251 -252 -253 -254 -255 -256 0
#         """

# nums = re.findall(r"-?\d+", result)
# print(nums)


class Result_Parser:
    def __init__(self, cryptominisat_output:str, label_to_variable:{}, variable_to_label:{}):
        self.label_to_variable = label_to_variable
        self.variable_to_label = variable_to_label
        self.results = cryptominisat_output

    def __init__(self, pycryptosat_solution: tuple, label_to_variable:{}, variable_to_label:{}):
        self.label_to_variable = label_to_variable
        self.variable_to_label = variable_to_label
        self.results = pycryptosat_solution

    def parse(self):
        if type(self.results) == str:
            self._parse_file()
        else:
            self._parse_tuple()

    def _parse_file(self):
        pass

    def _parse_tuple(self):
        num_states = 0
        while self.label_to_variable.get(f"x_{num_states}_0"):
            num_states += 1

        for state in range(num_states):
            state_bool = [self.results[self.label_to_variable[f"x_{state}_{i}"]] for i in range(128)]
            if self.label_to_variable.get(f"p_{state}_0_0"):
                prob = 0
                for m in range(32):
                    for p in range(3):
                        if self.results[self.label_to_variable[f"p_{state}_{m}_{p}"]] > 0:
                            prob += 1
                print(f"State {state}:", f"{be_bits_to_int(state_bool):032x}", "with probability:", prob)
            else:
                print(f"State {state}:", f"{be_bits_to_int(state_bool):032x}")

def be_bits_to_int(bits: list[bool]) -> int:
    n = 0
    for b in bits:
        n = (n << 1) | int(b)

    return n