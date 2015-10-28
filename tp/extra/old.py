import simpy

class Car:
	def __init__(self, env):
		self.env = env
		self.action = env.process(self.run())

	def run(self):
		while True:
			print("start parking at: " + str(self.env.now))
			charge_duration = 5
			try:
				yield self.env.process(self.charge(charge_duration))
			except simpy.Interrupt as inter:
				print("was interrupted")

			print("start driving at: " + str(self.env.now))
			trip_duration = 2
			yield self.env.timeout(trip_duration)

	def charge(self, duration):
		yield self.env.timeout(duration)

def driver(env, car):
	yield env.timeout(3)
	car.action.interrupt()

def main():
	env = simpy.Environment()
	car = Car(env)
	env.process(driver(env, car))
	env.run(until=15)

if __name__ == "__main__":
	main()