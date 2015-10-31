from host import Host
from connection import Connection
import utils
import math

class Server(Host):
	def __init__(self, sim, down_mbps, up_mbps):
		super().__init__(sim, down_mbps, up_mbps)

	def upload_finished(self, con):
		print("server acknowledges upload finished")
		self.uploads.remove(con)

		if not self.uploads:
			return

		"""
		After an upload has ended, try to speed up other uploads using the newly available
		upload bandwidth.  For each downloader, check that it has spare download space
		to increase the transfer speed.  Distribute the spare upload bandwidth between each
		client.  If the client has no spare download bandwidth, 0 will be added to the transfer
		speed.
		"""
		total_grow_space = math.fsum(c.destination.avail_download_space() for c in self.uploads)
		avail_upload_space = self.avail_upload_space()

		if total_grow_space <= avail_upload_space:
			print("grow with original spaces")
			grow_sizes = [c.destination.avail_download_space() for c in self.uploads]
		else:
			print("grow with proportion to avail_upload_space")
			grow_sizes = [(c.destination.avail_download_space() / total_grow_space) * avail_upload_space for c in self.uploads]

		for upload, grow_size in zip(self.uploads, grow_sizes):
			if grow_size <= 0:
				continue
			print("SERVER:   " + str(grow_size) + "   " + str(upload.destination.avail_download_space()) + "   " + str(upload.destination.id))
			info = {
				"reason": Connection.InterruptReason.speed_modified,
				"new_speed": upload.speed + grow_size # grow_size can be 0
			}
			upload.interrupt(info)
		self.upload_check_event.succeed()

	def download_finished(self, c, completed, transfered):
		raise Exception("Invalid Simulation state: server downloading files.")

	def external_transfer_finished(self, c):
		pass

	def upload_to(self, other, other_mbps, indices):
		"""
		Transfer pieces from self to other
		"""
		if not self.uploads:
			# print("SERVER: No active uploads, assigning min bw.")
			speed = min(self.up_mbps, other_mbps)
		else:
			if other_mbps <= self.avail_upload_space():
				# print("SERVER: Remaining space enough for client dl speed.")
				speed = other_mbps
			else:
				# print("SERVER: Rebalancing server upload speeds for new client.")
				speed = self.create_upload_space(other_mbps)
				assert(speed <= other_mbps)

		c = Connection(self.sim, self, other, speed, indices)
		self.uploads.append(c)

		return c

	def should_use_torrent(self):
		return self.avail_upload_space() < (1 - self.sim.torrent_threshold) * self.up_mbps

	def create_upload_space(self, speed):
		"""
		Shrink all active uploads proportionately in order to create an upload
		space of bandwidth "speed".  Returns the newly available bandwidth size to
		use with a new connection.  Returned value can be smaller or equal to "speed".

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
			upload.interrupt(info)
		self.upload_check_event.succeed()
		return final_speeds[-1]