"""
Tests to check if IntegerSet is working correctly
"""

from integer_set import IntegerSet

s = IntegerSet()
s.add_range(range(30, 40))
s.add_range(range(0, 20))
s.add_range(range(20, 21))
s.add_range(range(80, 82))
s.add_range(range(0, 20))
s.add_range(range(0, 20))
s.add_range(range(3, 11))
s.add_range(range(80, 85))
s.add_range(range(40, 81))
s.add_range(range(0, 100))
s.add_range(range(150, 151))
print(s)


t = IntegerSet(range(20, 25))
t.add_range(range(19, 19))
t.add_range(range(19, 20))
t.add_range(range(16, 20))
t.add_range(range(30, 31))
t.add_range(range(100000, 100002))
t.add_range(range(1))

print("------")
print(t)

q = IntegerSet(range(10))
q.add_range(range(5))
q.add_range(range(15))
q.add_range(range(20, 22))

print("------")
print(q)

for i in q:
	print(i)

b = IntegerSet(range(10))
assert(b.contains_range(range(4)))
assert(b.contains_range(range(10)))
b.add_range(range(10, 11))
assert(b.contains_range(range(11)))
print("OK")

print(len(b))

i_set = IntegerSet(range(10))
i_set.add_range(range (20, 30))
i_set2 = IntegerSet(range(10, 20))
i_set.add_set(i_set2)
print(i_set)

i_set = IntegerSet(range(4))
i_set.add_range(range(10, 13))
i_set.add_range(range(20, 23))
print(i_set.take(8))