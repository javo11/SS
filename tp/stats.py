import matplotlib.pyplot as plt

client_hist = []
cc = 0

def setup_stats(sim):
	plt.ion()
	fig = plt.figure()
	sim.plot = fig.add_subplot(1,1,1)

def update_stats(sim):
	global cc
	cc += 1
	interval = int(sim.stats_interval)
	elapsed = range(interval, int(sim.env.now) + interval, interval)
	client_hist.append(len(sim.clients))
	print("about to plot")
	assert len(elapsed) == len(client_hist)
	sim.plot.clear()
	sim.plot.plot(elapsed, client_hist)
	plt.draw()