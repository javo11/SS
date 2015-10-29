import itertools

class IntegerSet:
	"""
	Represents a set of integers.  Can be iterated over, in 
	ascending order.
	"""

	__slots__ = ["_ranges"]

	def __init__(self, r = None):
		self._ranges = [r] if r and len(r) > 0 else []

	def add_num(self, n):
		self.add_range(range(n, n + 1))

	def add_range(self, r):
		if len(r) == 0 or self.contains_range(r):
			return

		self._removed_contained_by(r)
		merge_left = None
		merge_right = None
		insertion_point = None

		for i, elem in enumerate(self._ranges):
			if elem[-1] + 1 < r[0]:
				insertion_point = i
			elif elem[0] <= r[0] <= elem[-1] + 1:
				merge_left = i
				if insertion_point is None:
					insertion_point = i - 1
			elif r[-1] + 1 >= elem[0]:
				merge_right = i
				break

		if insertion_point is None:
			self._ranges.insert(0, r)
		else:
			start = self._ranges[merge_left][0] if merge_left is not None else r[0]
			end = self._ranges[merge_right][-1] + 1 if merge_right is not None else r[-1] + 1
			new_r = range(start, end)

			del_offset = 0
			if merge_left is not None:
				del self._ranges[merge_left]
				del_offset = 1
			if merge_right is not None:
				del self._ranges[merge_right - del_offset]

			self._ranges.insert(insertion_point + 1, new_r)

	def __str__(self):
		s = "[ "
		for i in itertools.chain.from_iterable(self._ranges):
			s += str(i) + " "
		return s + "]"

	def __iter__(self):
		return itertools.chain.from_iterable(self._ranges)

	def __len__(self):
		return sum(len(elem) for elem in self._ranges)

	def contains_num(self, n):
		return self.contains_range(range(n, n + 1))

	def contains_range(self, r):
		if len(r) == 0:
			return True
		for elem in self._ranges:
			if self._range_contains(elem, r):
				return True

		return False

	def _removed_contained_by(self, r):
		self._ranges = [elem for elem in self._ranges if not self._range_contains(r, elem)]

	def _range_contains(self, a, b):
		"""
		Returns true iff a contains b
		"""
		return b[0] >= a[0] and b[-1] <= a[-1]