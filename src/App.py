import multiprocessing, os, random
import Scheduler

#App - app name
#V 	 - total no of unique virtual pages
#N 	 - number of page requests made by the App
class App(multiprocessing.Process):
	def __init__(self, app_lock, app_release, r_schedule, scheduler_free, 
					request_queue, paging, **kwargs):
		super().__init__()
		self.app_lock = app_lock
		self.name = kwargs['App']
		self.V = kwargs['V']
		self.N = kwargs['N']

		self.request_count = 0

		self.r_schedule = r_schedule
		self.scheduler_free = scheduler_free
		self.request_queue = request_queue
		self.paging = paging
		self.app_release = app_release
		
		self.display()		
		self.start()

	def run(self):
		rel_the_app = False
		print('app',self.name,'started')
		while True:	
			self.app_lock.acquire()
			self.scheduler_free.release()		
			if self.request_count < self.N:
				self.generate_page_request()			
			else:				
				self.scheduler_free.acquire()				
				rel_the_app = True										
			self.app_lock.release()
			self.app_release.release()
			if rel_the_app:
				rel_the_app = False
				self.r_schedule.put(self.pid)
				print(' stopping app',self.name)
				break
			self.scheduler_free.acquire()
		print('app',self.name,'terminated')

	def generate_page_request(self):
		self.request_count += 1
		page = random.randint(0,self.V)
		print(' page',page,'requested; request count', self.request_count)
		with self.paging:			
			self.request_queue.put(page)
			self.paging.wait()
			print(' page',page,'recieved')

	def display(self):
		print('(App name, V, N):',self.name, self.V, self.N)
		pass
