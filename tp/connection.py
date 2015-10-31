import simpy
import math
from enum import Enum

class Connection:
	InterruptReason = Enum("InterruptReason", "speed_modified closed")

	def __init__(self, sim, origin, destination, speed, requested):
		if speed <= 0:
			raise Exception("speed cannot be zero")
		self.sim = sim
		self.origin = origin
		self.destination = destination
		self.speed = speed
		self.requested = requested
		self.action = None

	def begin(self):
		"""
		Connection start point.  It spawns the start_transfer process.
		Various Connections can be "running" at the same time.  Each
		instance of Connection should start the start_transfer only once, 
		and once it is finished, be discarded.
		"""
		self.action = self.sim.env.process(self.start_transfer())

	def interrupt(self, info):
		"""
		Interrupt the start_transfer process.  Usually, in order to change
		the transfer speed (mbps) or to end the tranfer prematurely.
		"""
		if not self.action:
			raise Exception("Unable to interrupt uninitialized connection.")
		self.action.interrupt(cause=info)

	def start_transfer(self):
		"""
		start_transfer process.  Initially, it ends after "time" seconds have elapsed,
		via the timeout event.  The timeout can be interrupted in order to cancel the 
		transfer or to modify the connection speed.
		"""
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
				# print("Transfer interrupted from host %d" % self.origin.id, end="")
				# print(" to host %d" % self.destination.id, end="")
				# print(" at %f" % self.sim.env.now, end="")
				# print(" (reason: %s)" % str(inter.cause["reason"]))

				self.destination.bandwidth_check_down()
				elapsed = self.sim.env.now - last_modified
				transfered_count += math.floor((elapsed * self.speed * 1024**2) / self.sim.mtu)

				if inter.cause["reason"] == Connection.InterruptReason.speed_modified:
					last_modified = self.sim.env.now
					print(str(inter.cause["new_speed"] - self.speed) + "   " + str(self.destination.avail_download_space()) + "   " + str(self.destination.id))
					self.speed = inter.cause["new_speed"]
					if self.speed <= 0:
						raise Exception("speed cannot be zero")

					"""
					Calculate time needed to end transfer using the new connection speed,
					taking into account already transfered pieces.
					"""
					time = self.time_to_transfer(len(self.requested) - transfered_count)
				else:
					print("CLOSED")
					ended = True
					completed = False

		transfered_count = len(self.requested) if completed else transfered_count

		# Invoke callbacks
		self.destination.download_finished(self, completed, transfered_count)
		self.origin.upload_finished(self)
		self.sim.connection_ended(self)

	def time_to_transfer(self, packet_count):
		return float(packet_count * self.sim.mtu) / (self.speed * 1024**2)