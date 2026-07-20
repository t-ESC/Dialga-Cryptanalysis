PBI = [
	[4, 1, 6, 3, 0, 5, 2, 7],
	[1, 6, 7, 0, 5, 2, 3, 4],
	[2, 3, 4, 1, 6, 7, 0, 5],
	[7, 4, 1, 2, 3, 0, 5, 6],
]
PBI_INV = [
	[4, 1, 6, 3, 0, 5, 2, 7], #symmetric to Pb0
	[3, 0, 5, 6, 7, 4, 1, 2],
	[6, 3, 0, 1, 2, 7, 4, 5],
	[5, 2, 3, 4, 1, 6, 7, 0],
]

state = [i for i in range(0, 128)]
new_state = []

for row in range(4):
	for col in range(4):
		index = 4*row + col
		for bit in range(8):
			bit_index = (4*row + col)*8 + bit
			new_bit = 7-PBI[row][bit]
			# new_state.append(new_bit)
			new_state.append((4*row + col)*8 + PBI_INV[col][bit])

# for i in range(0, 16):
# 	row = (i >> 2)
# 	for j in range(0, 8):
# 		new_state.append(PBI[row][j] + (i*8))


# print(state)
print(new_state)