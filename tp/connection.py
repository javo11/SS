import math
import simpy

def capacity_for(mbps, latency, mtu):
	"""
	mbps: megabytes per second
	latency: miliseconds
	mtu: bytes
	"""
	val = (float(latency) * ((mbps * (1024**2)) / 1000)) / mtu
	return math.floor(val)

class Connection:
	def __init__(self, env, origin, destination, capacity, requested, latency):
		self.env = env
		self.origin = origin
		self.destination = destination
		self.capacity = capacity
		self.store = simpy.resources.store.Store(env, capacity)
		self.requested = requested
		self.latency = latency