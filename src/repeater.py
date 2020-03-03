class Repeater:
	"""The Repeater class is a way to schedule tasks repeating a finite number of times or infinitelly.

	"""

	def __init__(self, scheduler):
		"""Constructor method for the Repeater class.

		:param scheduler: an initialized sched.scheduler to keep track of the time
		"""

		self.s = scheduler
		# To store the information about the to-be-executed tasks
		self.actions = []
		# Schedules a low-priority, infinitelly-running dummy task to keep the scheduler
		# from stopping execution when the queue is empty.
		self.add(lambda: 0, 1<<1, -1, priority=999)

	def add(self, action, delay, ttl, now=False, priority=1, *args):
		"""Adds a task to the queue of actions.

		:param action: the function to execute
		:param delay: the time to wait between each execution in seconds
		:param ttl: maximum number of executions, negative if infinite
		:param now: flag to immediatelly execute the action once. If True, does not count towads the maximum number of executions
		:param priority: tasks scheduled for the same time will be executed ordered by priority. A lower number represents a higher priority
		:param *args: arguments passed to the function to execute.
		"""
		if len(args) == 0:
			# No arguments
			dct = {"action": action, "delay": delay, "ttl": ttl, "priority": priority}
		else:
			# Argments present
			dct = {"action": action, "delay": delay, "ttl": ttl, "priority": priority, "args": args}

		# Execute if now == True
		if now == True:
			if "args" in dct:
				dct["action"](*dct["args"])
			else:
				dct["action"]()
				
		# Add the information about execution to the array
		self.actions.append(dct)
		# Schedule the execution
		self.s.enter(delay, priority, self._execute, argument=(dct,))
	
	def start(self):
		"""To start the execution of the scheduler.

		Since the timer of the delay starts when calling the method add(), it is advisable to first call start(), then add the tasks for greater precision
		"""
		self.s.run()

	
	def _execute(self, dct):
		"""Executes the task and takes care of the re-scheduling
		
		:param dct: the dictionary with all the information about the task to be executed
		"""
		# Execute the task
		if "args" in dct:
			# With arguments
			dct["action"](dct["args"])
		else:
			# Without arguments
			dct["action"]()

		if dct["ttl"] > 0:
			# Decrement ttl if positive
			dct["ttl"] -= 1
		if dct["ttl"] != 0:
			# If in this iteration ttl reached 0, delete it from the array
			self.actions.remove(dct)
		else:
			# Else, re-schedulet it
			self.s.enter(dct["delay"], dct["priority"], self._execute, argument=(dct,))