from host import Host
from connection import Connection

class Server(Host):
	def __init__(self, sim, down_mbps, up_mbps):
		super().__init__(sim, down_mbps, up_mbps)

	def upload_finished(self, c):
		print("server acknowledges upload finished")
		self.uploads.remove(c)

	def download_finished(self, c):
		raise Exception("Invalid Simulation state: server downloading files.")

	def upload_to(self, other, other_mbps, indices):
		"""
		Transfer pieces from self to other
		"""
		if not self.uploads:
			print("SERVER: No active uploads, assigning min bw.")
			speed = min(self.up_mbps, other_mbps)
		else:
			used_upload = sum(c.speed for c in self.uploads)
			remaining_upload = self.up_mbps - used_upload
			if other_mbps <= remaining_upload:
				print("SERVER: Remaining space enough for client dl speed.")
				speed = other_mbps
			else:
				print("SERVER: Rebalancing client upload speeds for new client.")
				speed = self.create_upload_space(other_mbps)

		c = Connection(self.sim, self, other, speed, indices)
		self.uploads.append(c)
		return c

	def create_upload_space(self, speed):
		"""
		TODO: Change so that new speed is limited to a certain value.
			  This is to avoid allocating too much space for a new connection.
		"""
		all_speeds = [c.speed for c in self.uploads]
		all_speeds.append(speed)
		speeds_sum = sum(all_speeds)
		final_speeds = [(s / speeds_sum) * self.up_mbps for s in all_speeds]
		for upload, new_speed in zip(self.uploads, final_speeds[:-1]):
			info = { 
				"reason": Connection.InterruptReason.speed_modified,
				"new_speed": new_speed
			}
			upload.action.interrupt(cause=info)
		return final_speeds[-1]