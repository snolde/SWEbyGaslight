import random

class Problem:
	def __init__(self):
		"""Init random 4-bit nibble (0-15)"""
		self.val = random.randint(0, 15)
		#self.val=15
		self.turns = 0
	
	def move(self, mask, callback):
		"""Update masked bits of val with callback
		function"""
		if mask.bit_count() == 2:
			self.turns += 1

			print(f"\nMove {self.turns:2}: \
				{mask:04b} {self.val:04b} ->", end=' ')
		
			# Callback and update
			self.val = (self.val & ~mask) | (mask & \
						callback(mask, self.val & mask))
		else:
			print(f"Illegal move! Select 2 bits.")
		
		print(f"{self.val:04b}")
		# Random roll (0-3 positions)
		r = random.randint(0, 3)
		self.val = ((self.val << r) | (self.val >> (4 - \
						r))) & 0xF
		
		# Check win condition
		if self.val == 0 or self.val == 0xF:
			print(f"\n✓ SOLVED: {self.turns} turns!")
			return self.turns
		
		return 0