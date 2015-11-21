from host import Host
from connection import Connection
import utils
import math

class Server(Host):
	def __init__(self, sim, down_mbps, up_mbps):
		super().__init__(sim, down_mbps, up_mbps)

	def upload_finished(self, con):
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

		if total_grow_space <= 0:
			return

		if total_grow_space <= avail_upload_space:
			grow_sizes = [c.destination.avail_download_space() for c in self.uploads]
		else:
			grow_sizes = [(c.destination.avail_download_space() / total_grow_space) * avail_upload_space for c in self.uploads]

		self.update_upload_speeds(grow_sizes, True)

	def update_upload_speeds(self, speeds, additive):
		if len(self.uploads) != len(speeds):
			raise Exception("Invalid speeds length, must match self.uploads")

		factor = 1 if additive else 0
		s = 0
		for upload, speed in zip(self.uploads, speeds):
			s += 1
			skip = additive and utils.isclose(0, speed)
			skip |= not additive and utils.isclose(speed, upload.speed)
			if skip:
				continue

			new_speed = (upload.speed * factor) + speed
		
			upload.interrupt((Connection.SPEED_MODIFIED, new_speed))

		# if not self.upload_check_event.triggered:
		# 	self.upload_check_event.succeed()

	def download_finished(self, c, completed, transfered):
		raise Exception("Invalid Simulation state: server downloading files.")

	def external_transfer_finished(self, c):
		pass

	def upload_to(self, other, other_mbps, indices):
		"""
		Transfer pieces from self to other
		"""
		if not self.can_use_http():
			raise Exception("HTTP downloads are not enabled")

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

	def can_use_torrent(self):
		return self.avail_upload_space() < (1 - self.sim.torrent_threshold) * self.up_mbps

	def can_use_http(self):
		if not self.uploads:
			return True
		per_cl_up = self.up_mbps / len(self.uploads)
		return per_cl_up > (self.sim.client_down_mu * self.sim.http_down_threshold)

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
		client_speed = final_speeds.pop()
		self.update_upload_speeds(final_speeds, False)

		return client_speed