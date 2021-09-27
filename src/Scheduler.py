import multiprocessing

class Scheduler(multiprocessing.Process):
	def __init__(self, app_release, r_schedule, scheduler_free, request_queue, apps, **kwargs):
		super().__init__()
		self.C = kwargs['C'] #page requests
		self.r_schedule = r_schedule #queue
		self.scheduler_free = scheduler_free
		self.request_queue = request_queue #queue
		self.app_release = app_release
		self.ready_apps = apps #list

		self.display()		
		self.start()	

	def run(self):
		while True:
			call = self.r_schedule.get()
			if call == -1: 		
				self.app_release.acquire()
				print('scheduler is running round robin as scheduling algorithm')
				self.ready_apps[0][1].acquire()
				popped = self.ready_apps.pop(0) #pop the app which is ready
				self.ready_apps.append(popped) #append the poped app to queue
				self.ready_apps[0][1].release()
				self.scheduler_free.release()
				self.app_release.release()
			else: #release app
				app_id = call
				for i,app in enumerate(self.ready_apps):
					if app[0] == app_id:
						app[1].acquire()
						self.ready_apps.pop(i)
				if len(self.ready_apps) == 0:
					print('All jobs are completed')
					self.request_queue.put(-2)
					print('Scheduler stoped')
					break
				else:
					self.ready_apps[0][1].release()

	def schedule_one(self):
		if len(self.ready_apps) != 0:
			self.ready_apps[0][1].release()
			print('First app ',self.ready_apps[0][0],'scheduled')
		else:
			print('No process or apps are there to schedule')
			pass

	def admit_app(self, app_id, app_lock):
		self.ready_apps.append((app_id,app_lock))

	def display(self):
		print(' Scheduler details(C):',self.C)
		pass
