import itertools
import math

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

	def add_set(self, i_set):
		for r in i_set._ranges:
			self.add_range(r)

	def intersect(self, other):
		A = self.copy()
		A.add_set(other)
		
		q = A.copy()
		q.remove_set(other)

		r = other.copy()
		r.add_set(self)
		r.remove_set(self)
		
		A.remove_set(q)
		A.remove_set(r)
		return A

	def take(self, n):
		if n > len(self):
			raise Exception("Set contains less elements than requested amount")
		elif n == len(self):
			return self.copy()

		i_set = IntegerSet()
		for r in self._ranges:
			if n - len(r) >= 0:
				i_set.add_range(r)
				n-= len(r)
			else:
				i_set.add_range(range(r[0], r[0] + n))
				break

		return i_set

	def copy(self):
		i_set = IntegerSet()
		i_set._ranges = [r for r in self._ranges]

		return i_set

	def split(self, n):
		i_set = self.copy()
		size = math.floor(len(self)/n)
		parts = []

		if size <= 0:
			raise Exception("Unable to split in " + str(n) + " parts")

		for i in range(n - 1):
			set_part = i_set.take(size)
			i_set.remove_first(size)
			parts.append(set_part)

		size += len(self) % n
		set_part = i_set.take(size)
		i_set.remove_first(size)
		parts.append(set_part)

		return parts


	def remove_first(self, n):
		if (n > len(self)):
			raise Exception("Set contains less elements than requested amount")
		i = 0
		for i, r in enumerate(self._ranges):
			if n - len(r) > 0:
				n -= len(r)
			else:
				break

		self._ranges = self._ranges[i:]
		r = self._ranges[0]
		self._ranges[0] = range(n + r[0], r[-1] + 1)

	def add_range(self, r):
		if type(r) is not range:
			raise TypeError()

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

	def remove_set(self, other):
		for r in other._ranges:
			self.remove_range(r)

	def remove_range(self, target_r):
		self._removed_contained_by(target_r)
		left_range = None
		right_range = None
		for i, r in enumerate(self._ranges):  
			if r[0] > target_r[-1]:
				break

			if r[-1] < target_r[0]:
				continue
			
			if r[0] < target_r[0]:
				left_range = i
			else:
				right_range = i

		if left_range is not None:
			r = self._ranges[left_range]
			self._ranges[left_range] = range(r[0], target_r[0])
			if right_range is None:
				self.add_range(range(target_r[-1] + 1, r[-1] + 1))
			
		if right_range is not None:
			r = self._ranges[right_range]
			self._ranges[right_range] = range(target_r[-1] + 1, r[-1] + 1)

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