import matplotlib.pyplot as plt

def setup_stats(sim):
	plt.ion()
	fig = plt.figure(figsize=(20,10))

	sim.clients_plot = fig.add_subplot(2, 2, 1)
	sim.connections_plot = fig.add_subplot(2, 2, 2)
	sim.comp_avg_plot = fig.add_subplot(2, 2, 3)
	sim.comp_count_plot = fig.add_subplot(2, 2, 4)

	sim.clients_hist = []
	sim.p2p_conn_hist = []
	sim.http_conn_hist = []
	sim.completion_avg_hist = []
	sim.completion_count_hist = []

def update_stats(sim, draw):
	sim.clients_hist.append(len(sim.clients))
	sim.p2p_conn_hist.append(sim.p2p_conn_count)
	sim.http_conn_hist.append(sim.http_conn_count)
	sim.completion_avg_hist.append(sim.completion_time_avg)
	sim.completion_count_hist.append(sim.completed_clients)

	print("P2P connections: ", sim.p2p_conn_count)
	print("HTTP connections: ", sim.http_conn_count)
	print("Client count: ", len(sim.clients))
	
	if not draw:
		return

	plot_vs_time(sim, sim.clients_plot, sim.clients_hist)
	plot_vs_time(sim, sim.connections_plot, sim.p2p_conn_hist)
	plot_vs_time(sim, sim.connections_plot, sim.http_conn_hist, False)
	plot_vs_time(sim, sim.comp_avg_plot, sim.completion_avg_hist)
	plot_vs_time(sim, sim.comp_count_plot, sim.completion_count_hist)

	sim.clients_plot.legend(["clients"], loc=4, framealpha=0.7)
	sim.connections_plot.legend(["P2P", "HTTP"], loc=4, framealpha=0.7)
	sim.comp_avg_plot.legend(["avg. download time (minutes)"], loc=4, framealpha=0.7)
	sim.comp_count_plot.legend(["completed clients"], loc=4, framealpha=0.7)

	plt.draw()

def plot_vs_time(sim, plot, data, clear=True):
	interval = int(sim.stats_interval)
	elapsed = range(interval, int(sim.env.now) + interval, interval)
	assert len(elapsed) == len(data)
	if clear:
		plot.clear()
	plot.plot(elapsed, data)

def stats_end(sim):
	plt.show(block=True)