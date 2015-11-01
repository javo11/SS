import math

def isclose(a, b, rel_tol=1e-09):
	"""
	math.isclose function from Python 3.5
	"""
	if a * b != 0 and math.copysign(1, a) * math.copysign(1, b) < 0:
		return False

	abs_a = math.fabs(a)
	abs_b = math.fabs(b)
	if abs_a < abs_b:
		if abs_a == 0:
			return abs_b < rel_tol
		return 1 - (abs_a / abs_b) < rel_tol
	else:
		if abs_b == 0:
			return abs_b < rel_tol
		return 1 - (abs_b / abs_a) < rel_tol
