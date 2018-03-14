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
		self.client.post("/search/structured")
		# Probably a POST?



# Required for running a locust test.  Defines the user properites.
class WebsiteUser(HttpLocust):
    task_set = UserBehavior

    # No need to send too many status requests.  Send one every 2 seconds.
    min_wait = 2000
    max_wait = 2000

def next_item_in_cycle(l):
	item = l.pop()
	l.insert(0, item)
	return item