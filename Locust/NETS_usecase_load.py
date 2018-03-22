from locust import HttpLocust, TaskSet, task, events

import time, csv, threading, os

# Environment Variables
import EV

# Python 2 Compatibility
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = OSError

# Required for running a locust test.  Defines the actions that a user will take.
class UserBehavior(TaskSet):

	@task(1)
	def text_search(self):
		self.client.get("/search?text=%s" % next_item_in_cycle(EV.search_terms))

	@task(1)
	def reverse(self):
		self.client.get("/reverse?point.lat=%f&point.lon=%f" % next_item_in_cycle(EV.reverse_coords))

	@task(1)
	def autocomplete(self):
		self.client.get("/autocomplete?text=%s" % next_item_in_cycle(EV.autocomplete_terms))

	@task(1)
	def place(self):
		self.client.get("/place?ids=%s" % next_item_in_cycle(EV.gids))
		# ids not necessarily persistent

	@task(1)
	def structured(self):
		self.client.get("/search/structured?%s" % next_item_in_cycle(EV.structured_parameters))

	def on_start(self):
		self.id = LocustCounter.increment()


class Logger():

	def __init__(self, filename):
		self.result_queue = [[
			"Users",
			"Request Type",
			"Name",
			"Response Time",
			"Test Time",
			"Length",
			"Exception"
		]]
		self.filename = filename
		self.queue_write_length = 1000
		self.lock = threading.Lock()
		self.start_time = time.time()
		try:
			os.remove(filename)
		except FileNotFoundError:
			print("%s does not yet exist.  It will be created." % filename)

	def add(self, request_type, name, response_time, response_length = 0, exception = ""):
		self.result_queue += [[
			LocustCounter.get(),
			request_type,
			name,
			response_time,
			time.time() - self.start_time,
			response_length,
			exception
		]]
		if len(self.result_queue) >= self.queue_write_length and not self.lock.locked():
			with self.lock: self.write()

	def write(self):
		current_length = len(self.result_queue)
		data_to_write = self.result_queue[:current_length]
		# Append the data to the results file.
		with open(self.filename, "a", newline='') as results_file:
			writer = csv.writer(results_file)
			writer.writerows(data_to_write)

		print("Wrote %d entries to %s" % (current_length, self.filename))
		del self.result_queue[:current_length]



# Required for running a locust test.  Defines the user properites.
class WebsiteUser(HttpLocust):
	task_set = UserBehavior

	min_wait = 0
	max_wait = 0

	logger = Logger("results.csv")

	events.request_success += logger.add
	events.request_failure += logger.add



def next_item_in_cycle(l):
	item = l.pop()
	l.insert(0, item)
	return item

class LocustCounter:
	count = 0

	@staticmethod
	def increment():
		LocustCounter.count += 1

	@staticmethod
	def get():
		return LocustCounter.count