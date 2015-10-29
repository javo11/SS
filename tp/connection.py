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
		self.action = None

	def begin(self):
		self.action = self.sim.env.process(self.start_transfer())

	def interrupt(self, info):
		if not self.action:
			raise Exception("Unable to interrupt uninitialized connection.")
		self.action.interrupt(cause=info)

	def start_transfer(self):
		time = self.time_to_transfer(len(self.requested))
		ended = False
		completed = False
		transfered_count = 0
		last_modified = self.sim.env.now

		while not ended:
			try:
				yield self.sim.env.timeout(time)
				print("Transfer complete from host %d" % self.origin.id, end="")
				print(" to host %d" % self.destination.id, end="")
				print(" at %f" % self.sim.env.now)
				ended = True
				completed = True
			except simpy.Interrupt as inter:
				print("Transfer interrupted from host %d" % self.origin.id, end="")
				print(" to host %d" % self.destination.id, end="")
				print(" at %f" % self.sim.env.now, end="")
				print(" (reason: %s)" % str(inter.cause["reason"]))

				self.destination.bandwidth_check_down()
				elapsed = self.sim.env.now - last_modified
				transfered_count += math.floor((elapsed * self.speed * 1024**2) / self.sim.mtu)

				if inter.cause["reason"] == Connection.InterruptReason.speed_modified:
					last_modified = self.sim.env.now
					self.speed = inter.cause["new_speed"]

					time = self.time_to_transfer(len(self.requested) - transfered_count)
				else:
					ended = True
					completed = False

				if inter.cause.get("is_last"):
					print("IS LAST")
					self.origin.bandwidth_check_up()

		transfered_count = len(self.requested) if completed else transfered_count

		self.destination.download_finished(self)
		self.origin.upload_finished(self)
		self.sim.connection_ended(self)

	def time_to_transfer(self, packet_count):
		return float(packet_count * self.sim.mtu) / (self.speed * 1024**2)