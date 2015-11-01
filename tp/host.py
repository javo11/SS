from integer_set import IntegerSet
import math
import utils

class Host:
	ID_COUNTER = 0

	def __init__(self, sim, down_mbps, up_mbps):
		self.sim = sim
		self.down_mbps = down_mbps
		self.up_mbps = up_mbps
		self.id = self.ID_COUNTER
		Host.ID_COUNTER += 1
		self.uploads = []
		self.downloads = []
		self.pieces = IntegerSet()
		self.upload_check_event = sim.env.event()
		self.sim.env.process(self.upload_check_process())

	def upload_to(self, other, other_mbps, indices):
		raise NotImplementedError()

	def upload_finished(self, c):
		raise NotImplementedError()

	def download_finished(self, c, completed, transfered):
		raise NotImplementedError()

	def external_transfer_finished(self, c):
		raise NotImplementedError()

	def connection_ended(self, c):
		if not (c.origin == self or c.destination == self):
			self.external_transfer_finished(c)

	def upload_check_process(self):
		while True:
			yield self.upload_check_event
			self.upload_check_event = self.sim.env.event()
			self.bandwidth_check_up()

	def avail_upload_space(self):
		used_upload = math.fsum(c.speed for c in self.uploads)
		return self.up_mbps - used_upload

	def has_upload_space(self):
		return self.avail_upload_space() > 0

	def bandwidth_check_up(self):
		used_upload = math.fsum(c.speed for c in self.uploads)
		cond = used_upload <= self.up_mbps or utils.isclose(used_upload, self.up_mbps)
		assert cond, "Upload BW exceeded (host ID: %d, used: %f)" % (self.id, used_upload)

	def avail_download_space(self):
		used_download = math.fsum(c.speed for c in self.downloads)
		free = self.down_mbps - used_download
		return 0 if utils.isclose(0, free) else free

	def has_download_space(self):
		return self.avail_download_space() > 0

	def bandwidth_check_down(self):
		used_download = math.fsum(c.speed for c in self.downloads)
		cond = used_download <= self.down_mbps or utils.isclose(used_download, self.down_mbps)
		assert cond, "Download BW exceeded (host ID: %d, used: %f, original_mbps: %f)" % (self.id, used_download, self.down_mbps)
