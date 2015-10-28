import simpy
import math
from enum import Enum

class Connection:
	InterruptReason = Enum("InterruptReason", "speed_modified closed")

	def __init__(self, sim, origin, destination, speed, requested):
		self.sim = sim
		self.origin = origin
		self.destination = destination
		self.speed = speed
		self.requested = requested

	def begin(self):
		self.action = self.sim.env.process(self.start_transfer())

	def start_transfer(self):
		time = self.time_to_transfer(len(self.requested))
		ended = False
		transfered_count = 0
		last_modified = self.sim.env.now

		while not ended: 
			try:
				yield self.sim.env.timeout(time)
				print("Transfer complete from host %d" % self.origin.id, end="")
				print(" to host %d" % self.destination.id, end="")
				print(" at %f" % self.sim.env.now)
				ended = True
			except simpy.Interrupt as inter:
				print("Transfer interrupted from host %d" % self.origin.id, end="")
				print(" to host %d" % self.destination.id, end="")
				print(" at %f" % self.sim.env.now, end="")
				print(" (reason: %s)" % str(inter.cause["reason"]))
				
				if inter.cause["reason"] == Connection.InterruptReason.speed_modified:
					elapsed = self.sim.env.now - last_modified
					transfered_count += math.floor((elapsed * self.speed * 1024**2) / self.sim.mtu)
					last_modified = self.sim.env.now
					self.speed = inter.cause["new_speed"]
					time = self.time_to_transfer(len(self.requested) - transfered_count)
				else:
					raise NotImplementedError()

		self.destination.download_finished(self)
		self.origin.upload_finished(self)
		self.sim.connection_ended(self)

	def time_to_transfer(self, packet_count):
		return float(packet_count * self.sim.mtu) / (self.speed * 1024**2)