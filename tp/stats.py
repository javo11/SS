import matplotlib.pyplot as plt

def setup_stats(sim):
	plt.ion()
	fig = plt.figure(figsize=(20,10))

	sim.clients_plot = fig.add_subplot(2, 2, 1)
	sim.connections_plot = fig.add_subplot(2, 2, 2)
	sim.comp_avg_plot = fig.add_subplot(2, 2, 3)
	sim.comp_count_plot = fig.add_subplot(2, 2, 4)

	sim.clients_hist = []
	sim.active_clients_hist = []
	sim.p2p_conn_hist = []
	sim.http_conn_hist = []
	sim.completion_avg_hist = []
	sim.completion_count_hist = []

def plot_stats(sim):
	plot_vs_time(sim, sim.clients_plot, sim.clients_hist)
	plot_vs_time(sim, sim.clients_plot, sim.active_clients_hist, False)
	plot_vs_time(sim, sim.connections_plot, sim.p2p_conn_hist)
	plot_vs_time(sim, sim.connections_plot, sim.http_conn_hist, False)
	# plot_vs_time(sim, sim.comp_avg_plot, sim.completion_avg_hist)

	sim.comp_avg_plot.clear()
	sim.comp_avg_plot.hist(sim.completion_times, bins=30, histtype='step')

	plot_vs_time(sim, sim.comp_count_plot, sim.completion_count_hist)

	sim.clients_plot.legend(["clients", "active clients"], loc=4, framealpha=0.7)
	sim.connections_plot.legend(["P2P", "HTTP"], loc=4, framealpha=0.7)
	sim.comp_avg_plot.legend(["download times (minutes)"], loc=4, framealpha=0.7)
	sim.comp_count_plot.legend(["completed clients"], loc=4, framealpha=0.7)
	plt.draw()

def plot_vs_time(sim, plot, data, clear=True):
	times = [v[0] for v in data]
	values = [v[1] for v in data]
	if clear:
		plot.clear()
	plot.plot(times, values)

def stats_end(sim):
	plt.show(block=True)