from locust import HttpLocust, TaskSet, task, events

import time, csv

# Environment Variables
import EV

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
		LocustCounter.increment()


def on_request_completion(request_type, name, response_time, response_length = 0, exception = ""):
	results = [LocustCounter.get(), request_type, name, response_time, response_length, exception]

	# Append the data to the results file.
	with open("results.csv", "a") as results_file:
		writer = csv.writer(results_file)
		writer.writerow(results)


# Required for running a locust test.  Defines the user properites.
class WebsiteUser(HttpLocust):
	task_set = UserBehavior

	min_wait = 400
	max_wait = 400

	events.request_success += on_request_completion
	events.request_failure += on_request_completion

	# Write the header of the results file.
	with open("results.csv", "w+") as results_file:
		writer = csv.writer(results_file)
		writer.writerow(["Users", "Request Type", "Name", "Response Time", "Length", "Exception"])

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